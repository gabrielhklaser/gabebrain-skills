---
name: paleomap-refiner
description: >-
  Refina mapas paleoclimáticos exportados em PDF (zonas Árido/Semiárido/Úmido + amostras): acabamento
  artístico (paleta, transições suaves, ondulações de água) sem mover dados, e costa contínua reconstruída
  a partir da costa atual (Natural Earth) girada pela placa. Entrada: PDF "full". Saída: PDF/PNG + JSON.
---

# Paleomap Refiner

## Uso
```bash
python scripts/refine_paleomap.py <mapa_full.pdf> [--sigma 3] [--min-area 40] [--softness 14] [--relief 0.06]
                                  [--no-waves] [--no-cache] [--out <pasta>]
```
Saída em `<pasta>` (padrão: a do PDF): `<nome>_refinado.pdf`, `.png`, `_relatorio.json`, `_costa.cache`.
Use o PDF **full** (pontos e costa em vetor). O "raster" é só imagem.
1ª execução de um mapa: ~4-5 min (ajuste de placas); com o `.cache`, ~1 min.
Baixa sozinha (1ª vez) o Natural Earth 10m coastline e 50m land para `data/`.

## Regras científicas (invariantes)
- Amostras e pontos auxiliares: coordenadas do vetor do PDF, nunca alteradas.
- Zonas: só a forma da fronteira muda (suavização de probabilidade; manchas com amostra da mesma classe
  são preservadas). O relatório mede concordância de pixels, áreas e deslocamento máximo.
- Costa = mapa-base, não dado: pode ser reconstruída.

## Como a costa é completada (`paleofit.py`)
A costa do mapa paleo é a costa atual GIRADA por placa. Busca aleatória em SO(3) + ICP acha a rotação
de cada trecho (<= 12°) da costa paleo (erro ~0,03° nos bons casos); uma rotação só vale se explicar
>= 25° de costa (evita casamentos por acaso). Com a rotação, a costa atual em alta resolução substitui
os trechos que encaixam e preenche as falhas entre eles; o que o paleo tem a mais (lagos etc.) é mantido.

## Estilo (`ripples.py`)
Sem halo branco: costa em tinta azul-marinho + "water lining" (contornos paralelos que esmaecem) só no lado
do mar (lado testado nos polígonos de terra atuais). Lagos e ilhotas < 3° ficam sem ondulação.

## Limitações conhecidas
- Trechos sem placa ajustada mantêm a costa paleo original (suavizada), podendo ter serrilhado.
- Fiordes densos (Patagônia) ficam carregados.
- Ondulações usam distância em graus (boas nos trópicos; ~40% menores em latitudes altas).
