"""Registro esférico: acha a rotação que leva a costa ATUAL (Natural Earth) sobre os trechos paleo.

Os mapas paleo são a costa moderna girada por placa (polos de Euler). Achando a rotação de
cada placa a partir dos trechos que existem, a costa moderna girada mostra a forma que falta.
"""
from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

DATA = Path(__file__).resolve().parent.parent / "data"
NE_URL = "https://naciscdn.org/naturalearth/10m/physical/ne_10m_coastline.zip"
LAND_URL = "https://naciscdn.org/naturalearth/50m/physical/ne_50m_land.zip"
LAND_URL = "https://naciscdn.org/naturalearth/50m/physical/ne_50m_land.zip"
DEG = np.pi / 180


def ll2xyz(ll: np.ndarray) -> np.ndarray:
    lon, lat = ll[:, 0] * DEG, ll[:, 1] * DEG
    return np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def xyz2ll(p: np.ndarray) -> np.ndarray:
    return np.column_stack([np.arctan2(p[:, 1], p[:, 0]), np.arcsin(np.clip(p[:, 2], -1, 1))]) / DEG


def load_modern() -> list[np.ndarray]:
    """Linhas de costa atuais (lon, lat). Baixa o Natural Earth 10m na 1ª execução."""
    import geopandas as gpd
    shp = DATA / "ne_10m_coastline" / "ne_10m_coastline.shp"
    if not shp.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        raw = urllib.request.urlopen(NE_URL, timeout=120).read()
        zipfile.ZipFile(io.BytesIO(raw)).extractall(DATA / "ne_10m_coastline")
    lines = []
    for g in gpd.read_file(shp).geometry:
        for part in getattr(g, "geoms", [g]):
            lines.append(np.asarray(part.coords)[:, :2])
    return lines


def densify(line: np.ndarray, step: float) -> np.ndarray:
    seg = np.hypot(*np.diff(line, axis=0).T)
    out = [line[:1]]
    for a, b, s in zip(line[:-1], line[1:], seg):
        n = max(int(np.ceil(s / step)), 1)
        out.append(a + (b - a) * (np.arange(1, n + 1) / n)[:, None])
    return np.vstack(out)


def sample_line(line: np.ndarray, n: int) -> np.ndarray:
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(line, axis=0).T))]
    t = np.linspace(0, d[-1], n)
    return np.column_stack([np.interp(t, d, line[:, 0]), np.interp(t, d, line[:, 1])])


