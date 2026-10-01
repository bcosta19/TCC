import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.build_official_instance_2026 import build, parse_classification


def meeting(day, start, end, room):
    return {"dia": day, "inicio": start, "fim": end, "sala": room}


BASE = {
    "rooms": [{"id": "202", "laboratorio": False}, {"id": "L1", "laboratorio": True}],
    "teachers": [],
    "classes": [
        {
            "id": "2026-1-TCC00001-A1", "semestre": "2026-1", "codigo": "TCC00001", "turma": "A1",
            "origem": "IC", "obrigatoria": True, "grupos_curriculares": ["CC-P1"],
            "professores_observados": ["Ana"], "capacidade_turma": 40,
            "encontros": [meeting("segunda", "07:00", "09:00", "202"), meeting("quarta", "07:00", "09:00", "202")],
        },
        {
            "id": "2026-1-TCC00002-A1", "semestre": "2026-1", "codigo": "TCC00002", "turma": "A1",
            "origem": "IC", "obrigatoria": None, "grupos_curriculares": [],
            "professores_observados": ["Ana", "Bia"], "capacidade_turma": 30,
            "encontros": [meeting("terca", "09:00", "11:00", "L1"), meeting("quinta", "09:00", "11:00", "202")],
        },
        {
            "id": "2026-1-GMA00001-A1", "semestre": "2026-1", "codigo": "GMA00001", "turma": "A1",
            "origem": "externa", "obrigatoria": True, "grupos_curriculares": ["CC-P1"],
            "professores_observados": ["Externo"], "capacidade_turma": 60,
            "encontros": [meeting("segunda", "09:00", "11:00", "202")],
        },
    ],
}


def complete_tables() -> dict[str, list[dict]]:
    return {
        "revisao_classificacao_curricular_2026.csv": [
            {"turma_id": "2026-1-TCC00002-A1", "codigo": "TCC00002", "decisao": "optativa:CC"},
        ],
        "politica_cotutoria_2026.csv": [
            {"turma_id": "2026-1-TCC00002-A1", "professores": "Ana;Bia",
             "politica_h12": "integral_para_cada_docente", "professor_responsavel": ""},
        ],
        "universo_h12_2026.csv": [
            {"nome_normalizado": "Ana", "incluido_h12": "nao"},
            {"nome_normalizado": "Bia", "incluido_h12": "nao"},
            {"nome_normalizado": "Caio", "incluido_h12": "nao"},
            {"nome_normalizado": "Externo", "incluido_h12": "nao"},
        ],
        "cadastro_salas_2026.csv": [
            {"sala": "202", "capacidade_fisica": "60", "recursos_oficiais": "projetor", "validado": "sim"},
            {"sala": "L1", "capacidade_fisica": "30", "recursos_oficiais": "", "validado": "sim"},
        ],
        "revisao_recursos_disciplinas_2026.csv": [
            {"codigo": "TCC00001", "alternou_tipo_de_sala": "False", "requer_laboratorio": "nao", "recursos_requeridos": "", "validado": "sim"},
            {"codigo": "TCC00002", "alternou_tipo_de_sala": "True", "requer_laboratorio": "sim", "recursos_requeridos": "", "validado": "sim"},
            {"codigo": "GMA00001", "alternou_tipo_de_sala": "False", "requer_laboratorio": "nao", "recursos_requeridos": "", "validado": "sim"},
        ],
        "revisao_horarios_fixos_2026.csv": [
            {"turma_id": "2026-1-TCC00001-A1", "horario_fixo": "nao", "validado": "sim"},
            {"turma_id": "2026-1-TCC00002-A1", "horario_fixo": "sim", "validado": "sim"},
            {"turma_id": "2026-1-GMA00001-A1", "horario_fixo": "sim", "validado": "sim"},
        ],
        "revisao_setores_2026.csv": [
            {"codigo": "TCC00001", "setor_oficial": "ALG", "dias_oficiais": "segunda;quarta;sexta", "validado": "sim"},
            {"codigo": "TCC00002", "setor_oficial": "ALG", "dias_oficiais": "", "validado": "sim"},
            {"codigo": "GMA00001", "setor_oficial": "EXTERNO", "dias_oficiais": "", "validado": "sim"},
        ],
        "revisao_habilitacao_docente_2026.csv": [
            {"codigo": "TCC00001", "docente": "Ana", "habilitado": "sim", "validado": "sim"},
            {"codigo": "TCC00001", "docente": "Caio", "habilitado": "sim", "validado": "sim"},
            {"codigo": "TCC00001", "docente": "Bia", "habilitado": "nao", "validado": "sim"},
            {"codigo": "TCC00002", "docente": "Ana", "habilitado": "sim", "validado": "sim"},
            {"codigo": "TCC00002", "docente": "Bia", "habilitado": "sim", "validado": "sim"},
        ],
        "revisao_prioridades_docentes_2026.csv": [
            {"nome_normalizado": name, "prioridade": "1.0", "validado": "sim"}
            for name in ("Ana", "Bia", "Caio", "Externo")
        ],
        "revisao_turmas_externas_2026.csv": [
            {"semestre": "2026-1", "codigo": "GMA00002", "disciplina": "CALCULO", "curso": "CC",
             "periodo_curricular": "CC-P1", "turma": "B1", "turma_url": "/x", "horarios": "Sex 07:00-09:00",
             "vinculada_ao_pdf": "False", "tratamento_no_modelo": "fixar_horario_e_sala"},
            {"semestre": "2026-1", "codigo": "GMA00003", "disciplina": "OUTRA", "curso": "SI",
             "periodo_curricular": "", "turma": "C1", "turma_url": "/y", "horarios": "Sex 09:00-11:00",
             "vinculada_ao_pdf": "False", "tratamento_no_modelo": "ignorar_fora_do_ic"},
        ],
    }


