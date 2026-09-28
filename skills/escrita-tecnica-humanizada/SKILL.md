---
name: escrita-tecnica-humanizada
description: >-
  Diretrizes de redação científica de alto impacto, eliminação de clichês sintéticos
  de IA (anti-AI slop) e destilação de dissertações de mestrado em artigos científicos
  para Computação Aplicada. Focado em voz ativa, autoridade técnica, ritmo variado e precisão.
allowed-tools:
  - read
  - write
---

# ✍️ Escrita Técnica Humanizada & Anti-AI Slop (Computação Aplicada)

Esta skill orienta os agentes na produção de texto acadêmico e técnico autêntico, denso e fluido, eliminando a linguagem genérica, monótona e artificial característica de modelos de linguagem não calibrados.

---

## 🚫 1. Filtro Anti-AI Slop: Clichês e Padrões Banidos

Modelos de IA costumam recorrer a muletas linguísticas previsíveis. Esta skill estabelece uma proibição rígida de tais padrões:

### Termos e Frases Proibidas:
- ❌ *"Delve"* / *"Mergulhar profundamente"*
- ❌ *"Tapestry"* / *"Mosaico complexo"*
- ❌ *"Crucial"* / *"Pivotal"* / *"Beacon"* / *"Game-changer"*
- ❌ *"Serves as a testament"* / *"É um testemunho de..."*
- ❌ *"It is important to note that"* / *"Vale ressaltar que"* / *"Cabe destacar que"* (Corte a muleta e vá direto ao fato)
- ❌ *"Moreover"* / *"Furthermore"* repetidos em quase todo parágrafo (Use conectivos lógicos naturais ou transições temáticas diretas)
- ❌ *"In summary, ..."* / *"In conclusion, ..."* iniciando parágrafos de síntese
- ❌ *"Sheds light on"* / *"Desvenda os segredos"*
- ❌ Tríades forçadas: Listas de exatamente três adjetivos ou verbos abstratos ("rápido, escalável e robusto").

---

## 🎼 2. Cadência, Ritmo e "Burstiness" (O Toque Humano)

Detectores e leitores humanos identificam textos sintéticos pela uniformidade do tamanho das frases (efeito metrônomo).
- **Variação Estrutural:** Intercale frases curtas e afirmativas com frases analíticas mais longas e ricas em subordinadas.
- **Voz Ativa e Autoria:** Prefira a voz ativa sempre que declarar uma decisão metodológica ("Adotamos o algoritmo LAMP..." ou "O pipeline calcula..." em vez de "Foi realizada a execução do...").
- **Densidade Informacional ("Cada palavra paga aluguel"):** Se uma palavra puder ser removida sem alterar o significado técnico, corte-a. Evite redundâncias como "análise analítica prévia", "planejamento futuro", "completamente otimizado".

---

## 🔄 3. Pipeline de Conversão: Dissertação de Mestrado ➡️ Artigo Científico

A transição de uma dissertação para um artigo não é um resumo simplificado; é uma **mudança de gênero discursivo**:

| Elemento | Na Dissertação (Tese) | No Artigo Científico (Conferência / Periódico) |
|:---|:---|:---|
| **Objetivo** | Demonstrar competência ampla e exaustiva | Apresentar uma **única contribuição pontual e relevante** |
| **Introdução** | 10 a 20 páginas de contexto histórico | 1 a 1.5 páginas: Problema $\to$ Gaps $\to$ Proposta $\to$ Articulação de Resultados |
| **Referencial Teórico** | Exaustivo, enciclopédico | Focado exclusivamente no estado da arte imediatamente confrontado |
| **Metodologia** | Cada detalhe procedimental | Arquitetura conceitual, axiomas formais e reprodutibilidade essencial |
| **Experimentos** | Múltiplos estudos de caso e apêndices | O experimento mais contundente com análise estatística robusta |
| **Extensão** | 80 a 150 páginas | 6 a 12 páginas (SBC, IEEE, ACM, Springer) |

---

## 📚 4. Ancoragem no Acervo do Mestrado PPGCA/Unisinos

Ao redigir seções do artigo em Computação Aplicada:
1. **Consulte o Acervo:** Use a CLI local `busca_computacao_aplicada.py` para buscar citações e trechos exatos de:
   - **Ontologias:** Tellus-Onto (SBSI 2021), B-Track Onto (iSys 2024), CIE Framework (2024), NeOn, OWL-DL.
   - **Machine Learning & Redução:** LAMP (Joia et al., 2011), NCA (Sinaice et al., 2021), Ribeiro (2019).
   - **Engenharia Semiótica / IHC:** Clarisse de Souza (2005), MIS, MAC, Cooper (2007).
   - **Engenharia de Software:** IEEE SWEBOK v4, SAP-TAM.
2. **Formatação Formal:** Expressar axiomas em notação Description Logics ($C \sqsubseteq D$), tensores matemáticos, equações KaTeX/LaTeX e tabelas em Markdown ou BibTeX padronizado.

---

## ⚡ 5. Script de Auditoria de Estilo: `anti_slop_audit.py`

Execute o linter estilístico para identificar clichês, calcular a variabilidade de frases e detectar muletas de linguagem:
```powershell
python "$HOME/.gemini/config/skills/escrita-tecnica-humanizada/scripts/anti_slop_audit.py" "caminho\artigo.md"
```
