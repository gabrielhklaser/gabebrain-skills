"""Testes do funil: python -m unittest test_funil (dentro de scripts/)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import funil as f

ITENS = [
    {"url": "https://www.exemplo.com/a?utm_source=x", "titulo": "Aquífero Guarani recarga", "views": 2_000_000,
     "data": "2025-03-01"},
    {"url": "https://exemplo.com/a/", "titulo": "Aquífero Guarani recarga (cópia)", "views": 1_500_000,
     "data": "2025-03-02"},
    {"url": "https://pinterest.com/p", "titulo": "Aquífero bonito", "views": 9_000_000, "data": "2025-01-01"},
    {"url": "https://blog.org/b", "titulo": "Recarga de aquífero", "views": 10, "data": "2025-02-01"},
    {"url": "https://site.net/c", "titulo": "Casino aquífero", "views": 5_000_000, "data": "2025-02-01"},
    {"url": "https://velho.net/d", "titulo": "Aquífero antigo", "views": 3_000_000, "data": "2019-01-01"},
    {"titulo": "Sem URL aquífero", "views": 3_000_000, "data": "2025-01-01"},
    {"url": "https://bom.net/e", "titulo": "Groundwater recharge", "views": "1.200.000", "data": "2025-05-01"},
]

REGRAS = {
    "campos_obrigatorios": ["url", "titulo"],
    "dedupe": "url",
    "dominios_bloqueados": ["pinterest.com"],
    "data": {"campo": "data", "desde": "2024-01-01"},
    "numeros": {"views": {"min": 1_000_000}},
    "palavras": {"campos": ["titulo"], "alguma": ["aquífero", "groundwater"], "nenhuma": ["casino"]},
    "ordenar": {"campo": "views", "desc": True},
    "limite": 10,
}


class NormalizacaoTests(unittest.TestCase):
    def test_url_normalizada_ignora_www_barra_e_rastreio(self):
        self.assertEqual(f.normalize_url("https://www.Exemplo.com/a/?utm_source=x&id=2"), "exemplo.com/a?id=2")
        self.assertEqual(f.normalize_url("http://exemplo.com/a"), "exemplo.com/a")

    def test_numero_aceita_formatos_brasileiros_e_texto(self):
        self.assertEqual(f.to_number("1.200.000"), 1_200_000)
        self.assertEqual(f.to_number("2,5"), 2.5)
        self.assertEqual(f.to_number(42), 42)
        self.assertIsNone(f.to_number("sem número"))

    def test_dominio_bloqueia_subdominio(self):
        self.assertTrue(f.domain_matches("https://br.pinterest.com/x", ["pinterest.com"]))
        self.assertFalse(f.domain_matches("https://notpinterest.com/x", ["pinterest.com"]))


class FiltroTests(unittest.TestCase):
    def test_funil_de_codigo_aplica_todas_as_regras(self):
        kept, report = f.apply_rules(ITENS, REGRAS)
        self.assertEqual([i["url"] for i in kept], ["https://www.exemplo.com/a?utm_source=x", "https://bom.net/e"])
        self.assertEqual(report["entrada"], 8)
        self.assertEqual(report["saida"], 2)
        self.assertEqual(report["cortes"], {
            "campos_obrigatorios": 1, "dominios_bloqueados": 1, "data": 1, "numeros.views": 1,
            "palavras.nenhuma": 1, "dedupe": 1,
        })

    def test_limite_corta_depois_de_ordenar(self):
        kept, report = f.apply_rules(ITENS, {**REGRAS, "limite": 1})
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["url"], "https://www.exemplo.com/a?utm_source=x")
        self.assertEqual(report["cortes"]["limite"], 1)

    def test_sem_regras_nada_e_cortado(self):
        kept, report = f.apply_rules(ITENS, {})
        self.assertEqual(len(kept), len(ITENS))
        self.assertEqual(report["cortes"], {})

    def test_dominios_permitidos_restringem(self):
        kept, _ = f.apply_rules(ITENS, {"dominios_permitidos": ["bom.net"]})
        self.assertEqual([i["url"] for i in kept], ["https://bom.net/e"])

    def test_palavras_todas_e_sem_acento(self):
        regras = {"palavras": {"campos": ["titulo"], "todas": ["aquifero", "recarga"]}}
        kept, _ = f.apply_rules(ITENS, regras)
        self.assertEqual(len(kept), 3)  # acentos e caixa nao importam

    def test_data_ate_e_data_invalida_cortam(self):
        itens = [{"data": "2025-01-10"}, {"data": "lixo"}, {"data": "2026-01-01"}]
        kept, report = f.apply_rules(itens, {"data": {"campo": "data", "ate": "2025-12-31"}})
        self.assertEqual(kept, [{"data": "2025-01-10"}])
        self.assertEqual(report["cortes"]["data"], 2)

    def test_regra_desconhecida_falha_alto(self):
        with self.assertRaises(ValueError):
            f.apply_rules(ITENS, {"limte": 5})


class JevTests(unittest.TestCase):
    def _jev(self, probs):
        jev = MagicMock()
        jev.load_key.return_value = "chave-de-teste"
        jev.ENDPOINT, jev.MODEL = "http://x", "jev-latest"
        respostas = iter({"answers": {"relevante": {"noul": p}}, "usage": {}} for p in probs)
        return jev, (lambda *_a, **_k: next(respostas))

    def test_jev_aprova_descarta_e_marca_incertos(self):
        itens = [{"titulo": "a"}, {"titulo": "b"}, {"titulo": "c"}]
        jev, fake = self._jev([0.95, 0.10, 0.60])
        with patch.object(f, "load_jev", return_value=jev), patch.object(f, "ask_jev", side_effect=fake):
            kept, report = f.jev_triage(itens, "Trata de recarga de aquífero?", ["titulo"], threshold=0.7)
        self.assertEqual([i["titulo"] for i in kept], ["a", "c"])
        self.assertTrue(kept[1]["_funil_incerto"])
        self.assertNotIn("_funil_incerto", kept[0])
        self.assertEqual(report, {"entrada": 3, "aprovados": 1, "incertos": 1, "descartados": 1, "erros": 0})

    def test_jev_sem_chave_nao_descarta_nada(self):
        jev = MagicMock()
        jev.load_key.return_value = None
        with patch.object(f, "load_jev", return_value=jev):
            kept, report = f.jev_triage([{"titulo": "a"}], "pergunta?", ["titulo"])
        self.assertEqual(len(kept), 1)
        self.assertIn("indisponivel", report)


class CliTests(unittest.TestCase):
    def test_cli_le_jsonl_grava_saida_e_relatorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            entrada = tmp_path / "candidatos.jsonl"
            entrada.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in ITENS), encoding="utf-8")
            regras = tmp_path / "regras.json"
            regras.write_text(json.dumps(REGRAS), encoding="utf-8")
            saida = tmp_path / "aprovados.jsonl"
            code = f.main(["--entrada", str(entrada), "--regras", str(regras), "--saida", str(saida)])
            self.assertEqual(code, 0)
            linhas = saida.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(linhas), 2)
            relatorio = json.loads((tmp_path / "aprovados.relatorio.json").read_text(encoding="utf-8"))
            self.assertEqual(relatorio["codigo"]["saida"], 2)

    def test_cli_le_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "c.csv"
            entrada.write_text("url,titulo,views\nhttps://a.com,x,5\nhttps://b.com,y,500\n", encoding="utf-8")
            itens = f.read_items(entrada)
            kept, _ = f.apply_rules(itens, {"numeros": {"views": {"min": 100}}})
            self.assertEqual([i["url"] for i in kept], ["https://b.com"])


if __name__ == "__main__":
    unittest.main()
