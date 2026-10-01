"""Refinamento estético-científico de mapas paleoclimáticos exportados em PDF.

Lê o PDF "full" (raster de zonas + pontos/linhas vetoriais), extrai:
  * a grade de zonas climáticas (raster embutido) -> classes por desmistura de cor;
  * as amostras (círculos vetoriais) com a posição exata e a classe pela cor;
  * as linhas de costa (vetor) e o georreferenciamento (graticule do PDF).

Depois refina SÓ a forma das zonas (remove ruído/pontas via suavização de
probabilidade por classe), gera transições suaves e renderiza um mapa novo.
Pontos e linhas de costa nunca são movidos. Um relatório quantifica o quanto
as zonas mudaram em relação ao original (concordância, áreas, deslocamento).

Uso:
    python refine_paleomap.py <mapa_full.pdf> [--sigma 3] [--min-area 40] [--out <pasta>]
"""
from __future__ import annotations

import argparse
import json
import pickle
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pymupdf
from shapely.geometry import LineString
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path as MplPath

import coastline
import paleofit
import ripples
from scipy import ndimage as ndi

# Classes na ordem usada em todo o script
CLASSES = ("Árido", "Semiárido", "Úmido")
SRC_COLORS = np.array([(0.79, 0.69, 0.35), (0.36, 0.53, 0.31), (0.23, 0.46, 0.58)])
PALETTE = np.array([  # paleta refinada (areia, sálvia, azul-petróleo)
    (0.890, 0.745, 0.420),
    (0.522, 0.659, 0.447),
    (0.200, 0.435, 0.557),
])
POINT_COLORS = ["#E0A930", "#5E8F4A", "#1F5F82"]
BG = "#F5F2EA"
INK = "#2B3140"
OCEAN_TOP = (0.851, 0.894, 0.914)
OCEAN_BOTTOM = (0.765, 0.827, 0.863)
WAVE = "#F3F8FB"
COAST = "#243047"
UPSAMPLE = 4
FEATHER_DEG = 1.2


# ---------------------------------------------------------------- extração
@dataclass(frozen=True)
class Georef:
    ax: float  # lon = ax * x + bx
    bx: float
    ay: float  # lat = ay * y + by
    by: float

    def lon(self, x):
        return self.ax * np.asarray(x) + self.bx

    def lat(self, y):
        return self.ay * np.asarray(y) + self.by


def _deg(label: str) -> float:
    v = float(re.match(r"(\d+)", label).group(1))
    return -v if label.endswith(("S", "W")) else v


def fit_georef(page) -> Georef:
    """Casa as linhas do graticule (vetor) com os rótulos de grau do PDF."""
    xs, ys = [], []
    for d in page.get_drawings():
        if d["fill"] is not None or d["color"] is None or abs(d["color"][0] - 0.58) > 0.02:
            continue
        r = d["rect"]
        (xs if r.width < 1 else ys).append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)[r.width >= 1])
    words = {}
    for w in page.get_text("words"):
        if "°" in w[4]:
            words[(w[4], round(w[0]), round(w[1]))] = w
    lon_pts, lat_pts = [], []
    for (txt, _, _), w in words.items():
        cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
        if txt.endswith(("E", "W")) or (txt == "0°" and w[1] > 600):
            near = min(xs, key=lambda v: abs(v - cx))
            if abs(near - cx) < 6:
                lon_pts.append((near, _deg(txt)))
        else:
            near = min(ys, key=lambda v: abs(v - cy))
            if abs(near - cy) < 6:
                lat_pts.append((near, _deg(txt)))
    ax, bx = np.polyfit(*zip(*lon_pts), 1)
    ay, by = np.polyfit(*zip(*lat_pts), 1)
    return Georef(ax, bx, ay, by)


def _bezier(p0, p1, p2, p3, n=8):
    t = np.linspace(0, 1, n)[:, None]
    pts = [np.array([p.x, p.y]) for p in (p0, p1, p2, p3)]
    return ((1 - t) ** 3) * pts[0] + 3 * ((1 - t) ** 2) * t * pts[1] + 3 * (1 - t) * t**2 * pts[2] + t**3 * pts[3]


