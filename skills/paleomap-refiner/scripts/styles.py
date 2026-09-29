"""Camadas de estilo do mapa (textura de água, sombra da costa, luz de borda, batimetria, vinheta).

Tudo é decorativo e calculado sobre a máscara terra/mar (landmask.build); não toca nas zonas
nem nas amostras. Cada camada é um RGBA float (h, w) na mesma grade da máscara (origem no topo).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi

INK = np.array([0.055, 0.118, 0.200])       # sombra: azul-marinho profundo
WHITE = np.array([1.0, 1.0, 1.0])
SHALLOW = np.array([0.36, 0.66, 0.72])      # batimetria: água rasa
DEEP = np.array([0.05, 0.19, 0.33])         # batimetria: água profunda
LAND_TINT = np.array([0.933, 0.902, 0.827])  # terra fora da caixa de zonas


@dataclass(frozen=True)
class Style:
    name: str
    sea_zone_alpha: float   # opacidade das zonas sobre o mar (1 = igual à terra)
    texture: float          # força da textura de água
    ripple_lines: float     # força das linhas finas de ondulação da textura
    shadow: float           # força da sombra da terra sobre o mar
    shadow_off_deg: tuple   # deslocamento da sombra (lon, lat) em graus
    shadow_blur_deg: float
    rim: float              # luz de borda na terra (lado do sol)
    bathy: float            # força do degradê raso -> profundo
    bathy_scale_deg: float
    vignette: float
    extras: bool            # rosa dos ventos + barra de escala


STYLES = {
    "1-pragmatico": Style("1-pragmatico", 0.88, 0.35, 0.0, 0.22, (0.10, -0.10), 0.22, 0.0, 0.0, 1.0, 0.0, False),
    "2-artistico": Style("2-artistico", 0.78, 0.55, 0.45, 0.38, (0.18, -0.18), 0.35, 0.22, 0.22, 2.0, 0.10, False),
    "3-dramatico": Style("3-dramatico", 0.66, 0.75, 0.7, 0.62, (0.32, -0.32), 0.55, 0.45, 0.42, 3.0, 0.22, True),
}


def _noise(shape, sigma, rng):
    n = ndi.gaussian_filter(rng.normal(0, 1, shape), sigma)
    return n / (n.std() + 1e-9)


def water_texture(shape, res, strength, lines, seed=11):
    """Textura de água: manchas suaves + linhas finas de ondulação. Retorna (claro, escuro) em [0, 1]."""
    rng = np.random.default_rng(seed)
    px = 1.0 / res  # pixels por grau
    mott = 0.6 * _noise(shape, 0.25 * px, rng) + 0.4 * _noise(shape, 0.07 * px, rng)
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]] / px
    warp = 0.9 * _noise(shape, 0.5 * px, rng)
    wave = np.sin(2 * np.pi * ((xx * 0.55 + yy * 0.83) / 0.42 + warp))  # ondas oblíquas, ~0,42° de período
    crest = np.clip((wave - 0.86) / 0.14, 0, 1) * np.clip(0.55 + 0.45 * _noise(shape, 0.3 * px, rng), 0, 1)
    light = np.clip(0.5 * mott, 0, None) * strength * 0.10 + crest * lines * 0.20 * strength
    dark = np.clip(-0.5 * mott, 0, None) * strength * 0.10
    return np.clip(light, 0, 1), np.clip(dark, 0, 1)


def build(land: np.ndarray, extent: tuple, style: Style, rel: np.ndarray) -> dict:
    """rel (0-1): confiança da máscara; sombra, luz de borda e batimetria só valem perto da costa desenhada.
    Devolve {'water': RGBA, 'shadow': RGBA, 'rim': RGBA|None, 'bathy': RGBA|None, 'land': RGBA, 'vignette': RGBA|None, 'sea': float}."""
    lon0, lon1, lat0, lat1 = extent
    h, w = land.shape
    res = (lon1 - lon0) / w
    landf = ndi.gaussian_filter(land.astype(float), 0.8)
    sea = 1.0 - landf

    # textura de água (só no mar)
    light, dark = water_texture(land.shape, res, style.texture, style.ripple_lines)
    water = np.zeros((h, w, 4))
    water[..., :3] = np.where((light > dark)[..., None], WHITE, INK)
    soft_sea = ndi.gaussian_filter(sea, 0.6 / res) ** 2  # máscara suavizada: erros viram esmaecimento, não retângulos
    water[..., 3] = np.maximum(light, dark) * soft_sea

    # sombra da terra sobre o mar (luz de NW: a sombra cai para SE)
    dx, dy = style.shadow_off_deg
    moved = ndi.shift(landf, (-dy / res, dx / res), order=1, mode="nearest")  # -dy: lat sobe = linha desce
    cast = ndi.gaussian_filter(moved, style.shadow_blur_deg / res)
    shadow = np.zeros((h, w, 4))
    shadow[..., :3] = INK
    shadow[..., 3] = np.clip(cast, 0, 1) * sea * style.shadow * rel

    out = {"water": water, "shadow": shadow, "sea": sea, "rim": None, "bathy": None, "vignette": None}

    if style.rim > 0:  # luz de borda: a terra "acende" na borda voltada ao sol (NW)
        lit = ndi.shift(landf, (dy / res * 0.6, -dx / res * 0.6), order=1, mode="nearest")
        edge = np.clip(landf - ndi.gaussian_filter(lit, 0.16 / res), 0, 1)
        rim = np.zeros((h, w, 4))
        rim[..., :3] = WHITE
        rim[..., 3] = np.clip(edge * 1.6, 0, 1) * landf * style.rim * rel
        out["rim"] = rim

    if style.bathy > 0:  # raso -> profundo com a distância da costa
        dist = ndi.distance_transform_edt(landf < 0.5) * res
        t = 1 - np.exp(-dist / style.bathy_scale_deg)
        bathy = np.zeros((h, w, 4))
        bathy[..., :3] = SHALLOW[None, None, :] * (1 - t[..., None]) + DEEP[None, None, :] * t[..., None]
        bathy[..., 3] = style.bathy * sea * rel
        out["bathy"] = bathy

    if style.vignette > 0:
        yy, xx = np.mgrid[0:h, 0:w]
        r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / np.sqrt(2)
        vig = np.zeros((h, w, 4))
        vig[..., :3] = INK
        vig[..., 3] = np.clip((r - 0.45) / 0.55, 0, 1) ** 2 * style.vignette
        out["vignette"] = vig
    return out


def land_tint(land: np.ndarray) -> np.ndarray:
    """Terra em tom de pergaminho (aparece fora da caixa das zonas)."""
    landf = ndi.gaussian_filter(land.astype(float), 0.8)
    rgba = np.zeros(land.shape + (4,))
    rgba[..., :3] = LAND_TINT
    rgba[..., 3] = landf
    return rgba
