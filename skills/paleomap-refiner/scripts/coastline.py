"""Costa contínua e suave a partir dos fragmentos vetoriais do PDF.

A linha de costa é mapa-base (não é dado da pesquisa), então aqui ela pode ser
reconstruída: fragmentos são costurados pelas pontas, microfeições somem e o
traçado é suavizado (Chaikin). Anéis fechados viram polígonos de continente.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

SNAP_DEG = 0.03      # pontas mais próximas que isso são a mesma
CLOSE_DEG = 0.6      # linha cujas pontas ficam a menos disso vira anel
MIN_SIZE_DEG = 0.35  # feições menores que isso (bbox) são descartadas
STEP_DEG = 0.22      # espaçamento de reamostragem antes de suavizar
GAP_DEG = 0.45       # 2ª passada: fecha lacunas pequenas entre trechos de costa


def is_area(ln: np.ndarray) -> bool:
    """Anel de verdade (não um traço que vai e volta): área relevante p/ o perímetro."""
    x, y = ln[:, 0], ln[:, 1]
    area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    per = np.hypot(*np.diff(ln, axis=0).T).sum()
    return area / (per ** 2 + 1e-12) > 0.01


def stitch(parts: list[np.ndarray], tol: float = SNAP_DEG) -> list[np.ndarray]:
    """Une fragmentos cujas pontas coincidem (grafo de pontas, percurso guloso)."""
    parts = [p for p in parts if len(p) > 1]
    ends = np.array([p[0] for p in parts] + [p[-1] for p in parts])
    tree = cKDTree(ends)
    n = len(parts)
    used = np.zeros(n, bool)

    def neighbor(pt, exclude):
        for j in tree.query_ball_point(pt, tol):
            k = j % n
            if not used[k] and k != exclude:
                return k, j >= n  # True = casou com o fim do fragmento
        return None

    lines = []
    for i in range(n):
        if used[i]:
            continue
        used[i] = True
        chain = [parts[i]]
        for forward in (True, False):
            while True:
                tip = chain[-1][-1] if forward else chain[0][0]
                nb = neighbor(tip, -1)
                if nb is None:
                    break
                k, at_end = nb
                used[k] = True
                seg = parts[k]
                if forward:
                    chain.append(seg[::-1] if at_end else seg)
                else:
                    chain.insert(0, seg if at_end else seg[::-1])
        lines.append(np.vstack(chain))
    return lines


def resample(line: np.ndarray, step: float) -> np.ndarray:
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(line, axis=0).T))]
    if d[-1] < step * 3:
        return line
    t = np.linspace(0, d[-1], int(d[-1] / step) + 1)
    return np.column_stack([np.interp(t, d, line[:, 0]), np.interp(t, d, line[:, 1])])


def chaikin(line: np.ndarray, closed: bool, it: int = 3) -> np.ndarray:
    for _ in range(it):
        a = line if closed else line[:-1]
        b = np.roll(line, -1, axis=0) if closed else line[1:]
        q, r = 0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b
        mid = np.column_stack([q, r]).reshape(-1, 2)
        line = mid if closed else np.vstack([line[0], mid, line[-1]])
    return line


def build(parts: list[np.ndarray]):
    """Devolve (anéis de terra, linhas abertas), suavizados."""
    rings, opens = [], []
    for ln in stitch(stitch(parts), GAP_DEG):
        size = np.ptp(ln, axis=0).max()
        if size < MIN_SIZE_DEG:
            continue
        closed = np.hypot(*(ln[0] - ln[-1])) < max(CLOSE_DEG, 0.02 * size) and is_area(ln)
        ln = chaikin(resample(ln, STEP_DEG), closed)
        (rings if closed else opens).append(np.vstack([ln, ln[:1]]) if closed else ln)
    return rings, opens
