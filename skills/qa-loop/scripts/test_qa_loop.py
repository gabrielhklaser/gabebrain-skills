"""Testes do qa-loop. Nenhuma chamada de rede: respostas do Jev sao simuladas."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import qa_loop as qa  # noqa: E402


def rnd(nota: float, veto: bool = False, pendente: bool = False) -> dict:
    return {"nota": nota, "veto": veto, "pendente": pendente}


# ------------------------------------------------------------ decide / loop

def test_aprova_quando_nota_alcanca_limiar_sem_veto() -> None:
    assert qa.decide([rnd(85)])["status"] == "APROVADO"


def test_veto_reprova_mesmo_com_nota_alta() -> None:
    assert qa.decide([rnd(99, veto=True)])["status"] == "REPROVADO"


def test_reprova_e_pede_nova_rodada_dentro_do_limite() -> None:
    d = qa.decide([rnd(60)])
    assert d["status"] == "REPROVADO" and d["proxima_iteracao"] == 2 and d["restantes"] == 2


def test_escala_ao_atingir_limite_de_iteracoes() -> None:
    d = qa.decide([rnd(50), rnd(60), rnd(70)], max_iter=3)
    assert d["status"] == "ESCALAR" and "limite" in d["motivo"]


def test_escala_por_estagnacao() -> None:
    d = qa.decide([rnd(60), rnd(61)], max_iter=5)
    assert d["status"] == "ESCALAR" and "estagnou" in d["motivo"]


def test_regressao_tambem_conta_como_estagnacao() -> None:
    assert qa.decide([rnd(70), rnd(55)], max_iter=5)["status"] == "ESCALAR"


def test_teto_absoluto_nao_pode_ser_burlado() -> None:
    historico = [rnd(10 + 10 * i) for i in range(qa.HARD_MAX_ITERATIONS)]
    assert qa.decide(historico, max_iter=999)["status"] == "ESCALAR"


def test_loop_sempre_termina_com_notas_arbitrarias() -> None:
    """Propriedade: nenhuma sequencia de notas abaixo do limiar produz reprovacao eterna."""
    historico: list[dict] = []
    for step in range(qa.HARD_MAX_ITERATIONS + 1):
        historico.append(rnd(40 + step * 5))
        if qa.decide(historico, max_iter=999)["status"] != "REPROVADO":
            return
    pytest.fail("o loop nao terminou dentro do teto absoluto")


def test_pendente_nao_conta_como_decisao() -> None:
    assert qa.decide([rnd(0, pendente=True)])["status"] == "PENDENTE_AGENTE"


def test_historico_vazio_e_erro() -> None:
    with pytest.raises(ValueError):
        qa.decide([])


# ------------------------------------------------------------------ gates

def test_gate_compile_detecta_erro_de_sintaxe(tmp_path: Path) -> None:
    ruim = tmp_path / "ruim.py"
    ruim.write_text("def f(:\n", encoding="utf-8")
    assert not qa.gate_compile(ruim).passed


def test_gate_json_invalido(tmp_path: Path) -> None:
    arq = tmp_path / "x.json"
    arq.write_text("{oops", encoding="utf-8")
    assert not qa.gate_json(arq).passed


def test_gate_segredo_detecta_token(tmp_path: Path) -> None:
    arq = tmp_path / "cfg.py"
    arq.write_text('API_KEY = "abcdefghijklmnop1234567890"\n', encoding="utf-8")
    assert not qa.gate_secrets(arq).passed


def test_gate_segredo_passa_em_codigo_limpo(tmp_path: Path) -> None:
    arq = tmp_path / "ok.py"
    arq.write_text("import os\nKEY = os.environ['TYPESAFE_API_KEY']\n", encoding="utf-8")
    assert qa.gate_secrets(arq).passed


def test_gate_testes_reflete_exit_code() -> None:
    assert qa.gate_tests(f'"{sys.executable}" -c "import sys; sys.exit(0)"').passed
    assert not qa.gate_tests(f'"{sys.executable}" -c "import sys; sys.exit(1)"').passed


def test_arquivo_inexistente_e_veto(tmp_path: Path) -> None:
    gates = qa.run_gates([tmp_path / "nao_existe.py"])
    assert gates[0].critical and not gates[0].passed


# ---------------------------------------------------------------- pontuacao

def jev_response(score: float, conf: float, veto_p: float = 0.05) -> dict:
    answers: dict = {pid: {"type": "score", "score": score, "confidence": conf}
                     for pid in ("funcionalidade", "robustez", "praticas", "aderencia")}
    answers["veto_segredo"] = {"type": "noul", "noul": veto_p}
    answers["veto_destrutivo"] = {"type": "noul", "noul": veto_p}
    return {"answers": answers, "cost_usd": 0.00001}


def test_pontuacao_maxima_soma_100() -> None:
    r = qa.score_with_jev(qa.load_rubric("dev"), jev_response(4.0, 0.9), {})
    assert r["nota"] == 100.0 and not r["vetos_jev"]


def test_pontuacao_meio_da_escala() -> None:
    assert qa.score_with_jev(qa.load_rubric("dev"), jev_response(2.0, 0.9), {})["nota"] == 50.0


def test_baixa_confianca_marca_pilar_incerto() -> None:
    r = qa.score_with_jev(qa.load_rubric("dev"), jev_response(4.0, 0.3), {})
    assert all(p["incerto"] for p in r["pilares"])


def test_override_do_agente_resolve_incerteza() -> None:
    overrides = {p: 1.0 for p in ("funcionalidade", "robustez", "praticas", "aderencia")}
    r = qa.score_with_jev(qa.load_rubric("dev"), jev_response(0.0, 0.1), overrides)
    assert r["nota"] == 100.0 and not any(p["incerto"] for p in r["pilares"])


def test_veto_do_jev_exige_probabilidade_alta() -> None:
    r = qa.score_with_jev(qa.load_rubric("dev"), jev_response(4.0, 0.9, veto_p=0.9), {})
    assert set(r["vetos_jev"]) == {"segredo", "destrutivo"}


def test_veto_ambiguo_vai_para_incertos_sem_vetar() -> None:
    r = qa.score_with_jev(qa.load_rubric("dev"), jev_response(4.0, 0.9, veto_p=0.5), {})
    assert not r["vetos_jev"] and r["vetos_incertos"]


def test_modo_privado_nao_envia_nada_ao_jev() -> None:
    r = qa.score_with_jev(qa.load_rubric("geo"), {"answers": {}}, {})
    assert r["nota"] == 0.0 and all(p["fonte"] == "ausente" for p in r["pilares"])


@pytest.mark.parametrize("nome", ["dev", "geo", "ciencia"])
def test_rubricas_validas(nome: str) -> None:
    rubric = qa.load_rubric(nome)
    questions = qa.build_questions(rubric)
    assert len(questions) == len(rubric["pilares"]) + len(rubric["vetos"])


def test_estado_trunca_artefato_grande() -> None:
    state = qa.build_state("spec", "x" * (qa.ARTIFACT_CHAR_LIMIT + 500), [])
    assert "truncado" in state


# --------------------------------------------------------------- validacao

def saida(**over: object) -> dict:
    base = {"nota_final": 90, "status": "APROVADO", "analise_breve": "ok", "feedbacks_de_correcao": []}
    return {**base, **over}


def test_saida_valida() -> None:
    assert qa.validate_output(saida()) == []


def test_reprovado_sem_feedback_e_invalido() -> None:
    assert qa.validate_output(saida(status="REPROVADO", nota_final=50))


def test_nota_fora_do_intervalo() -> None:
    assert qa.validate_output(saida(nota_final=101))


def test_campo_ausente() -> None:
    dado = saida()
    del dado["analise_breve"]
    assert qa.validate_output(dado)


# ------------------------------------------------- privacidade / classificacao

def test_detecta_dados_privados_localmente() -> None:
    assert "cpf" in qa.looks_private("CPF 123.456.789-09 do requerente")
    assert "email" in qa.looks_private("contato: fulano@empresa.com.br")
    assert "processo" in qa.looks_private("Processo nº 27964/2026")


def test_codigo_limpo_nao_e_privado() -> None:
    assert qa.looks_private("def f(x: int) -> int:\n    return x + 1\n") == []


def test_guarda_bloqueia_envio_de_material_privado() -> None:
    import argparse
    args = argparse.Namespace(privado=False, autorizado_privado=False)
    assert qa._may_send(args, "CPF 123.456.789-09") == (False, "agente (privado detectado)")
    assert qa._may_send(args, "codigo limpo") == (True, "jev")


def test_autorizacao_explicita_libera_envio() -> None:
    import argparse
    args = argparse.Namespace(privado=False, autorizado_privado=True)
    assert qa._may_send(args, "CPF 123.456.789-09")[0] is True


def test_flag_privado_sempre_bloqueia() -> None:
    import argparse
    args = argparse.Namespace(privado=True, autorizado_privado=True)
    assert qa._may_send(args, "qualquer coisa")[0] is False


def test_classify_confianca_alta() -> None:
    resp = {"answers": {"rubrica": {"choice": "geo", "confidence": 0.95},
                        "trivial": {"noul": 0.1}}}
    out = qa.classify_with_jev(resp)
    assert out["rubrica"] == "geo" and not out["trivial"]


def test_classify_baixa_confianca_deixa_para_o_agente() -> None:
    resp = {"answers": {"rubrica": {"choice": "geo", "confidence": 0.4}, "trivial": {"noul": 0.9}}}
    out = qa.classify_with_jev(resp)
    assert out["rubrica"] is None and out["rubrica_incerta"] and out["trivial"]