def kabsch(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    u, _, vt = np.linalg.svd(src.T @ dst)
    d = np.sign(np.linalg.det(u @ vt))
    return (u @ np.diag([1, 1, d]) @ vt).T  # R tal que dst ≈ src @ R.T


class Modern:
    def __init__(self, coarse=0.25, fine=0.04):
        self.lines = load_modern()
        pts = [densify(l, fine) for l in self.lines]
        self.dense = pts
        self.xyz = [ll2xyz(p) for p in pts]
        allp = np.vstack(self.xyz)
        self.tree = cKDTree(allp)
        coarse_ll = np.vstack([densify(l, coarse) for l in self.lines])
        self.coarse_tree = cKDTree(ll2xyz(coarse_ll))

    def search(self, ll_pts: np.ndarray, n_rot=3_000_000, max_deg=75, keep=12, cap=0.03, seed=0):
        """Busca aleatória em SO(3) (ângulo <= max_deg) + refino ICP. Devolve [(score, R)]."""
        X = ll2xyz(ll_pts)
        rng = np.random.default_rng(seed)
        rots = Rotation.random(n_rot, random_state=rng)
        rots = rots[rots.magnitude() <= max_deg * DEG]
        mats = rots.as_matrix()
        scores = np.empty(len(mats))
        for i in range(0, len(mats), 20000):
            Y = np.einsum("rij,nj->rni", mats[i:i + 20000], X)
            d, _ = self.coarse_tree.query(Y.reshape(-1, 3), workers=-1)
            scores[i:i + 20000] = np.minimum(d, cap).reshape(len(Y), -1).mean(1)
        best = np.argsort(scores)[:keep * 20]
        out = []
        for j in best:
            R = self.icp(X, mats[j])
            out.append((self.score(X, R), R))
        out.sort(key=lambda t: t[0])
        uniq = []
        for s, R in out:  # remove quase-duplicatas
            if all(np.linalg.norm(Rotation.from_matrix(R @ U.T).as_rotvec()) > 0.02 for _, U in uniq):
                uniq.append((s, R))
        return uniq[:keep]

    def fit_lines(self, lines, view, min_len=1.0, chunk_deg=12.0, good=0.0025, good_short=0.0012,
                  max_searches=40, min_plate_deg=25.0):
        """Ajusta uma rotação a cada TRECHO (<= chunk_deg) dos traços paleo; busca novas placas só se preciso.

        Trechos, e não linhas inteiras: uma linha longa pode juntar placas com rotações diferentes.
        """
        lo_lon, hi_lon, lo_lat, hi_lat = view
        length = lambda x: float(np.hypot(*np.diff(x, axis=0).T).sum())
        pieces = []
        for l in lines:
            arc = np.r_[0, np.cumsum(np.hypot(*np.diff(l, axis=0).T))]
            n = max(int(np.ceil(arc[-1] / chunk_deg)), 1)
            cut = np.searchsorted(arc, np.linspace(0, arc[-1], n + 1))
            for a, b in zip(cut[:-1], cut[1:]):
                pieces.append((arc[-1], l[a:min(b + 1, len(l))]))
        pieces.sort(key=lambda p: -p[0])  # continentes primeiro: as buscas são caras e limitadas
        inview = [c for _, c in pieces if len(c) > 2 and length(c) >= min_len and c[:, 0].max() > lo_lon
                  and c[:, 0].min() < hi_lon and c[:, 1].max() > lo_lat and c[:, 1].min() < hi_lat]
        pts = [ll2xyz(sample_line(c, min(160, max(30, int(length(c) * 3))))) for c in inview]
        lens = [length(c) for c in inview]
        thr = lambda k: good if lens[k] >= 6 else good_short
        rots, assign, searches = [], {}, 0
        for k, c in enumerate(inview):
            if k in assign:
                continue
            if lens[k] < 8 or searches >= max_searches:
                continue
            searches += 1
            best = self.search(sample_line(c, 100), n_rot=800_000, keep=1)
            if not best or best[0][0] >= good:
                continue
            R = best[0][1]
            for _ in range(2):  # refina com todos os trechos que a rotação explica
                fits = [j for j in range(len(inview)) if j not in assign and self.score(pts[j], R) < thr(j)]
                R = self.icp(np.vstack([pts[j] for j in fits]), R, iters=10) if fits else R
            fits = [j for j in range(len(inview)) if j not in assign and self.score(pts[j], R) < thr(j)]
            if sum(lens[j] for j in fits) < min_plate_deg:  # placa sem peso = casamento por acaso
                continue
            rots.append(R)
            assign.update({j: len(rots) - 1 for j in fits})
        return inview, rots, self.reassign(inview, rots, good, good_short)

    def reassign(self, inview, rots, good=0.0025, good_short=0.0012):
        """Cada trecho fica com a rotação de MELHOR encaixe (margens conjugadas, como Brasil x África,
        têm forma quase igual e casam com rotações erradas se valer a primeira que servir)."""
        length = lambda x: float(np.hypot(*np.diff(x, axis=0).T).sum())
        assign = {}
        for j, c in enumerate(inview):
            X = ll2xyz(sample_line(c, min(160, max(30, int(length(c) * 3)))))
            sc = [self.score(X, R) for R in rots]
            k = int(np.argmin(sc))
            if sc[k] < (good if length(c) >= 6 else good_short):
                assign[j] = k
        return assign

    def complete(self, inview, rots, assign, all_lines, view, cover_tol=0.0040, max_run_deg=25.0,
                 min_anchor_deg=0.4, min_run_deg=0.3, sample_min_deg=6.0, min_size_deg=0.0):
        """Costa final = costa atual girada (trechos que encaixam + falhas entre eles) + sobras do paleo.

        Devolve (linhas, trechos): cada trecho longo (>= sample_min_deg, confiável) vem com o índice da
        placa (seg, k); serve para separar terra de mar (ver landmask.py).
        """
        lo_lon, hi_lon, lo_lat, hi_lat = view
        new_lines, runs = [], []
        for k, R in enumerate(rots):
            mine = [inview[i] for i, a in assign.items() if a == k]
            if not mine:
                continue
            cover = cKDTree(ll2xyz(np.vstack([densify(l, 0.04) for l in mine])))
            for chain, ll0 in zip(self.xyz, self.dense):
                P = chain @ R
                ll = xyz2ll(P)
                inw = (ll[:, 0] > lo_lon) & (ll[:, 0] < hi_lon) & (ll[:, 1] > lo_lat) & (ll[:, 1] < hi_lat)
                if not inw.any():
                    continue
                cov = cover.query(P, workers=-1)[0] < cover_tol
                if cov.sum() < 15:
                    continue
                arc = np.r_[0, np.cumsum(np.hypot(*np.diff(ll, axis=0).T))]
                keep = cov.copy()
                edges = np.flatnonzero(np.diff(np.r_[0, (~cov).astype(int), 0]))
                for a, b in zip(edges[::2], edges[1::2]):  # trechos sem cobertura [a, b)
                    if a == 0 or b >= len(cov) or arc[b - 1] - arc[a] > max_run_deg:
                        continue
                    la = a - 1
                    while la > 0 and cov[la - 1]:
                        la -= 1
                    rb = b
                    while rb < len(cov) - 1 and cov[rb + 1]:
                        rb += 1
                    if arc[a - 1] - arc[la] >= min_anchor_deg and arc[rb] - arc[b] >= min_anchor_deg:
                        keep[a:b] = True
                keep &= inw
                keep[np.r_[False, np.abs(np.diff(ll[:, 0])) > 5]] = False  # quebra na linha de data
                edges = np.flatnonzero(np.diff(np.r_[0, keep.astype(int), 0]))
                for a, b in zip(edges[::2], edges[1::2]):
                    seg = ll[a:b]
                    if len(seg) > 2 and arc[b - 1] - arc[a] >= min_run_deg and np.ptp(seg, axis=0).max() >= min_size_deg:
                        new_lines.append(seg)
                        if arc[b - 1] - arc[a] >= sample_min_deg:  # trechos curtos podem ter casado errado
                            runs.append((seg, k))
        return self._add_leftovers(new_lines, all_lines), runs

    def _add_leftovers(self, new_lines, all_lines, tol=0.0045, min_pts=12, min_size_deg=0.0):
        """Mantém partes do paleo que a costa atual não explica (lagos, feições que só existem no paleo)."""
        if not new_lines:
            return list(all_lines)
        tree = cKDTree(ll2xyz(np.vstack([densify(l, 0.04) for l in new_lines])))
        out = list(new_lines)
        for l in all_lines:
            dl = densify(l, 0.04)
            far = tree.query(ll2xyz(dl), workers=-1)[0] > tol
            edges = np.flatnonzero(np.diff(np.r_[0, far.astype(int), 0]))
            for a, b in zip(edges[::2], edges[1::2]):
                if b - a >= min_pts and np.ptp(dl[a:b], axis=0).max() >= min_size_deg:
                    out.append(dl[a:b])
        return out

    def land(self):
        if not hasattr(self, "_land"):
            import geopandas as gpd
            shp = DATA / "ne_50m_land" / "ne_50m_land.shp"
            if not shp.exists():
                raw = urllib.request.urlopen(LAND_URL, timeout=120).read()
                zipfile.ZipFile(io.BytesIO(raw)).extractall(DATA / "ne_50m_land")
            self._land = gpd.read_file(shp).geometry.union_all()
        return self._land

    def score(self, X, R, cap=0.03):
        d, _ = self.tree.query(X @ R.T, workers=-1)
        return float(np.minimum(d, cap).mean())

    def icp(self, X, R, iters=25, trim=0.85):
        for _ in range(iters):
            Y = X @ R.T
            d, idx = self.tree.query(Y, workers=-1)
            keep = d <= np.quantile(d, trim)
            near = self.tree.data[idx]
            R = kabsch(X[keep], near[keep])
        return R
