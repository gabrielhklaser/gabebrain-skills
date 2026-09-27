# No AI Slop - Checklist de Avaliação e Auditoria Científica (Eval)

Utilize este checklist após redigir ou auditar seções de artigos científicos e acadêmicos. Cada item deve ser avaliado como **APROVADO (Pass)** ou **REPROVADO (Fail)**. Se qualquer verificação falhar, corrija antes da entrega final.

---

## 1. Princípios de Redação e Autoria Humana
- [ ] **Preservação da Voz do Pesquisador:** A edição preservou o tom, a terminologia e as hipóteses do autor sem pasteurizar ou impor um estilo corporativo genérico?
- [ ] **Sem Fabricação de Dados:** Nenhum número, autor, citação, métrica ou afirmação foi inventada?
- [ ] **Mínimo Corte Eficaz:** Frases humanas e autênticas foram mantidas sem simplificação excessiva?
- [ ] **Voz Ativa e Responsabilidade:** O texto declara com clareza quem tomou as decisões metodológicas e o que o algoritmo executa?
- [ ] **Teste de Portabilidade:** As frases de introdução, contribuição e conclusão são exclusivas desta pesquisa e não poderiam ser coladas em qualquer outro artigo?

---

## 2. Palavras e Expressões Banidas
- [ ] **Léxico de IA Eliminado:** *delve, tapestry, crucial, pivotal, beacon, game-changer, multifaceted, foster, leverage, utilize, streamline, robust, transformative, etc.*?
- [ ] **Muletas Acadêmicas Eliminadas:** *"Vale ressaltar que"*, *"Cabe destacar que"*, *"É importante notar que"*, *"It is worth noting that"*, *"No cenário contemporâneo"*, *"In today's fast-paced world"*?
- [ ] **Advérbios Vazios Cortados:** *fundamentally, truly, essentially, inherently, merely, simply*?

---

## 3. Os 20+ Padrões de Slop
- [ ] **Sem Contrastes Binários:** Sem *"It's not X. It's Y."* ou *"Não é apenas X, mas sim Y."*
- [ ] **Sem Throat-Clearing:** Abertura direta nos fatos sem preâmbulos dramáticos (*"Here's the thing"*, *"A grande questão é"*).
- [ ] **Sem Colon Reveals:** Sem o formato dramático *"O segredo: um modelo pré-treinado."*
- [ ] **Sem Análise Superficial (-ing clauses):** Sem gerúndios vazios ao final de frases (*"destacando a relevância..."*, *"underscoring the impact..."*).
- [ ] **Sem Puffery / Inflação:** Sem expressões grandiloquentes como *"serves as a testament"*, *"marca um divisor de águas"*, *"desempenha papel vital"*.
- [ ] **Sem Atribuição Doninha (Weasel Attribution):** Sem *"muitos autores apontam"*, *"estudos comprovam"* sem citar o autor e o ano formal.
- [ ] **Sem Enumeração Negativa:** Sem *"Não é X. Nem Y. É Z."*
- [ ] **Sem Ritmo Robótico:** Há variação natural de tamanho de frases (*burstiness* com desvio padrão > 4 palavras)?
- [ ] **Sem Fechamentos Filosóficos Falsos:** O artigo encerra com conclusões técnicas e trabalhos futuros, sem frases de efeito motivacional.
- [ ] **Sem Resumo Repetitivo Inicial:** Conclusão vai direto aos achados em vez de repetir a introdução com *"Em conclusão"*, *"Em suma"*.
- [ ] **Sem Poluição de Formatação:** Sem emojis, sem negritos teatrais no meio de sentenças, sem tópicos vazios.
- [ ] **Travessões Controlados (Em-dash):** No máximo 1 ou 2 por seção, preferindo vírgulas ou orações coordenadas.

---

## 4. Rigor Científico (Computação Aplicada)
- [ ] **Contribuição Unificada:** O artigo defende claramente uma contribuição pontual em vez de tentar resumir 100 páginas de dissertação.
- [ ] **Precisão de Métricas:** Valores numéricos de acurácia, F1-score, latência, tempo de treinamento e significância estatística ($p$-valor) estão explícitos.
- [ ] **Formalismo Conceitual:** Modelos formais (Ontologias OWL, Description Logics $C \sqsubseteq D$, tensores de projeção) estão corretamente expressos em KaTeX/LaTeX.
- [ ] **Relatório de Alterações:** O relatório final contém o bloco **"O que mudou" (What changed)** justificando cada corte para transparência do autor.