def extract_vectors(page, geo: Georef, legend_rect):
    samples, dots, coasts = [], [], []
    for d in page.get_drawings():
        r = d["rect"]
        if d["fill"] is not None and r.width < 10:
            if legend_rect.contains(r):
                continue
            cls = int(np.argmin(np.linalg.norm(SRC_COLORS - np.array(d["fill"]), axis=1)))
            rec = (float(geo.lon((r.x0 + r.x1) / 2)), float(geo.lat((r.y0 + r.y1) / 2)), cls)
            (samples if d["type"] == "fs" else dots).append(rec)
        elif d["fill"] is None and d["color"] and abs(d["color"][0] - 0.20) < 0.02:
            line, last = [], None
            for it in d["items"]:
                seg = np.array([[it[1].x, it[1].y], [it[2].x, it[2].y]]) if it[0] == "l" else (
                    _bezier(*it[1:5]) if it[0] == "c" else None)
                if seg is None:
                    continue
                if last is not None and np.hypot(*(seg[0] - last)) > 0.5:
                    coasts.append(np.array(line)); line = []
                line.extend(seg.tolist()); last = seg[-1]
            if line:
                coasts.append(np.array(line))
    coasts = [np.column_stack([geo.lon(c[:, 0]), geo.lat(c[:, 1])]) for c in coasts if len(c) > 1]
    return np.array(samples), np.array(dots), coasts


def extract_zone_raster(doc, page, geo: Georef):
    infos = sorted(page.get_image_info(xrefs=True), key=lambda i: -i["width"] * i["height"])
    zone = next(i for i in infos if i["bbox"][0] > 150)  # o maior fora da legenda
    legend = next((pymupdf.Rect(i["bbox"]) for i in infos if i is not zone), pymupdf.Rect())
    pix = pymupdf.Pixmap(doc, zone["xref"])
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3] / 255.0
    x0, y0, x1, y1 = zone["bbox"]
    extent = (float(geo.lon(x0)), float(geo.lon(x1)), float(geo.lat(y1)), float(geo.lat(y0)))
    return img, extent, legend


# ---------------------------------------------------------------- classificação
def unmix(img: np.ndarray, bg: np.ndarray):
    """pixel = a*classe + (1-a)*fundo -> devolve (classe, a). Lida com a borda esfumada."""
    v = img - bg
    best_res, labels, alpha = None, None, None
    for k, c in enumerate(SRC_COLORS):
        d = c - bg
        a = np.clip((v @ d) / (d @ d), 0, 1.2)
        res = np.linalg.norm(v - a[..., None] * d, axis=-1)
        if best_res is None:
            best_res, labels, alpha = res, np.zeros(res.shape, int), a
        else:
            m = res < best_res
            best_res = np.where(m, res, best_res); labels = np.where(m, k, labels); alpha = np.where(m, a, alpha)
    return labels, alpha


def classify(img, bg):
    """Classe por pixel. Pixels de transição (misturas) vão para a classe mais próxima."""
    lab, alpha = unmix(img, bg)
    valid = alpha > 0.55
    d = np.linalg.norm(img[..., None, :] - SRC_COLORS, axis=-1)
    lab = np.where(valid, np.argmin(d, axis=-1), -1)
    return lab, valid


def remove_speckles(lab, valid, min_area, protect_ij=None):
    """Remove manchas pequenas, exceto as que contêm uma amostra da mesma classe (são dado)."""
    out = lab.copy()
    for k in range(len(CLASSES)):
        cc, n = ndi.label(lab == k)
        if n == 0:
            continue
        sizes = ndi.sum(np.ones_like(cc), cc, index=np.arange(1, n + 1))
        small = set((np.flatnonzero(sizes < min_area) + 1).tolist())
        if protect_ij is not None:
            ii, jj, kk = protect_ij
            small -= set(cc[ii[kk == k], jj[kk == k]].tolist())
        out[np.isin(cc, list(small))] = -1
    holes = (out < 0) & valid
    idx = ndi.distance_transform_edt(out < 0, return_distances=False, return_indices=True)
    filled = out[tuple(idx)]
    return np.where(holes, filled, out)


def anchor_mask(lab, ij, max_area=400):
    """Manchas pequenas da grade original que contêm uma amostra da mesma classe."""
    ii, jj, kk = ij
    M = np.zeros((len(CLASSES),) + lab.shape, bool)
    for k in range(len(CLASSES)):
        cc, _ = ndi.label(lab == k)
        ids = set(cc[ii[kk == k], jj[kk == k]].tolist()) - {0}
        for i in ids:
            comp = cc == i
            if comp.sum() <= max_area:
                M[k] |= comp
    return M


def smooth_probs(lab, valid, sigma, anchors=None):
    idx = ndi.distance_transform_edt(~valid, return_distances=False, return_indices=True)
    lab_full = lab[tuple(idx)]  # estende a borda só para não criar artefato no filtro
    P = np.stack([ndi.gaussian_filter((lab_full == k).astype(float), sigma, mode="nearest")
                  for k in range(len(CLASSES))])
    if anchors is not None:  # núcleos ancorados em amostra não podem sumir na suavização
        for k in range(len(CLASSES)):
            P[k] = np.maximum(P[k], 1.5 * ndi.gaussian_filter(anchors[k].astype(float), sigma / 3))
    return P / P.sum(0, keepdims=True)


