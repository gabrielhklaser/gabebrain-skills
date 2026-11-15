# Exemplos de entrada e saída

Use estes exemplos para calibrar formato, intensidade e o que entra em `O que mudou`. Os textos são ilustrativos. Em todos, a versão editada só usa fatos que estavam no original.

## Editar: email informal para o time

**Pedido:** "Deixa esse email menos corporativo, mas mantém o tom leve."

**Entrada:**

> Oi, pessoal!
>
> Espero que estejam todos bem. Estou escrevendo para compartilhar uma atualização importante sobre o projeto do novo painel. Nesse sentido, gostaria de destacar que, após intensas discussões, chegamos a um marco crucial: a primeira versão está pronta para testes.
>
> Vale ressaltar que essa entrega não é apenas um passo técnico. É um reflexo do comprometimento e da sinergia de todo o time. Além disso, foram realizadas melhorias significativas na performance e na experiência do usuário.
>
> Peço que todos realizem os testes até sexta-feira e reportem eventuais problemas no canal #painel. Fico à disposição para quaisquer dúvidas.
>
> Abraços,
> Marina

**Saída:**

> Oi, pessoal!
>
> Depois das discussões, a primeira versão do novo painel está pronta para testes. Ela vem com melhorias de desempenho e na experiência de uso.
>
> Testem até sexta-feira e reportem qualquer problema no canal #painel. Qualquer dúvida, me chamem.
>
> Abraços,
> Marina
>
> ### O que mudou
>
> - Comecei pela notícia e cortei a abertura que só anunciava o assunto.
> - Removi "marco crucial", o contraste "não é apenas um passo técnico" e a "sinergia do time", que não acrescentavam informação.
> - Tirei os conectivos mecânicos ("Nesse sentido", "Vale ressaltar", "Além disso").
> - Mantive as melhorias sem acrescentar métricas, que não aparecem no original.

O que este exemplo mostra: a saudação, o "Abraços" e o tom leve são do autor e ficam. A frase sobre melhorias continua vaga porque especificar exigiria inventar; a lacuna vai para `O que mudou`, não para o texto.

## Reescrever: post de rede social

**Pedido:** "Reescreve esse post, tá com cara de ChatGPT."

**Entrada:**

> 🚀 Liderança não é sobre cargo. É sobre impacto.
>
> Ao longo dos anos, aprendi que o verdadeiro líder não é aquele que dá ordens, mas aquele que inspira. Não se trata de controlar. Trata-se de empoderar.
>
> Grandes líderes fazem três coisas: escutam, confiam e delegam.
>
> O resultado? Times mais engajados, mais produtivos e mais felizes.
>
> E você, o que acha? Concorda? Comenta aqui 👇
>
> #liderança #gestão #carreira

**Saída:**

> Aprendi, ao longo dos anos, que liderança tem a ver com o impacto de quem lidera, independentemente do cargo. Quem inspira e dá autonomia ao time escuta, confia e delega, em vez de se limitar a dar ordens e controlar. Isso deixa o time mais engajado, produtivo e feliz.
>
> #liderança #gestão #carreira
>
> ### O que mudou
>
> - Reescrevi em vez de editar: quase todas as frases eram contraste binário, pergunta autorrespondida ou frase de efeito, e não sobrava estrutura para aproveitar.
> - Mantive a afirmação central, a experiência em primeira pessoa e as três atitudes, que são do autor.
> - Cortei o emoji, a pergunta "O resultado?" e a chamada genérica para comentar; mantive a defesa de inspirar e dar autonomia ao time.
> - Mantive as opiniões do autor sem acrescentar exemplos, resultados ou experiências pessoais.

O que este exemplo mostra: reescrever não autoriza inventar um caso, uma métrica ou uma frase de impacto nova. As hashtags ficam porque são convenção da plataforma, não vício de escrita. A tríade "escuta, confia e delega" permanece porque é conteúdo do autor, não ritmo fabricado.

## Detectar: trecho de artigo

**Pedido:** "Esse texto parece IA? Não reescreve, só aponta."

**Entrada:**

> No cenário atual, a inteligência artificial vem transformando profundamente a forma como as empresas operam. Especialistas afirmam que a adoção dessas tecnologias representa um marco fundamental para a competitividade. Não se trata apenas de automatizar processos, mas de repensar modelos de negócio. Além disso, a IA possibilita ganhos significativos de eficiência, promovendo uma cultura de inovação. Em conclusão, o futuro é promissor para quem souber aproveitar essa jornada.

**Saída:**

> ### Padrões encontrados
>
> - **Abertura de contexto universal:** "No cenário atual, a inteligência artificial vem transformando profundamente a forma como as empresas operam". Comece pelo fato ou pela decisão específica do texto.
> - **Atribuição vaga e inflação de importância:** "Especialistas afirmam que a adoção dessas tecnologias representa um marco fundamental". Identifique a fonte se ela estiver disponível e descreva o efeito sustentado por ela; caso contrário, sinalize a falta de fonte sem inventá-la.
> - **Contraste binário mecânico:** "Não se trata apenas de automatizar processos, mas de repensar modelos de negócio". Apresente a automatização e a revisão dos modelos de negócio diretamente, preservando ambas as ideias.
> - **Análise superficial com gerúndio:** "promovendo uma cultura de inovação". Corte ou substitua por um efeito concreto presente no texto.
> - **Fecho genérico:** "Em conclusão, o futuro é promissor para quem souber aproveitar essa jornada". Termine no último fato ou próximo passo.
>
> Os padrões aparecem juntos, mas não permitem determinar quem escreveu o texto. O trecho contém afirmações amplas e atribuições sem fonte identificada; uma edição pode simplificá-las, sem confirmá-las nem inventar dados.

O que este exemplo mostra: cada achado tem nome, trecho exato e correção em uma frase. Não há porcentagem, veredito de autoria nem reescrita. O diagnóstico termina sem oferta automática de editar.

## Quando não há o que marcar

**Pedido:** "Detecte problemas de estilo, sem reescrever."

**Entrada:**

> Trocamos o banco de sessões do Redis para o Postgres em 14 de agosto. O motivo foi simples: a gente já tinha o Postgres rodando e o Redis só servia pra isso. Perdemos uns 3 ms por requisição, o que ninguém notou. Ganhamos um serviço a menos pra monitorar às 3 da manhã.

**Saída:**

> Não encontrei padrões relevantes. O texto tem fatos, datas, uma decisão explicada e a voz do autor ("a gente", "pra", "às 3 da manhã"). Os dois-pontos introduzem uma explicação real, não uma revelação.

O que este exemplo mostra: "pra", "a gente" e o humor seco são sinais de voz, não de problema. A skill não força mudanças para justificar a própria existência.
