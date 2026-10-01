"""Máscara terra/mar e distância à costa, para os efeitos artísticos no lado do mar.

Perto da costa de cada placa (<= BUFFER_DEG), a terra vem dos polígonos de terra ATUAIS girados pela
rotação daquela placa. Mais longe, cada pixel herda o rótulo do pixel classificado mais próximo.
Não depende de a costa estar fechada.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import shapely
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.segmentation import watershed

import paleofit as pf

RES_DEG = 0.05
BUFFER_DEG = 3.0


@dataclass(frozen=True)
class SeaField:
    extent: tuple         # lon0, lon1, lat0, lat1
    land: np.ndarray      # bool (h, w), origem no topo
    dist_deg: np.ndarray  # distância (graus) até a costa, só no mar; 0 em terra


def _raster(lines, extent, shape):
    lon0, lon1, lat0, lat1 = extent
    h, w = shape
    res = (lon1 - lon0) / w
    img = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(img)
    for ln in lines:
        x = (ln[:, 0] - lon0) / res - 0.5
        y = (lat1 - ln[:, 1]) / res - 0.5
        draw.line(list(zip(x.tolist(), y.tolist())), fill=1, width=1)
    return np.asarray(img, bool)


def build(plate_runs, rots, land_geom, all_lines, extent, res=RES_DEG, buffer_deg=BUFFER_DEG,
          min_plate_deg=25.0) -> SeaField:
    lon0, lon1, lat0, lat1 = extent
    w, h = int((lon1 - lon0) / res), int((lat1 - lat0) / res)
    lon = lon0 + (np.arange(w) + 0.5) * res
    lat = lat1 - (np.arange(h) + 0.5) * res
    gx, gy = np.meshgrid(lon, lat)

    best_d = np.full((h, w), np.inf, np.float32)
    best_k = np.full((h, w), -1, np.int16)
    length = lambda runs: sum(float(np.hypot(*np.diff(r, axis=0).T).sum()) for r in runs)
    plate_runs = {k: v for k, v in plate_runs.items() if length(v) >= min_plate_deg}  # placas sem peso = ruído
    for k, runs in plate_runs.items():
        d = (ndi.distance_transform_edt(~_raster(runs, extent, (h, w))) * res).astype(np.float32)
        closer = d < best_d
        best_d[closer], best_k[closer] = d[closer], k

    known = best_d < buffer_deg
    land = np.zeros((h, w), bool)
    for k in plate_runs:
        sel = known & (best_k == k)
        if not sel.any():
            continue
        paleo = pf.ll2xyz(np.column_stack([gx[sel], gy[sel]]))
        modern = pf.xyz2ll(paleo @ rots[k].T)  # paleo = moderno @ R  ->  moderno = paleo @ R.T
        land[sel] = shapely.contains_xy(land_geom, modern[:, 0], modern[:, 1])

    coast = _raster(all_lines, extent, (h, w))
    # propaga os rótulos conhecidos sem atravessar a costa (4-conectado: a linha de 1 px bloqueia diagonais)
    markers = np.where(known & ~coast, np.where(land, 1, 2), 0)
    order = ndi.distance_transform_edt(markers == 0).astype(np.float32)  # inunda do marcador mais próximo
    filled = watershed(order, markers, mask=~coast, connectivity=1)
    land = filled == 1
    land = ndi.binary_opening(land, iterations=1)

    dist = ndi.distance_transform_edt(~coast) * res
    dist[land] = 0.0
    return SeaField(extent, land, dist)
