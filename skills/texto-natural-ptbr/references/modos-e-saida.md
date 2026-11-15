# Modos de uso e saída (detalhe)

Texto integral das seções "Modos de uso" e "Saída" do `SKILL.md` original (v1.9.0), movido para cá na instalação local. Leia quando houver amostra de voz, edição de arquivo, uso como etapa de outra tarefa, resposta numa conversa ou entrega longa. As regras de fidelidade do `SKILL.md` prevalecem.

## Editar

É o modo padrão para pedidos de edição. Faça a menor intervenção que resolva os problemas reais. Preserve a estrutura quando ela funciona; reorganize apenas onde a ordem dificultar a compreensão.

Em respostas numa conversa, comece pela resposta ou decisão e evite reconstruir o contexto já compartilhado. Só corte uma recapitulação quando esse contexto estiver disponível; preserve fatos novos, razões que mudam a decisão e informações necessárias para agir. Pedidos de explicação completa e documentos que precisam ser autônomos exigem o contexto correspondente.

## Reescrever

Use quando o usuário pedir reescrita ou quando reorganizar frases e parágrafos for necessário para cumprir a transformação solicitada. Preserve os fatos e as ressalvas, com as exceções de escopo explicitamente pedidas. Não use a generalidade do texto como licença para criar conteúdo.

## Detectar

Use em auditorias, diagnósticos ou perguntas como "parece IA?" sem pedido de edição. Para cada achado, cite o trecho exato, nomeie o padrão e explique o problema e o ajuste sugerido. Agrupe repetições e priorize os achados com efeito real na leitura, sem limite artificial que esconda problemas distintos.

Não reescreva o texto inteiro, não atribua autoria e não dê porcentagem de IA. Se a pergunta for sobre autoria, esclareça que estilo não permite determiná-la. Se não houver problemas relevantes, diga isso sem fabricar achados.

## Calibrar voz

Quando houver amostra própria, observe ritmo, vocabulário, pontuação, humor, formalidade e transições. Use apenas os traços observáveis e compatíveis com o pedido atual. Não copie fatos, relatos pessoais ou frases da amostra para o texto editado.

## Arquivo e uso embutido

Arquivo é o suporte, não um modo que substitui o pedido. Em "detecte problemas neste arquivo", apenas leia e relate. Em "edite este arquivo", grave a prosa revisada no arquivo indicado, preserve mudanças alheias e confira o diff antes de informar o resultado. Se o usuário pedir uma sugestão na conversa ou proibir alterações, não grave.

Se não conseguir gravar, diga isso e entregue a alternativa disponível; não afirme que atualizou o arquivo. Publicar ou enviar o texto depende de autorização no pedido, não desta skill.

No uso como etapa interna de outra tarefa, siga o contrato de saída dela; para edição embutida, devolva apenas o texto final.

## Saída

O formato solicitado pelo usuário vem primeiro. Se pedir "só o texto", omita comentários. Nos demais pedidos de editar ou reescrever, entregue o texto final completo e, quando houver mudanças, uma seção breve `O que mudou` com as alterações relevantes. Se houve reescrita, indique o motivo em uma linha. Não substitua trechos por "[...]". Se o volume exceder o canal, use um arquivo quando autorizado ou combine a entrega em partes; explicite qualquer trecho pendente.

No modo detectar, use `Padrões encontrados` com nome, citação e sugestão para cada padrão observado. Na edição de arquivo, informe apenas o que foi alterado e conferido, sem repetir o documento inteiro.

Comece pela entrega. Em continuações, informe apenas o estado ou insumo que importa para prosseguir; não imponha estimativas, listas com tamanho fixo ou próximos passos artificiais. Quando terminar, encerre sem convite automático para continuar.