class BuildOfficialInstance2026Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        self.base = self.data / "base.json"
        self.base.write_text(json.dumps(BASE), encoding="utf-8")
        self.evidence = {"preferences": {"TCC00001": {"Caio": 2.0}}, "patterns": {}}

    def tearDown(self):
        self.tmp.cleanup()

    def write_tables(self, tables):
        for name, rows in tables.items():
            pd.DataFrame(rows).to_csv(self.data / name, index=False)

    def build(self, tables):
        self.write_tables(tables)
        return build(self.base, self.data, evidence=self.evidence)

    def classes(self, payload):
        return {item["id"]: item for item in payload["classes"]}

    def test_complete_reviews_produce_ready_instance(self):
        payload = self.build(complete_tables())
        self.assertEqual(payload["erros_validacao"], [])
        self.assertEqual(payload["pendencias_aplicacao"], {})
        self.assertTrue(payload["pronta_para_experimento"])

    def test_classification_and_cotutoria_are_applied(self):
        classes = self.classes(self.build(complete_tables()))
        optional = classes["2026-1-TCC00002-A1"]
        self.assertIs(optional["obrigatoria"], False)
        self.assertEqual(optional["grupos_curriculares"], [])
        self.assertTrue(optional["professor_fixo"])

    def test_flexible_class_uses_official_sector_days(self):
        payload = self.build(complete_tables())
        item = self.classes(payload)["2026-1-TCC00001-A1"]
        self.assertFalse(item["horario_fixo"])
        self.assertEqual(item["horario_dominio_fonte"], "dias_oficiais_do_setor")
        used_days = {meeting["dia"] for pattern in item["dominio_horarios"] for meeting in pattern}
        self.assertLessEqual(used_days, {"segunda", "quarta", "sexta"})
        self.assertIn(item["padrao_horario_observado"], item["dominio_horarios"])

    def test_qualification_defines_teacher_domain(self):
        item = self.classes(self.build(complete_tables()))["2026-1-TCC00001-A1"]
        self.assertEqual(item["professores_habilitados"], ["Ana", "Caio"])
        self.assertEqual(item["preferencias_professores"]["Caio"], 2.0)

    def test_lab_requirement_respects_alternating_rooms(self):
        item = self.classes(self.build(complete_tables()))["2026-1-TCC00002-A1"]
        self.assertEqual([m["requer_laboratorio"] for m in item["encontros"]], [True, False])

    def test_rooms_receive_official_capacity_and_resources(self):
        rooms = {room["id"]: room for room in self.build(complete_tables())["rooms"]}
        self.assertEqual(rooms["202"]["capacity"], 60)
        self.assertEqual(rooms["202"]["resources"], ["projetor"])
        self.assertTrue(rooms["L1"]["laboratorio"])

    def test_only_fixed_external_web_offers_enter_instance(self):
        classes = self.classes(self.build(complete_tables()))
        external = classes["2026-1-GMA00002-B1-WEB"]
        self.assertTrue(external["horario_fixo"])
        self.assertEqual(external["grupos_curriculares"], ["CC-P1"])
        self.assertNotIn("2026-1-GMA00003-C1-WEB", classes)

    def test_unvalidated_rows_stay_pending_without_proxy(self):
        tables = complete_tables()
        tables["cadastro_salas_2026.csv"][0]["validado"] = ""
        tables["revisao_horarios_fixos_2026.csv"][0]["validado"] = ""
        payload = self.build(tables)
        self.assertFalse(payload["pronta_para_experimento"])
        self.assertIn("capacidade_sala", payload["pendencias_aplicacao"])
        self.assertIn("horario_fixo", payload["pendencias_aplicacao"])
        room = next(room for room in payload["rooms"] if room["id"] == "202")
        self.assertIsNone(room["capacity"])
        self.assertTrue(self.classes(payload)["2026-1-TCC00001-A1"]["horario_fixo"])

    def test_ignored_class_is_removed(self):
        tables = complete_tables()
        tables["revisao_classificacao_curricular_2026.csv"][0]["decisao"] = "ignorar"
        self.assertNotIn("2026-1-TCC00002-A1", self.classes(self.build(tables)))

    def test_parse_classification(self):
        self.assertEqual(parse_classification("obrigatoria:SI-P7"), ("obrigatoria", True, ["SI-P7"]))
        self.assertEqual(parse_classification("optativa:SI"), ("optativa", False, []))
        with self.assertRaises(ValueError):
            parse_classification("obrigatoria:SI")


if __name__ == "__main__":
    unittest.main()
