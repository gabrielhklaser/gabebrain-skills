# Solo, empuxo e estabilidade: o que exigir e como conferir

## Índice
1. Investigação e parâmetros do solo
2. Escolha do tipo de empuxo
3. Sobrecargas, água e drenagem
4. Estabilidade global do maciço
5. Verificações locais da contenção
6. Fórmulas para conferência rápida
7. Sinais de alerta
8. Sensibilidade, interação solo-estrutura, recalques e sismo
9. Rastreabilidade

## 1. Investigação e parâmetros do solo

Exigir no memorial:
- Relatório de sondagem (SPT, NBR 6484) com furos locados na planta e na região da contenção, perfil estratigráfico, nível d'água e data.
- Parâmetros de projeto: peso específico γ (kN/m³), ângulo de atrito efetivo φ' (°), coesão efetiva c' (kPa) e, se houver argila, resistência não drenada.
- Origem dos parâmetros: ensaio de laboratório (cisalhamento direto/triaxial) ou correlação com NSPT. Correlação é aceitável em fase de projeto básico, mas deve vir citada e com a literatura da correlação. Parâmetro "adotado" sem origem é pendência.
- Parâmetros diferentes por camada, caso o perfil seja estratificado. Uma única camada homogênea precisa ser justificada pela sondagem.
- Solo de aterro: compactação e parâmetros específicos, porque o aterro não herda os parâmetros do solo natural.

## 2. Escolha do tipo de empuxo

- **Ativo (Rankine ou Coulomb):** vale quando a estrutura pode se deslocar o suficiente para mobilizar a resistência do solo (muros de gravidade e de flexão livres, cortinas em balanço).
- **Repouso (K0):** vale quando a estrutura é rígida ou travada e não permite deformação (estruturas aporticadas com vigas e lajes travando a cortina, subsolos, contenções com múltiplos apoios). Dá empuxo maior que o ativo.
- **Passivo:** só pode ser contado com cautela, com redução e sem contar camadas superficiais sujeitas a escavação futura.

Pergunta para o projetista: por que o tipo escolhido é coerente com a rigidez e os deslocamentos admissíveis? Para estrutura de pilares, vigas e cortina travados, o empuxo ativo pode estar contra a segurança.

## 3. Sobrecargas, água e drenagem

- Sobrecarga a montante: veículos, edificações vizinhas, depósito de material, aterro adicional. Em prática urbana, valores de 10 a 20 kPa são comuns, mas o correto é derivar do uso real. Sobrecarga de piso de edificação (por exemplo 3 kPa) não representa terreno a montante.
- Água: nível d'água e cenário de chuva intensa. Contenção sem drenagem precisa dimensionar para empuxo hidrostático, o que muda muito a carga.
- Sistema de drenagem: dreno barbacã, geodreno, camada filtrante, dreno profundo, canaleta de crista, conexão com a drenagem pluvial. A ausência de drenagem é a causa mais comum de ruptura de contenções.

## 4. Estabilidade global do maciço

O parecer pede comprovar a estabilidade do maciço a montante. Isso exige:
- Seção(ões) crítica(s) com geometria, estratigrafia e posição da contenção.
- Método de equilíbrio limite declarado (Fellenius, Bishop simplificado, Janbu, Spencer ou Morgenstern-Price) ou análise por elementos finitos. Bishop e métodos rigorosos são preferidos para superfícies circulares e gerais.
- Busca da superfície crítica (não apenas uma superfície testada) e ilustração do resultado.
- Cenários: condição normal, saturada e com sobrecarga. Se o solo for coesivo, verificar curto e longo prazo.
- FS obtido comparado ao mínimo da NBR 11682 para o nível de segurança declarado (ver `normas.md`).
- Software e versão, arquivo de entrada ou dados suficientes para reproduzir.

Sem essa verificação, o documento não comprova estabilidade do maciço, mesmo que as seções de concreto passem.

## 5. Verificações locais da contenção

