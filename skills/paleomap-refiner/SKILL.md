---
name: paleomap-refiner
description: >-
  Refina mapas paleoclimáticos exportados em PDF (zonas Árido/Semiárido/Úmido + amostras), dando
  acabamento estético (paleta, transições suaves, contornos, halo nos pontos) sem mover dados.
  Extrai o raster de zonas e os vetores (amostras, costa, graticule) do PDF "full", suaviza só as
  fronteiras das zonas e gera PDF/PNG + relatório JSON de fidelidade científica.
---

# Paleomap Refiner

## Quando usar
Mapas `map_<idade>_ma_..._full.pdf` gerados pelo pipeline KNN/IDW de paleoclima, quando se quer
uma versão de publicação mais bonita mantendo o rigor.

## Uso
```bash
python scripts/refine_paleomap.py <mapa_full.pdf> [--sigma 3] [--min-area 40] [--softness 14] [--relief 0.06] [--out <pasta>]
```
Saída: `<nome>_refinado.pdf`, `.png` e `_relatorio.json` (padrão: pasta do PDF de entrada).
Use o PDF **full** (tem pontos e costa em vetor = posição exata). O "raster" é só imagem.

## O que é invariante (regras científicas)
- Amostras e pontos auxiliares: coordenadas lidas do vetor do PDF, nunca alteradas.
- Linhas de costa: vetor original reprojetado com o mesmo georreferenciamento.
- Zonas: só a forma da fronteira muda (suavização gaussiana da probabilidade de cada classe +
  argmax). Manchas < `--min-area` px são absorvidas, **exceto** as que contêm amostra da mesma classe.

## O que o relatório mede
`concordancia_pixels` (≥ 0,98 recomendado), áreas por classe antes/depois,
`deslocamento_max_graus` da fronteira, coerência amostra↔zona. Se a concordância cair abaixo de 0,98,
reduza `--sigma`.

## Parâmetros
- `--sigma`: suavização (px da grade original; 1 px ≈ 0,1°). 2–4 é seguro.
- `--softness`: largura visual da transição entre cores (maior = mais estreita). Só cosmético.
- `--relief`: sombreamento decorativo do campo úmido–árido (0 desliga).
