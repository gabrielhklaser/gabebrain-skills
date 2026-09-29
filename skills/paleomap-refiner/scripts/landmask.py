"""Máscara terra/mar com os continentes fechados.

No PDF a costa vem em arcos abertos (não há polígonos). Como cada trecho é a costa atual girada por
placa (paleofit), a terra de cada placa vem dos polígonos de terra ATUAIS girados pela mesma
rotação. Cada pixel usa a placa cuja costa ajustada está mais perto (Voronoi), dentro de
BUFFER_DEG; além disso herda o rótulo do pixel conhecido mais próximo. No fim, limpeza morfológica.
"""
from __future__ import annotations

import numpy as np
import shapely
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.segmentation import watershed

import paleofit as pf

RES_DEG = 0.05
BUFFER_DEG = 3.5
MIN_ISLAND_DEG2 = 0.06  # manchas menores que isso (graus²) são ruído de generalização


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


def _remove_small(mask, res):
    """Tira manchas (de terra e de mar) menores que MIN_ISLAND_DEG2."""
    min_px = MIN_ISLAND_DEG2 / res**2
    out = mask.copy()
    for value in (True, False):
        lab, n = ndi.label(out == value)
        if n:
            sizes = ndi.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
            small = np.isin(lab, np.flatnonzero(sizes < min_px) + 1)
            out[small] = not value
    return out


def build(runs, rots, land_geom, lines, extent, res=RES_DEG, buffer_deg=BUFFER_DEG, min_plate_deg=35.0,
          vote_deg=2.0, min_run_deg=15.0, primary_deg=100.0):
    """runs: [(seg lon/lat, índice_da_placa)]. Devolve (terra, confiável): bool (h, w), origem no topo."""
    lon0, lon1, lat0, lat1 = extent
    w, h = int((lon1 - lon0) / res), int((lat1 - lat0) / res)
    lon = lon0 + (np.arange(w) + 0.5) * res
    lat = lat1 - (np.arange(h) + 0.5) * res
    gx, gy = np.meshgrid(lon, lat)

    total = lambda segs: sum(float(np.hypot(*np.diff(s, axis=0).T).sum()) for s in segs)
    by_plate = {}
    for seg, k in runs:
        by_plate.setdefault(k, []).append(seg)
    # só placas bem ancoradas mandam (as parciais casam por acaso em parte do traçado); de cada uma
    # valem TODOS os trechos, pois compartilham a mesma rotação
    by_plate = {k: v for k, v in by_plate.items() if total(v) >= primary_deg}
    dist = {k: (ndi.distance_transform_edt(~_raster(segs, extent, (h, w))) * res).astype(np.float32)
            for k, segs in by_plate.items()}
    plates = list(dist)
    pd = np.stack([dist[k] for k in plates])
    nearest = pd.min(axis=0)
    pbest = np.array(plates)[np.argmin(pd, axis=0)]

    def is_land(k, sel):
        paleo = pf.ll2xyz(np.column_stack([gx[sel], gy[sel]]))
        modern = pf.xyz2ll(paleo @ rots[k].T)  # paleo = moderno @ R  ->  moderno = paleo @ R.T
        return shapely.contains_xy(land_geom, modern[:, 0], modern[:, 1])

    # margens quase encostadas (Brasil x África): perto (< vote_deg) das duas, é terra se qualquer uma disser terra
    land = np.zeros((h, w), bool)
    for k in plates:
        near = dist[k] < vote_deg
        if near.any():
            land[near] |= is_land(k, near)
    known = nearest < buffer_deg
    for k in plates:  # além do raio de voto: vale a placa mais próxima
        sel = (pbest == k) & known & (nearest >= vote_deg)
        if sel.any():
            land[sel] = is_land(k, sel)

    # inunda a partir da faixa confiável sem cruzar a costa (as linhas são barreira)
    barrier = _raster(lines, extent, (h, w))
    barrier = ndi.binary_dilation(barrier, structure=ndi.generate_binary_structure(2, 1))
    markers = np.where(known & ~barrier, np.where(land, 1, 2), 0)
    order = ndi.distance_transform_edt(markers == 0).astype(np.float32)
    filled = watershed(order, markers, mask=~barrier, connectivity=1)
    _, (iy, ix) = ndi.distance_transform_edt(filled == 0, return_indices=True)  # barreira e recintos sem semente
    land = filled[iy, ix] == 1
    return _remove_small(land, res), known


def coast_reliability(lines, extent, shape, full_deg=1.5, fade_deg=2.0):
    """1 perto da costa desenhada (onde a máscara é boa), caindo a 0 a full_deg + fade_deg de distância."""
    h, w = shape
    res = (extent[1] - extent[0]) / w
    d = ndi.distance_transform_edt(~_raster(lines, extent, (h, w))) * res
    return np.clip(1 - (d - full_deg) / fade_deg, 0, 1)