Conforme o tipo de estrutura:
- Tombamento, deslizamento na base e capacidade de carga do solo de apoio (muros de gravidade e de flexão).
- Ficha (embutimento) e momento fletor em cortinas em balanço.
- Ancoragens: carga de trabalho, comprimento livre e ancorado, ensaios (NBR 5629).
- Recalques e deslocamentos de topo compatíveis com construções e redes vizinhas.
- Fundação dos elementos que recebem o empuxo (sapata, estaca, tirante), incluindo tração e arrancamento quando o esforço normal é de tração.

## 6. Fórmulas para conferência rápida

Superfície do terreno horizontal e paramento vertical sem atrito:
- Ka = tan²(45° − φ'/2)
- K0 ≈ 1 − sen φ' (Jaky, solos granulares)
- Empuxo por metro de altura H: E = ½·K·γ·H² (triangular) + K·q·H (sobrecarga uniforme q)
- Ponto de aplicação: H/3 para o triângulo, H/2 para a sobrecarga
- Com c': desconto de 2·c'·√Ka na tensão ativa, aplicável com cautela (trinca de tração)
- Água: acrescentar ½·γw·hw², com γw ≈ 9,81 kN/m³

Conversões: 1 t ≈ 9,81 kN; 1 t/m² ≈ 9,81 kPa; 1 kgf/cm² ≈ 98,1 kPa.

Para comparar cargas pontuais de pilares com empuxo, converta-as em carga por metro: some as cargas horizontais por pilar, divida pelo espaçamento entre eixos e compare com E calculado. Use `scripts/empuxo_check.py`.

## 7. Sinais de alerta

- Cargas horizontais redondas e repetidas, sem origem declarada.
- Mesma carga em pilares de canto e de meio de vão, ou em faces com solicitações diferentes.
- Sobrecarga igual à de piso de edificação.
- Nenhuma menção a água, drenagem ou nível d'água.
- Sem sondagem ou parâmetros de solo no documento.
- "Passa" em todos os elementos, mas com taxas de utilização de 95% a 100% em vários pilares.
- Esforço normal negativo em pilar de fundação sem verificação de arrancamento.

## 8. Sensibilidade, interação solo-estrutura, recalques e sismo

**Sensibilidade às premissas.** Os parâmetros de solo têm incerteza grande, e a água muda o empuxo de forma não linear. Peça ao menos uma variação de φ' (por exemplo −3° a −5°), do nível d'água (com e sem saturação) e da sobrecarga, com o efeito no FS e nos esforços. Se um pequeno aumento de carga reprova elementos que já estão a 95–100%, o projeto não tem margem e o parecer deve registrar isso.

**Interação solo-estrutura e caminho de cargas.** O empuxo só chega à fundação passando por cortina, vigas, lajes e pilares. Verifique se o relatório descreve esse caminho: onde o empuxo é aplicado, quem o transmite, quem o resiste na base e como o conjunto é travado. A rigidez da estrutura decide entre empuxo ativo e de repouso (seção 2) e define se o modelo com cargas pontuais em pilares representa o comportamento real da cortina.

**Recalques.** Se a sondagem indicar argila mole ou aterro, peça estimativa de recalque (imediato e por adensamento) e verificação de compatibilidade com a estrutura e com construções vizinhas. Em solo granular compacto, a verificação costuma ser dispensável, mas a dispensa deve estar justificada.

**Sismo.** A sismicidade no Brasil é baixa, mas o relatório deve declarar a premissa (NBR 15421, a confirmar) e, se desconsiderar a ação sísmica, dizer por quê. Ausência total de menção é pendência de formalidade, não de cálculo.

## 9. Rastreabilidade

Todo resultado precisa poder ser reproduzido por terceiro. Exija:
- Versão e edição das normas usadas (por exemplo NBR 6118:2023).
- Software e versão, com arquivo de entrada ou dados que permitam repetir a análise.
- Lista das sondagens e ensaios usados, com identificação e data.
- Hipóteses e simplificações listadas, com o responsável técnico por cada decisão.
