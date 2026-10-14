---
name: revisao-memoria-calculo-contencao
description: Revisa memórias de cálculo e projetos de contenção, muros, cortinas, taludes e movimentação de terra contra um parecer técnico (PT) de licenciamento ambiental, com base nas NBRs de estabilidade de encostas, fundações, concreto e ações. Use sempre que o usuário pedir para conferir, auditar ou revisar memorial de dimensionamento geotécnico/estrutural, verificar se um relatório atende às exigências de um parecer técnico, checar empuxo, parâmetros de solo, fatores de segurança, estabilidade global, fundações ou armaduras de contenção, ou redigir exigências complementares para o empreendedor, mesmo que ele não cite as normas.
---

# Revisão de memória de cálculo de contenção

Objetivo: dizer, com evidência e referência de página, se uma memória de cálculo atende ao que um parecer técnico pediu e se os métodos são tecnicamente defensáveis. O revisor é o analista do órgão ambiental. Ele precisa de um resultado que possa virar texto de parecer, então cada conclusão deve apontar o que falta, onde foi procurado e qual norma sustenta a exigência.

## Princípios

- **Cobertura antes de mérito.** Primeiro verifique se cada item pedido no parecer aparece no documento. Só depois julgue os métodos. Um relatório correto, mas sobre outra coisa (por exemplo, só pilares quando o parecer pede estabilidade do maciço), não atende.
- **Não afirme norma de memória sem sinalizar.** Números de fatores de segurança, cobrimentos e limites mudam entre edições. Use os valores de `references/normas.md` como referência de trabalho e marque "confirmar na edição vigente" quando for citar no parecer.
- **Distinga fato de inferência.** "Não consta no documento" é fato (diga onde procurou). "Provavelmente o empuxo é ativo" é inferência (diga como chegou lá).
- **Aprovação do software não é estabilidade.** "Passa" em verificação de seção não prova que a contenção é estável. Ele só diz que a seção resiste aos esforços que o projetista informou.

## Fluxo

1. **Extrair o pedido.** Leia o parecer e liste cada exigência em itens verificáveis, com número do parecer anterior, data e prazo (ver `references/formato-saida.md` para o cálculo do prazo). Se o parecer remete a outro (por exemplo "conforme PT nº XXX"), diga que esse texto não foi visto, caso não tenha sido fornecido.
2. **Mapear o documento recebido.** Leia todas as páginas do relatório. Em PDFs longos, leia em blocos de até 20 páginas e monte um índice de seções antes de julgar. Anote responsável técnico, software, data, assinatura e ART.
3. **Cruzar pedido x entrega.** Classifique cada item como Atendido, Parcial, Pendente ou Não aplicável, com a evidência.
4. **Revisar a metodologia.** Percorra a lista do bloco seguinte. Use `references/solo-e-empuxo.md` para a parte geotécnica e `references/checklist-estrutural.md` para a estrutural.
5. **Fazer a conta de ordem de grandeza.** Rode `scripts/empuxo_check.py` para ver se as cargas horizontais declaradas são coerentes com algum empuxo plausível. O script não substitui o cálculo do projetista. Ele indica se vale questionar.
6. **Escrever a saída** no formato de `references/formato-saida.md`, fechando com a lista "critério de pronto" daquele arquivo.

## O que verificar na metodologia

Geotecnia (carregue `references/solo-e-empuxo.md`):
- Investigação do subsolo (SPT/NBR 6484, número e profundidade de sondagens) e parâmetros adotados: γ, φ', c', nível d'água.
- Tipo de empuxo (ativo, repouso, passivo) coerente com a deformabilidade da estrutura.
- Sobrecargas a montante (veículos, edificações, aterros) e drenagem.
- Sensibilidade a φ', nível d'água e sobrecarga; interação solo-estrutura e caminho de cargas; recalques se houver argila mole ou aterro; premissa sísmica declarada (seção 8 de `solo-e-empuxo.md`).
- Rastreabilidade: versão das normas, software e versão, sondagens usadas (seção 9 de `solo-e-empuxo.md`).
- Estabilidade global do maciço, com método declarado, superfície crítica, cenários (saturado, com sobrecarga) e fator de segurança mínimo conforme o nível de segurança da NBR 11682.
- Tombamento, deslizamento e capacidade de carga, quando a contenção é de gravidade ou em balanço.

Estrutura (carregue `references/checklist-estrutural.md`):
- Todos os elementos das pranchas aparecem no cálculo: vigas, lajes, cortinas, pilares, fundações.
- Ações e combinações (NBR 8681 / 6118), cargas horizontais justificadas pela geotecnia.
- Classe de agressividade, cobrimento, classe do concreto.
- Fundação: tensão admissível, tração/arrancamento, estaca ou sapata.
- ELS (fissuração, deslocamentos), estabilidade global, ancoragem e detalhamento.
- Margens de utilização muito altas (acima de cerca de 95%) merecem destaque, porque qualquer ajuste de carga reprova o elemento.

Formalidades:
- Identificação do processo e do interessado, responsável técnico com registro, ART/RRT, assinatura conforme exigido no parecer, nome e formato dos arquivos.

## Cuidados com a conclusão

- Não aprove nem reprove o projeto em termos absolutos. Aponte atendimento ao parecer e pendências técnicas. A responsabilidade técnica é do profissional habilitado do empreendedor.
- Se faltar documento-chave (pranchas, parecer anterior, sondagem), diga qual comparação não foi possível e peça o arquivo.
- Se os valores do relatório parecerem inconsistentes entre si (cargas idênticas em pilares de influência diferente, por exemplo), registre como questionamento ao projetista, sem presumir erro.