# ---------------------------------------------------------------- métricas
def pixel_class_at(lab, extent, lon, lat):
    h, w = lab.shape
    j = np.clip(((lon - extent[0]) / (extent[1] - extent[0]) * w).astype(int), 0, w - 1)
    i = np.clip(((extent[3] - lat) / (extent[3] - extent[2]) * h).astype(int), 0, h - 1)
    return lab[i, j]


def report(lab0, lab1, valid, extent, samples):
    deg_px = (extent[1] - extent[0]) / lab0.shape[1]
    agree = float((lab0 == lab1)[valid].mean())
    areas = {c: [float((lab0[valid] == k).mean()), float((lab1[valid] == k).mean())]
             for k, c in enumerate(CLASSES)}
    changed = (lab0 != lab1) & valid
    dist_max = 0.0
    for k in range(len(CLASSES)):
        m = changed & (lab1 == k)
        if m.any():  # distância de cada pixel alterado até a zona original daquela classe
            dist_max = max(dist_max, float(ndi.distance_transform_edt(lab0 != k)[m].max()))
    inside = [pixel_class_at(l, extent, samples[:, 0], samples[:, 1]) for l in (lab0, lab1)]
    in_dom = (samples[:, 0] >= extent[0]) & (samples[:, 0] <= extent[1])
    match = [float((c == samples[:, 2])[in_dom].mean()) for c in inside]
    return {
        "concordancia_pixels": round(agree, 4),
        "areas_original_vs_refinado": {k: [round(a, 4) for a in v] for k, v in areas.items()},
        "deslocamento_max_graus": round(dist_max * deg_px, 3),
        "grau_por_pixel": round(deg_px, 4),
        "amostras_coerentes_com_zona": {"original": round(match[0], 4), "refinado": round(match[1], 4)},
        "amostras_movidas": 0,
    }


# ---------------------------------------------------------------- render
def render_zones(P, softness, relief):
    Pu = np.stack([ndi.zoom(p, UPSAMPLE, order=3) for p in P]).clip(0, 1)
    W = np.exp(softness * Pu); W /= W.sum(0, keepdims=True)
    rgb = np.einsum("khw,kc->hwc", W, PALETTE)
    if relief > 0:  # sombreamento suave do campo "úmido - árido": só cosmético
        field = ndi.gaussian_filter(Pu[2] - Pu[0], 6 * UPSAMPLE)
        gy, gx = np.gradient(field)
        shade = (gx - gy) / (np.abs(gx - gy).max() + 1e-9)
        rgb = np.clip(rgb * (1 + relief * shade[..., None]), 0, 1)
    return Pu, rgb


def edge_alpha(shape, extent):
    h, w = shape
    fx = FEATHER_DEG / (extent[1] - extent[0]) * w
    fy = FEATHER_DEG / (extent[3] - extent[2]) * h
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum(np.minimum(xx / fx, (w - 1 - xx) / fx), np.minimum(yy / fy, (h - 1 - yy) / fy))
    return np.clip(d, 0, 1) ** 1.5


def draw_basemap(ax, view):
    """Oceano em degradê com grão de papel (a costa e as ondulações vêm por cima)."""
    x0, x1, y0, y1 = view
    h, w = 900, int(900 * (x1 - x0) / (y1 - y0))
    yy = np.linspace(0, 1, h)[:, None, None]
    ocean = (1 - yy) * np.array(OCEAN_TOP) + yy * np.array(OCEAN_BOTTOM)
    grain = ndi.gaussian_filter(np.random.default_rng(7).normal(0, 1, (h, w)), 1.2)[..., None]
    ocean = np.clip(np.broadcast_to(ocean, (h, w, 3)) * (1 + 0.025 * grain), 0, 1)
    ax.imshow(ocean, extent=view, origin="upper", interpolation="bicubic", zorder=0)


