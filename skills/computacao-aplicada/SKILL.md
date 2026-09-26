---
name: computacao-aplicada
description: >-
  Acessa, consulta e pesquisa no acervo científico do Mestrado em Computação Aplicada
  (PPGCA/Unisinos) do GabeBrain. Contém as obras estruturadas via Docling, fichas catalográficas
  e 10 Master Skills consolidadas (Engenharia Semiótica/IHC, Ontologias, Machine Learning & Métodos Espaciais,
  Engenharia & Arquitetura de Software, Paleoclima & Geodinâmica, Geoestatística, Geofísica Computacional,
  Geotectônica, Geologia Estrutural e Hidrogeologia). Use sempre que precisar responder
  a dúvidas sobre computação aplicada, algoritmos de vizinhança (k-NN), projeções multidimensionais (LAMP/NCA),
  design centrado no usuário, SWEBOK, SAP-TAM, ou consultar os documentos do mestrado.
---

# Acervo do Mestrado em Computação Aplicada (GabeBrain)

Esta skill conecta os agentes ao acervo de literatura científica do **Mestrado em Computação Aplicada (PPGCA / Unisinos)** de Gabriel (@gabrielhklaser), processado e convertido integralmente pelo motor **IBM Docling**.

---

## 📍 Estrutura e Localização no GabeBrain

- **Raiz do Acervo**: `C:\Users\Gabriel\Meu Drive\Obsidian_GabeBrain\GabeBrain\10-Trabalho\Computacao Aplicada\`
- **Índice Geral (MOC)**: `[[00 - Mestrado em Computacao Aplicada (indice)]]`
- **Texto Estruturado Docling**: `.../Computacao Aplicada/Docling/` (arquivos `.md` completos com tabelas e fórmulas)
- **Fichas Catalográficas**: `.../Computacao Aplicada/Fichas/` (`Ficha - <Nome>.md` com metadados, autores e resumo)
- **Índices das Sessões**: `.../Computacao Aplicada/Indices/` (hubs temáticos de navegação)
- **Script de Busca Rápida**: `.../Computacao Aplicada/Scripts/busca_computacao_aplicada.py`

---

## ⚡ CLI de Busca e Leitura Seletiva (`busca_computacao_aplicada.py`)

Para consultar citações exatas, autores e trechos sem carregar arquivos gigantes na janela de contexto:

```powershell
$CLI = "C:\Users\Gabriel\Meu Drive\Obsidian_GabeBrain\GabeBrain\10-Trabalho\Computacao Aplicada\Scripts\busca_computacao_aplicada.py"

# 1. Buscar termo no acervo (mostra documento, linha e trecho contextualizado):
python $CLI buscar "termo de busca" --limite 5

# 2. Filtrar busca por sessão temática:
python $CLI buscar "Bayesian" --sessao "Paleoclima"
python $CLI buscar "LAMP" --sessao "Redução de Dimensionalidade"

# 3. Ler trecho específico de um documento convertido pelo Docling:
python $CLI ler "joia2011" --inicio 1 --linhas 60

# 4. Inspecionar a Ficha Catalográfica de uma obra:
python $CLI ficha "comaniciu2002"

