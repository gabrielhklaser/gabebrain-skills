# Dissertação para artigo e acervo PPGCA

Leia ao converter a dissertação de mestrado (PPGCA/Unisinos) em artigo, ao redigir ou revisar seções para periódico ou conferência (Computers & Geosciences, Elsevier, IEEE, SBC, ACM, Springer) e quando precisar citar obras do acervo do programa.

Origem: tabela e seção de acervo trazidas da skill `escrita-tecnica-humanizada` (aposentada em 2026-11-15) e diretrizes acadêmicas que já estavam no `SKILL.md` da no-ai-slop.

## Mudança de gênero discursivo

O artigo não é uma tese condensada nem um resumo simplificado: apresenta uma contribuição técnica unificada e vertical.

| Elemento | Na dissertação | No artigo (conferência ou periódico) |
|:---|:---|:---|
| **Objetivo** | Demonstrar competência ampla e exaustiva | Apresentar uma única contribuição pontual e relevante |
| **Introdução** | 10 a 20 páginas de contexto histórico | 1 a 1,5 página: problema, lacunas, proposta, articulação dos resultados |
| **Referencial teórico** | Exaustivo, enciclopédico | Só o estado da arte diretamente confrontado |
| **Metodologia** | Cada detalhe procedimental | Arquitetura conceitual, axiomas formais e o essencial para reprodutibilidade |
| **Experimentos** | Vários estudos de caso e apêndices | O experimento mais contundente, com análise estatística adequada |
| **Extensão** | 80 a 150 páginas | 6 a 12 páginas (SBC, IEEE, ACM, Springer); confira o limite do periódico-alvo |

Corte a fundamentação genérica da dissertação e mantenha só as teorias que o artigo confronta.

## Diretrizes de redação

1. **Voz ativa com responsabilidade científica.** Em vez de "Foi implementado o classificador...", use "Implementamos o classificador..." ou "O pipeline processa...".
2. **Ritmo.** Alterne frases curtas e afirmativas com períodos analíticos mais longos; evite parágrafos de mesma forma em sequência.
3. **Densidade.** Se uma palavra sai sem mudar o sentido técnico, corte. Evite redundâncias como "análise analítica prévia", "planejamento futuro", "completamente otimizado".
4. **Precisão quantitativa.** Troque "o tempo de inferência diminuiu drasticamente" por "a latência de inferência caiu de 180 ms para 14 ms ($p < 0.01$)". Números só do texto ou dos dados do autor, nunca inventados.
5. **Formatação formal.** Axiomas em Description Logics ($C \sqsubseteq D$), equações em LaTeX/KaTeX, tabelas em Markdown e referências em BibTeX padronizado.
6. **Ancoragem conceitual** nos métodos do programa:
   - IHC / Engenharia Semiótica: notações semióticas (de Souza, 2005), comunicação designer-usuário, signos metalinguísticos, MIS, MAC, Cooper (2007).
   - Ontologias e Engenharia de Software: Description Logics, OWL-DL, NeOn, IEEE SWEBOK v4, SAP-TAM, Tellus-Onto (SBSI 2021), B-Track Onto (iSys 2024), CIE Framework (2024).
   - Machine Learning e redução de dimensionalidade: LAMP (Joia et al., 2011), NCA (Sinaice et al., 2021), Ribeiro (2019).

## Acervo do mestrado (PPGCA/Unisinos)

Antes de citar uma obra do programa, confira o trecho no acervo com a CLI local. O script fica no cofre e resolve o acervo (`Docling/`, `Fichas/`, `Indices/`) a partir da própria pasta: chame-o pelo caminho absoluto, não copie para cá.

```bash
CLI="C:/GabeBrain/GabeBrain/10-Trabalho/Computacao Aplicada/Scripts/busca_computacao_aplicada.py"
python "$CLI" buscar "LAMP" --limite 3      # busca lexical (--sessao, --regex)
python "$CLI" listar                        # catálogo (filtro: --sessao <nome>)
python "$CLI" ler "Joia" --inicio 1 --linhas 50
python "$CLI" ficha "Joia"
```

Para consulta mais ampla ao acervo, use a skill `computacao-aplicada` ou o subagente `ppgca-corpus`. Citação só com autor e ano conferidos no acervo; sem conferência, marque a lacuna em vez de completar.
