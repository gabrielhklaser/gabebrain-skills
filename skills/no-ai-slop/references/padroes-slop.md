# Os 20+ padrões de AI slop (catálogo de detecção)

Catálogo movido do `SKILL.md` da no-ai-slop em 2026-11-15; os padrões estão como eram, só esta abertura é nova. Leia antes de editar ou auditar no modo Detect.

Ressalva: um padrão conta quando aparece sem função ou se acumula com outros. Um travessão, um conectivo ou uma palavra da lista, sozinhos, não provam texto artificial nem autoria por IA.

1. **Contrastes Binários Falsos:** *“It’s not X. It’s Y.”* / *“Não se trata apenas de X, mas sim de Y.”*
   - *Correção:* Declare Y diretamente com foco na métrica ou no mecanismo.
2. **Aberturas Limpa-Garganta (Throat-Clearing):** *“Here’s the thing”*, *“Let me be clear”*, *“A verdade é que”*.
   - *Correção:* Elimine o preâmbulo e abra a frase no cerne técnico.
3. **Faux-Insight e Dramatização:** *“O que a maioria não percebe é...”*, *“What nobody tells you is...”*, *“A grande sacada:”*.
   - *Correção:* Corte a pose dramática; o mérito reside no resultado empírico.
4. **Colon Reveals (Dois Pontos com Revelação Teatral):** *“O diferencial da abordagem: um pipeline distribuído.”*
   - *Correção:* Transforme em oração contínua padrão: *“O pipeline distribuído assegura menor latência.”*
5. **Superficial Analysis (-ing Clauses Vazia):** Gerúndios que fingem inferir significado (*“destacando sua relevância”*, *“highlighting the need”*, *“underscoring the importance”*).
   - *Correção:* Indique a consequência técnica concreta ou o valor medido.
6. **Importance Puffery (Inflação de Relevância):** *“Stands as a testament”*, *“marca um momento divisor de águas”*, *“desempenha papel vital”*.
   - *Correção:* Exponha os números ou o caso de teste e deixe o leitor avaliar a significância.
7. **Interpretive Metadiscourse (Dizer ao leitor como interpretar):** *“Essa distinção é de suma importância”*, *“Como se pode observar claramente”*, *“Em outras palavras”*.
   - *Correção:* Se o dado é claro, corte o comentário. Se não for, complete com a evidência.
8. **Weasel Attribution (Atribuição Doninha / Sem Autoridade):** *“Especialistas apontam que...”*, *“Estudos demonstram que...”*, *“Industry consensus suggests”*.
   - *Correção:* Cite o autor e o ano formalmente (ex: `(Joia et al., 2011)` ou `(de Souza, 2005)`) ou corte a afirmação.
9. **Fake-Strong Verbs (Verbos Prolixos em vez de Diretos):** *“O framework atua como um facilitador do processo”* $\to$ *“O framework executa a validação”*.
10. **Synonym Cycling (Giro Artificial de Sinônimos):** Ficar trocando desnecessariamente termos técnicos definidos (ex: variar entre "sistema", "plataforma", "ferramenta", "solução", "artefato") apenas por medo de repetir a palavra exata. Em ciência, use o termo exato padronizado.
11. **Negative Listing (Enumeração Negativa):** *“Não é um algoritmo genético. Nem uma heurística gulosa. É uma projeção multidimensional.”* $\to$ *“O método emprega projeção multidimensional.”*
12. **Dramatic Fragmentation:** Frases deliberadamente quebradas para efeito retórico (*“Precisão. Rapidez. Escalabilidade. Isso é o LAMP.”*). Use orações completas e gramaticalmente coordenadas.
13. **Robotic Rhythm (Metrônomo de Parágrafos):** Parágrafos com exatamente três frases de mesmo tamanho. Quebre a monotonia alternando sentenças curtas e incisivas com períodos subordinados analíticos.
14. **Rhetorical Setups:** Perguntas retóricas direcionadas ao leitor (*“Como superar a alta dimensionalidade? A resposta é simples:”*). Em artigos acadêmicos, enuncie o problema e a solução metodológica.
15. **Fake-Profound Kickers:** Frases de efeito filosófico no encerramento (*“O futuro da IA não está por vir: ele já começou.”*). Corte sem piedade; encerre nas implicações práticas e limitações do estudo.
16. **Summary-Recap Endings:** Conclusões que iniciam repetindo textualmente tudo que foi dito com *"Em resumo"*, *"Concluindo"*, *"Em suma"*. Encerre nos achados e direcionamentos futuros concretos.
17. **Formatting Slop:** Emojis em títulos acadêmicos, negrito salpicado no meio de frases para ênfase teatral, tópicos curtos de duas palavras onde parágrafos argumentativos são exigidos.
18. **Em Dash Overload:** Excesso de travessões duplos (—) como muleta sintática. No máximo 1 ou 2 por seção quando estritamente superior a parênteses ou vírgula.
19. **Tríades Forçadas:** Listas previsíveis de 3 adjetivos vazios (*“eficiente, dinâmico e flexível”*).
20. **Portability Test (Teste de Portabilidade):** Se a frase puder ser transferida para qualquer outro artigo de computação sem precisar alterar nenhuma palavra, ela é puro enchimento (*filler*). Corte-a ou substitua por dados da sua pesquisa.