# 5. Listar todo o catálogo ou filtrar por sessão:
python $CLI listar --sessao "IHC"
```

---

## 📚 As 10 Sessões Temáticas e Obras Centrais

1. **Interação Humano-Computador & Semiótica (`IHC`):**
   - Clarisse de Souza (2001, 2005) - *Semiotic Engineering*, metacomunicação, métodos MIS e MAC.
   - Alan Cooper et al. (2007) - *About Face 3*, Goal-Directed Design, Personas, elisão de impostos cognitivos.
   - Gould & Lewis (1985) - Princípios fundamentais de usabilidade.
   - Herbert Simon (1996) - *The Sciences of the Artificial*.
   - Donald Schön (1983) - *The Reflective Practitioner*.
   - Roman Jakobson - *Linguística e Comunicação* (6 funções da linguagem aplicadas à interface).
   - Ahmed Seffah et al. - *Human-Centered Software Engineering (HCSE)*.
   - **Master Skill Associada:** `[[Master_IHC_e_Engenharia_Semiotica]]` (#14).

2. **Engenharia de Ontologias & Web Semântica (`ontologia`):**
   - Tellus-Onto (SBSI 2021) - Ontologia formal para geociências e recursos da terra.
   - B-Track Onto (SBSI 2023, iSys 2024) - Ontologia para acompanhamento longitudinal de pacientes com doenças crônicas.
   - CIE Framework (2024) - Engenharia de ontologias aplicada a saúde do trabalhador e exposoma ocupacional.
   - Metodologias NeOn e 101, OWL-DL, SPARQL, SWRL, reasoners (HermiT, Pellet) e UFO/BFO.
   - **Master Skill Associada:** `[[Master_Ontologias_e_Modelagem_Conhecimento]]` (#13).

3. **Machine Learning, Reconhecimento de Padrões & Métodos Espaciais (`KNN`, `redução de dimensionalidade`, `computação grafica`, `IA`, `R`):**
   - Classificação por instâncias: k-NN, métricas Minkowski/Mahalanobis, limites de Cover & Hart (1967).
   - Redução de Dimensionalidade: LAMP (Joia et al. 2011 - Procrustes ortogonal local via SVD), NCA (Sinaice et al. 2021 para sensores hiperespectrais).
   - Projeções Inversas: Ribeiro et al. (2019) para inspeção de fronteiras de decisão e comitês de classificadores.
   - Agrupamento Espacial: DBSCAN (Ester et al. 1996), Mean Shift (Comaniciu & Meer 2002; Szeliski 2022).
   - Geociências e Python: Maurizio Petrelli (2023) - Machine Learning for Earth Sciences (CoDA, ilr/clr de Aitchison, eletrofacies).
   - Inteligência Artificial: Russell & Norvig (PEAS, agentes racionais e arquiteturas).
   - **Master Skill Associada:** `[[Master_Machine_Learning_e_Ciencia_de_Dados]]` (#15).

4. **Engenharia & Arquitetura de Software (`arquitetura de software`, `Projeto`):**
   - IEEE SWEBOK v4 (2024) - 8 KAs essenciais (Requisitos, Arquitetura, Construção, Teste, Manutenção, SCM, Gestão, Modelos).
   - SAP-TAM Standard - Modelagem formal de arquitetura técnica (Níveis Conceitual e de Design; Agentes, Storages, Channels, Portas e ProtocolBoundaries).
   - Jeff Sutherland - Scrum: A Arte de Fazer o Dobro do Trabalho na Metade do Tempo.
   - Kleinberg & Tardos - *Algorithm Design* (Gulosos, Divisão e Conquista, DP, Fluxo em Redes, NP-Completude).
   - **Master Skill Associada:** `[[Master_Engenharia_e_Arquitetura_Software]]` (#16).

5. **Paleoclima & Modelagem Tectônica (`.`):**
   - Scotese et al. (2024) - Reconstrução geodinâmica e tectônica de placas do Cretáceo (PALEOMAP, GPlates v3).
   - Burgener et al. (2023) - Classificação Paleo-Köppen via modelagem Bayesiana (MCMC) de litologias, fósseis e geoquímica.
   - Indicadores paleoceanográficos: TEX86 (lipídios de arqueias), $\delta^{18}\text{O}$, supergreenhouse Aptiano-Albiano (Hasegawa et al. 2012).
   - Automação cartográfica: Generic Mapping Tools (GMT - Wessel et al. 2013) e PROWIS (workflows visuais).
   - **Master Skill Associada:** `[[Master_Paleoclima_e_Geologia_Espacial]]` (#10).

6. **Geoestatística & Métodos Quantitativos Espaciais (`Geoestatistica`):**
   - Yamamoto & Landim (2013) - Variáveis regionalizadas, semivariogramas teóricos (esférico, exponencial, gaussiano), Krigagem Ordinária/Simples/Indicatriz e Simulação Gaussiana Sequencial (SGS).
   - **Master Skill Associada:** `[[Master_Geoestatistica_e_Modelagem_Espacial]]` (#17).

7. **Geofísica Computacional & Sensores (`Geofísica`):**
   - Dentith & Mudge (2014, Cambridge) - Processamento digital de sinais geofísicos, FFT 2D, redução ao polo (RTP), continuação de campos potenciais, sinal analítico 3D e inversão geofísica.
   - **Master Skill Associada:** `[[Master_Geofisica_Computacional_e_Inversao]]` (#18).

8. **Geotectônica & Cinemática de Placas (`Geotectonica`):**
   - Kearey, Klepeis & Vine (2014) - Cinemática esférica, polos e matrizes de rotação finita de Euler, isócronas oceânicas e parametrização GPlates.
   - Hasui et al. (2012) e Mantesso-Neto et al. (2004) - Arquitetura orogênica, crátons précambrianos, ciclo brasiliano e abertura do Atlântico Sul.
   - **Master Skill Associada:** `[[Master_Geotectonica_e_Cinematica_Placas]]` (#19).

9. **Geologia Estrutural & Mecânica de Deformação (`Estrutural`):**
   - Davis, Reynolds & Kluth (2011, Wiley) - Tensores de tensão e deformação contínua, círculos de Mohr, critérios de ruptura Mohr-Coulomb/Byerlee, cinemática de falhas e geometria 3D.
   - **Master Skill Associada:** `[[Master_Geologia_Estrutural_e_Tensores]]` (#20).

10. **Hidrogeologia Computacional & Modelagem de Fluxo (`Hidrogeologia`):**
    - Feitosa et al. (2008, CPRM/LABHID) - Equação diferencial 3D de fluxo subterrâneo transiente, Lei de Darcy, soluções analíticas de Theis e Cooper-Jacob, hidráulica de aquíferos porosos, fraturados e cársticos.
    - **Master Skill Associada:** `[[Master_Hidrogeologia_e_Modelagem_Fluxo]]` (#21).

11. **Petrologia Geoquímica & Vulcanologia (`Petrologias`, `Vulcões`):**
    - Myron G. Best (2003) - Termodinâmica de equilíbrio de fases e diagramas multicomponentes.
    - Yardley et al. (1990) - Trajetórias P-T-t e texturas microestruturais petrográficas para treino de visão computacional.
    - Haraldur Sigurdsson (2000) e Oppenheimer et al. (2003) - Vulcanismo, reologia magmática, desgaseificação de voláteis ($SO_2, CO_2$) e forçamento climático de aerossóis.
    - **Master Skills Associadas:** `[[Master_Paleoclima_e_Geologia_Espacial]]` (#10) · `[[Master_Frontend_Design_e_UI_Engineering]]` (#05).

12. **Modelagem Matemática e Físico-Química (`Exatas`):**
    - James Stewart (2012) - Solucionários analíticos e multivariáveis de Cálculo diferencial, integral e vetorial (Gauss, Green, Stokes, EDPs).
    - Peter Atkins (2008, 2012) e McQuarrie (1999) - Físico-química clássica, energia de Gibbs, equilíbrio iônico e termodinâmica estatística molecular.
    - **Master Skill Associada:** `[[Master_Geoestatistica_e_Modelagem_Espacial]]` (#17).

13. **Geomorfologia e Dinâmica Costeira (`Geomorfologia`):**
    - Dieter Muehe et al. (PGGM, 2020) - Morfodinâmica costeira, batimetria computacional, sonografia e reconstrução de relevo submarino (Paleo-DEMs).
    - **Master Skill Associada:** `[[Master_GIS_Geoprocessamento]]` (#01).

14. **Geologia Geral e Geodiversidade (`Geologia Geral`, `Geologia de Sergipe`):**
    - Richard C. Selley (2005) - Encyclopedia of Geology (tesauro terminológico enciclopédico para ontologias).
    - Frank Press et al. (2006) - Para Entender a Terra e dinâmica de sistemas terrestres globais.
    - CPRM (2017) - Geodiversidade do Estado de Sergipe e modelagem SIG multicritério.
    - **Master Skill Associada:** `[[Master_Ontologias_e_Modelagem_Conhecimento]]` (#13).

---

## 🛡️ Protocolo Obrigatório para Agentes de IA

1. **Evidência Documental Rígida:** Ao formular soluções baseadas em técnicas do mestrado (ex: justificar a escolha de LAMP vs PCA, definir axiomas em OWL, calcular métricas de usabilidade em semiotic inspection ou desenhar arquiteturas SAP-TAM), **cite expressamente os autores e o documento correspondente no acervo**.
2. **Prioridade de Consulta:**
   - 1º: Master Skills em `📚 Biblioteca de Agentes\` (`Master_*.md`)
   - 2º: CLI `busca_computacao_aplicada.py` ou leitura seletiva no `Docling/`
   - 3º: Fichas Catalográficas em `Fichas/`
   - 4º: Conhecimento geral do modelo (sempre declarando quando for inferência externa).