def draw_map(out_base, rgb, Pu, extent, samples, dots, coasts, waves, title, subtitle, rep):
    lon0, lon1, lat0, lat1 = extent
    pad = 1.5
    fig_w = 11
    fig_h = fig_w * (lat1 - lat0 + 2 * pad) / (lon1 - lon0 + 2 * pad) * 0.92 + 1.6
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=BG)
    ax = fig.add_axes([0.07, 0.13, 0.88, 0.77], facecolor=BG)
    ax.set_xlim(lon0 - pad, lon1 + pad); ax.set_ylim(lat0 - pad, lat1 + pad); ax.set_aspect("equal")

    view = (lon0 - pad, lon1 + pad, lat0 - pad, lat1 + pad)
    draw_basemap(ax, view)

    rgba = np.dstack([rgb, edge_alpha(rgb.shape[:2], extent)])
    ax.imshow(rgba, extent=extent, origin="upper", interpolation="bilinear", zorder=1)

    # contornos finos entre zonas (fronteira = classe dominante muda)
    lon = np.linspace(lon0, lon1, Pu.shape[2]); lat = np.linspace(lat1, lat0, Pu.shape[1])
    for k in range(len(CLASSES)):
        others = np.max(np.delete(Pu, k, axis=0), axis=0)
        ax.contour(lon, lat, Pu[k] - others, levels=[0], colors="white", linewidths=0.7, alpha=0.55, zorder=2)

    alpha_of = dict(zip(ripples.LEVELS_DEG, ripples.ALPHAS))
    for dist, w in waves:  # ondulações de água, só no lado do mar
        ax.plot(w[:, 0], w[:, 1], color=WAVE, lw=0.55, alpha=alpha_of[dist], solid_capstyle="round", zorder=2.6)
    for c in coasts:
        ax.plot(c[:, 0], c[:, 1], color=COAST, lw=0.55, alpha=0.95, solid_joinstyle="round",
                solid_capstyle="round", zorder=3)

    for v in range(-180, 181, 10):
        ax.axvline(v, color=INK, lw=0.3, alpha=0.18, ls=(0, (1, 3)), zorder=2.5)
    for v in range(-90, 91, 10):
        ax.axhline(v, color=INK, lw=0.6 if v == 0 else 0.3, alpha=0.35 if v == 0 else 0.18,
                   ls="-" if v == 0 else (0, (1, 3)), zorder=2.5)
    fmt = lambda v, p, n: f"{abs(int(v))}°{'' if v == 0 else (p if v > 0 else n)}"
    ax.set_xticks([v for v in range(-180, 181, 10) if lon0 - pad <= v <= lon1 + pad])
    ax.set_yticks([v for v in range(-90, 91, 10) if lat0 - pad <= v <= lat1 + pad])
    ax.set_xticklabels([fmt(v, "E", "W") for v in ax.get_xticks()])
    ax.set_yticklabels([fmt(v, "N", "S") for v in ax.get_yticks()])
    ax.tick_params(colors=INK, labelsize=8, length=0, pad=4)
    for s in ax.spines.values():
        s.set_color(INK); s.set_linewidth(0.6); s.set_alpha(0.5)

    for k in range(len(CLASSES)):
        d = dots[dots[:, 2] == k] if len(dots) else dots
        if len(d):
            ax.scatter(d[:, 0], d[:, 1], s=5, c=POINT_COLORS[k], lw=0.3, edgecolors="white", zorder=4)
        s = samples[samples[:, 2] == k]
        ax.scatter(s[:, 0], s[:, 1], s=46, c="white", lw=0, alpha=0.85, zorder=4.5)  # halo
        ax.scatter(s[:, 0], s[:, 1], s=24, c=POINT_COLORS[k], edgecolors=INK, linewidths=0.6, zorder=5)

    fig.text(0.07, 0.955, title, fontsize=17, color=INK, weight="bold", family="serif")
    fig.text(0.07, 0.928, subtitle, fontsize=9, color=INK, alpha=0.7)

    handles = [Patch(facecolor=PALETTE[k], edgecolor="white", label=c) for k, c in enumerate(CLASSES)]
    handles += [Line2D([], [], ls="", marker="o", ms=6, mfc="#999", mec=INK, label=f"Amostras (n={len(samples)})"),
                Line2D([], [], ls="", marker="o", ms=3, mfc="#999", mec="white", label=f"Pontos auxiliares (n={len(dots)})")]
    leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.045), ncol=5,
                    fontsize=8, frameon=True, framealpha=0.92,
                    facecolor=BG, edgecolor=INK, title="Zonas paleoclimáticas", title_fontsize=8.5)
    leg.get_frame().set_linewidth(0.4)

    fig.text(0.07, 0.035,
             f"Zonas refinadas por suavização de probabilidade (concordância com o original: "
             f"{rep['concordancia_pixels']:.1%}; deslocamento máx. de fronteira ≈ {rep['deslocamento_max_graus']:.2f}°).\n"
             f"Amostras em posição original; costa completada a partir do contorno atual girado (Natural Earth).",
             fontsize=7, color=INK, alpha=0.65)
    fig.savefig(f"{out_base}.pdf", dpi=300, facecolor=BG)
    fig.savefig(f"{out_base}.png", dpi=250, facecolor=BG)
    plt.close(fig)


