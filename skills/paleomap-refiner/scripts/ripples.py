"""Ondulações de água ("water lining") do lado do mar: contornos paralelos à costa que esmaecem.

Estilo de carta náutica antiga. Só usa trechos com lado do mar conhecido (paleofit.Modern.complete).
Pedaços que invadem outra costa (canais estreitos, baías) são cortados.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString

LEVELS_DEG = (0.22, 0.50, 0.90, 1.45)
ALPHAS = (0.55, 0.40, 0.26, 0.14)
MIN_SIZE_DEG = 3.0  # lagos e ilhotas ficam sem ondulação (não dá para distingui-los de ilhas)
KEEP_FRAC = 0.85  # vértice do contorno precisa estar a >= 85% da distância nominal de qualquer costa


def _parts(curve):
    return list(getattr(curve, "geoms", [curve]))


def build(sided_runs, all_lines, levels=LEVELS_DEG):
    """Devolve [(distância, contorno lon/lat)] com os contornos já filtrados."""
    dense = np.vstack([_densify(l, 0.05) for l in all_lines])
    tree = cKDTree(dense)
    out = []
    for seg, side in sided_runs:
        if side == 0 or len(seg) < 4 or np.ptp(seg, axis=0).max() < MIN_SIZE_DEG:
            continue
        k = np.cos(np.deg2rad(seg[:, 1].mean()))
        scaled = np.column_stack([seg[:, 0] * k, seg[:, 1]])
        line = LineString(scaled)
        for d in levels:
            try:
                curve = line.offset_curve(side * d, join_style="round", quad_segs=4)
            except Exception:
                continue
            for part in _parts(curve):
                xy = np.asarray(part.coords)
                if len(xy) < 3:
                    continue
                ll = np.column_stack([xy[:, 0] / k, xy[:, 1]])
                ok = tree.query(ll)[0] >= KEEP_FRAC * d  # graus lon/lat: aproximação boa nos trópicos
                for piece in _runs(ll, ok):
                    out.append((d, piece))
    return out


def _runs(ll, ok, min_pts=4):
    edges = np.flatnonzero(np.diff(np.r_[0, ok.astype(int), 0]))
    return [ll[a:b] for a, b in zip(edges[::2], edges[1::2]) if b - a >= min_pts]


def _densify(line, step):
    seg = np.hypot(*np.diff(line, axis=0).T)
    out = [line[:1]]
    for a, b, s in zip(line[:-1], line[1:], seg):
        n = max(int(np.ceil(s / step)), 1)
        out.append(a + (b - a) * (np.arange(1, n + 1) / n)[:, None])
    return np.vstack(out)
