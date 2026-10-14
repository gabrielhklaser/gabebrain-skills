# Formato da saída

Entregue em português, direto ao ponto, em dois níveis: um resumo que o analista lê em um minuto e o detalhe que ele pode conferir.

## Estrutura

1. **Conclusão em uma ou duas frases.** O documento atende, atende parcialmente ou não atende ao parecer, e por quê.
2. **Quadro pedido x entrega.** Uma linha por exigência do parecer:

| Exigência do parecer | Situação | Evidência (página/seção) |
|---|---|---|
| Memória de cálculo geotécnica/estrutural | Pendente / Parcial / Atendido | ... |

3. **Pendências técnicas**, agrupadas (geotecnia, estrutura, fundações, formalidades), cada uma com: o que falta, por que importa, norma de referência.
4. **O que está correto**, em poucas linhas, para o analista não repetir conferência.
5. **Limitações da análise**: documentos que não foram vistos (parecer anterior, pranchas, sondagem) e verificações que ficaram sem comparação.
6. **Prazo**, se o parecer fixar (ver abaixo).
7. Oferecer, no fim, a redação das exigências complementares para o próximo parecer.

## Critério de "pronto"

Para o analista poder fechar a pendência da memória de cálculo, o relatório precisa ter, no mínimo:
1. Identificação (processo, interessado, obra, responsável técnico com registro, ART/RRT) e assinatura conforme o parecer.
2. Sondagem e parâmetros de solo com origem declarada.
3. Empuxos e sobrecargas justificados, com tipo de empuxo coerente com a rigidez da estrutura.
4. Estabilidade global com método, cenários e FS comparado ao mínimo da NBR 11682.
5. Dimensionamento de todos os elementos das pranchas (inclusive fundação) em ELU e ELS.
6. Sensibilidade a φ', água e sobrecarga, ou justificativa para dispensá-la.
7. Rastreabilidade (normas, software, versão, arquivos de entrada) e premissa sísmica declarada.

Use esta lista como fechamento da saída: marque cada item como atendido ou pendente.

## Prazo

Contar os dias a partir da data indicada no parecer. Use `python3 -c "from datetime import date,timedelta; print(date(AAAA,M,D)+timedelta(days=N))"` e informe a data resultante com a base da contagem. Se o parecer disser "a contar dos N dias a partir da data do documento X", a base é a data do documento X, não a do parecer atual. Informe se o relatório foi entregue dentro do prazo, comparando a data de assinatura com a data limite.

## Texto de exigências complementares (quando pedido)

Escrever em tom de parecer técnico: impessoal, objetivo, uma exigência por item, com a norma citada pelo nome e sem número de item não conferido. Exemplo de padrão:

"Apresentar memorial de estabilidade global do maciço a montante, com parâmetros geotécnicos de projeto e sua origem (sondagem SPT conforme NBR 6484), método de análise, fator de segurança obtido para a superfície crítica e comparação com o mínimo estabelecido na NBR 11682 para o nível de segurança adotado."

Manter o formato dos arquivos que o parecer exige (nomeados conforme o conteúdo, PDF, assinados conforme o decreto citado).