def title_from_name(name: str):
    ma = re.search(r"(\d+)_ma", name)
    meta = re.findall(r"(power[\d.]+|sharp[\d.]+|knn|idw|kdtree)", name)
    return (f"Paleoclima — {ma.group(1)} Ma" if ma else "Mapa paleoclimático",
            "Zonação climática interpolada (" + " · ".join(meta) + ") · versão refinada")


def smooth(lines, simplify_deg=0.03):
    """Simplifica (tira o serrilhado de fiordes), resamostra e arredonda (Chaikin)."""
    out = []
    for ln in lines:
        if len(ln) < 4:
            continue
        simple = np.asarray(LineString(ln).simplify(simplify_deg).coords)
        if len(simple) >= 3:
            out.append(coastline.chaikin(coastline.resample(simple, 0.09), False, 2))
    return out


def build_coast(page_lines, extent, cache: Path | None):
    """Costa contínua: costa atual (Natural Earth) girada por placa + sobras do paleo.

    O ajuste de placas é a parte lenta (~4 min) e fica em cache. Devolve (linhas, trechos_com_lado).
    """
    view = (extent[0] - 4, extent[1] + 4, extent[2] - 4, extent[3] + 4)
    stitched = coastline.stitch(coastline.stitch(page_lines), coastline.GAP_DEG)
    modern = paleofit.Modern()
    if cache is not None and cache.exists():
        inview, rots, assign = pickle.loads(cache.read_bytes())
    else:
        inview, rots, assign = modern.fit_lines(stitched, view)
        if cache is not None:
            cache.write_bytes(pickle.dumps((inview, rots, assign)))
    lines, sided = modern.complete(inview, rots, assign, [l for l in stitched if np.ptp(l, axis=0).max() > 0.2], view)
    return smooth(lines), [(smooth([s])[0], side) for s, side in sided if len(s) > 3]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--sigma", type=float, default=3.0, help="suavização das fronteiras (px da grade original)")
    ap.add_argument("--min-area", type=int, default=40, help="manchas menores (px) são absorvidas pelo entorno")
    ap.add_argument("--softness", type=float, default=14.0, help="maior = transição mais estreita")
    ap.add_argument("--relief", type=float, default=0.06, help="sombreamento cosmético (0 desliga)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--no-cache", action="store_true", help="refaz o ajuste de placas da costa (~4 min)")
    ap.add_argument("--no-waves", action="store_true", help="sem as ondulações de água")
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf); page = doc[0]
    geo = fit_georef(page)
    img, extent, legend = extract_zone_raster(doc, page, geo)
    samples, dots, coasts = extract_vectors(page, geo, legend)
    bg = np.array(next((d["fill"] for d in page.get_drawings()
                        if d["fill"] is not None and d["rect"].width > page.rect.width * 0.9), (0.93, 0.94, 0.95)))

    lab0, valid = classify(img, bg)
    h, w = lab0.shape
    jj = np.clip(((samples[:, 0] - extent[0]) / (extent[1] - extent[0]) * w).astype(int), 0, w - 1)
    ii = np.clip(((extent[3] - samples[:, 1]) / (extent[3] - extent[2]) * h).astype(int), 0, h - 1)
    lab_clean = remove_speckles(lab0, valid, a.min_area, (ii, jj, samples[:, 2].astype(int)))
    ij = (ii, jj, samples[:, 2].astype(int))
    P = smooth_probs(lab_clean, valid, a.sigma, anchor_mask(lab0, ij))
    lab1 = np.where(valid, P.argmax(0), -1)
    rep = report(lab0, lab1, valid, extent, samples)

    Pu, rgb = render_zones(P, a.softness, a.relief)
    out_dir = a.out or a.pdf.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / (a.pdf.stem.replace("_full", "") + "_refinado")
    title, sub = title_from_name(a.pdf.stem)
    cache = None if a.no_cache else out_dir / f"{base.name}_costa.cache"
    lines, sided = build_coast(coasts, extent, cache)
    waves = ripples.build(sided, lines) if not a.no_waves else []
    draw_map(base, rgb, Pu, extent, samples, dots, lines, waves, title, sub, rep)
    rep.update({"extent_lon_lat": [round(v, 3) for v in extent], "amostras": len(samples),
                "pontos_auxiliares": len(dots), "parametros": {k: v for k, v in vars(a).items() if k not in ("pdf", "out")}})
    Path(f"{base}_relatorio.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    print(f"Saída: {base}.pdf / .png")


if __name__ == "__main__":
    main()
