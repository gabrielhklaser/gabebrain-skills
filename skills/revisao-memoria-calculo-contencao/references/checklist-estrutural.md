# Checklist estrutural (concreto armado em contenção)

Use depois de revisar a geotecnia. Para cada item, registre Atendido, Parcial, Pendente ou N/A, com a página do relatório.

## Índice
1. Identificação do modelo
2. Ações e combinações
3. Elementos dimensionados x elementos das pranchas
4. Materiais e durabilidade
5. Verificações de ELU
6. Verificações de ELS
7. Fundações
8. Detalhamento
9. Consistência interna

## 1. Identificação do modelo
- Software e versão, ou método manual declarado.
- Modelo estrutural descrito (pórtico espacial, pilares isolados, cortina como laje, etc.).
- Apoios e vinculações justificados (engastes, coeficientes de flambagem, rigidez).
- Planta de formas e níveis (grupos e pisos) compatível com as pranchas.

## 2. Ações e combinações
- Peso próprio, permanentes, sobrecarga e empuxos como ações separadas.
- Empuxo de solo tratado como ação permanente ou variável conforme a norma, com coeficiente adequado. Carga de empuxo lançada como "permanente" é aceitável, mas a origem do valor tem de estar na memória geotécnica.
- Coeficientes parciais e de combinação conforme NBR 8681 e 6118 (por exemplo γf = 1,4).
- Combinações de ELU e ELS definidas, com as de ELS usadas nas verificações de fissuração e deslocamento.

## 3. Elementos dimensionados x elementos das pranchas
Montar um quadro: cada elemento das pranchas 1 a N e o resultado correspondente no relatório. Procure especificamente por:
- Pilares, vigas, lajes ou pisos, cortinas, blocos e sapatas, tirantes.
- Elementos citados nos materiais ou nos dados geométricos, mas sem resultado de dimensionamento.

## 4. Materiais e durabilidade
- Classe de agressividade ambiental declarada e justificada.
- fck, módulo de elasticidade e cobrimento coerentes com a classe (ver `normas.md`).
- Cortina em contato com solo com classe de concreto compatível.
- Aço (CA-50, CA-60) com fyk e γs corretos.

## 5. Verificações de ELU
- Flexão composta (N,M) e cortante (Q) para todos os trechos.
- Esbeltez e efeitos de segunda ordem em pilares, com comprimentos de flambagem justificados.
- Torção, se relevante.
- Estabilidade global da estrutura, quando for aporticada.
- Taxa de armadura entre mínimo e máximo da norma.
- Utilização acima de 95%: destacar e perguntar se há sensibilidade a variação de carga.

## 6. Verificações de ELS
- Abertura de fissuras wk comparada ao limite da classe de agressividade.
- Deslocamentos horizontais de topo e flechas, com limites declarados.
- Se o relatório só define combinações de ELS e não mostra resultado, registre Pendente.

## 7. Fundações
- Esforços na base apresentados (arranques) e usados para dimensionar sapata, estaca ou tirante.
- Tensão admissível do solo e referência da sondagem.
- Esforço normal de tração (N negativo, conforme convenção do software): verificação de arrancamento obrigatória.
- Excentricidades e momentos na base considerados.

## 8. Detalhamento
- Ancoragem, emendas, estribos, espaçamentos máximos e mínimos.
- Armaduras do relatório coerentes com as das pranchas (diâmetros, quantidades, espaçamentos).
- Juntas de dilatação, drenos e barbacãs nas pranchas coerentes com a premissa geotécnica.

## 9. Consistência interna
- Cargas e geometrias repetidas ou arredondadas em demasia.
- Seções duplicadas (por exemplo tabela de materiais repetida).
- Datas e assinaturas coerentes com o parecer e com o prazo.
- Responsável técnico, ART/RRT e assinatura conforme exigido.
