"""Avaliador independente do OptFrame para os quadros QH de 2025.

O avaliador trabalha diretamente sobre os CSVs produzidos por
``scripts/extract_qh_2025.py``. Ele avalia a solução real registrada na planilha;
posteriormente a mesma estrutura poderá avaliar soluções modificadas.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .rooms import is_lab_room
from .instance_io import load_instance_json
from .resources import infer_lab_requirement, lab_evidence_by_code


DAY_ORDER = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5}


@dataclass
class Evaluation:
    hard: dict
    soft: dict
    metadata: dict

    @property
    def hard_violations(self) -> int:
        return sum(self.hard.values())

    @property
    def score(self) -> float:
        # Nesta primeira versão, hard constraints têm prioridade lexicográfica.
        available_soft = [value for value in self.soft.values() if value is not None]
        return self.hard_violations * 1_000_000 + sum(available_soft)

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "hard_violations": self.hard_violations,
            "hard": self.hard,
            "soft": self.soft,
            "metadata": self.metadata,
        }


class QHEvaluator:
    def __init__(self, turmas: pd.DataFrame, horarios: pd.DataFrame, rooms: pd.DataFrame | None = None):
        self.turmas = turmas.copy()
        self.horarios = horarios.copy()
        self.min_obrigatorias_ano = int(self.turmas.attrs.get("min_obrigatorias_ano", 3))
        self.room_capacity = {}
        if rooms is not None and not rooms.empty and "id" in rooms and "capacidade_estimada" in rooms:
            self.room_capacity = dict(
                zip(rooms["id"].astype(str), pd.to_numeric(rooms["capacidade_estimada"], errors="coerce"))
            )
        self.horarios["inicio_min"] = self.horarios["inicio"].map(self._minute)
        self.horarios["fim_min"] = self.horarios["fim"].map(self._minute)
        self.horarios["slot"] = self.horarios.apply(
            lambda r: f"{r.semestre}|{r.dia}|{r.inicio}-{r.fim}", axis=1
        )

    @staticmethod
    def _minute(value: str) -> int:
        hour, minute = str(value).split(":")
        return int(hour) * 60 + int(minute)

    @staticmethod
    def _as_int(value) -> int | None:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _as_bool(value) -> bool | None:
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "sim", "yes"}:
            return True
        if normalized in {"false", "0", "nao", "não", "no"}:
            return False
        return None

    @staticmethod
    def _period_key(value: str) -> str | None:
        value = str(value).strip()
        if "-P" not in value:
            return None
        return value.split("-P", 1)[0] + "-P" + value.split("-P", 1)[1].split("-", 1)[0]

    def evaluate(self, min_rest_hours: int = 11, min_obrigatorias_ano: int | None = None) -> Evaluation:
        if min_obrigatorias_ano is not None:
            self.min_obrigatorias_ano = int(min_obrigatorias_ano)
        t = self.turmas.set_index("id", drop=False)
        h = self.horarios.copy()
        h["alocacao"] = h["turma_id"].map(t["alocacao"]).fillna("")
        h["curso"] = h["turma_id"].map(t["curso"]).fillna("")
        h["periodo"] = h["turma_id"].map(t["periodo"]).fillna("")
        h["capacidade"] = h["turma_id"].map(t["capacidade"]).map(self._as_int)
        h["capacidade_sala"] = h["sala"].map(self.room_capacity)
        if "requer_laboratorio" not in h.columns:
            h["requer_laboratorio"] = h["sala"].map(
                lambda room: is_lab_room(room) if str(room or "") else None
            )
        else:
            h["requer_laboratorio"] = h["requer_laboratorio"].map(self._as_bool)

        hard = {
            "conflitos_sala": self._room_conflicts(h),
            "conflitos_professor": self._teacher_conflicts(h),
            "conflitos_curriculares": self._curriculum_conflicts(h),
            "capacidade_insuficiente": self._capacity_violations(h),
            "recursos_incompativeis": self._resource_violations(h),
            "descanso_insuficiente": self._rest_violations(h, min_rest_hours),
            "carga_anual_insuficiente": self._annual_load_violations(t),
        }
        soft = {
            "dias_trabalhados": self._working_days(h),
            "janelas": self._windows(h),
            "desperdicio_capacidade": self._capacity_waste(h),
            "rodizio_semestre": self._rotation_penalty(t),
        }
        preference_score = self._preference_score(t)
        if preference_score is not None:
            soft["preferencia_priorizada"] = preference_score
        metadata = {
            "turmas": int(len(t)),
            "encontros": int(len(h)),
            "professores": int(t.loc[t["alocacao"].ne(""), "alocacao"].nunique()),
            "salas": int(h["sala"].replace("", pd.NA).dropna().nunique()),
            "laboratorios": sorted(room for room in self.room_capacity if is_lab_room(room)),
            "min_obrigatorias_ano": self.min_obrigatorias_ano,
        }
        return Evaluation(hard, soft, metadata)

    @staticmethod
    def _count_duplicate_groups(frame: pd.DataFrame, keys: list[str]) -> int:
        if frame.empty:
            return 0
        sizes = frame.groupby(keys, dropna=False).size()
        return int((sizes[sizes > 1] - 1).sum())

    def _room_conflicts(self, h: pd.DataFrame) -> int:
        valid = h[h["sala"].fillna("").ne("")]
        return self._count_duplicate_groups(valid, ["semestre", "dia", "inicio", "fim", "sala"])

    def _teacher_conflicts(self, h: pd.DataFrame) -> int:
        valid = h[h["alocacao"].fillna("").ne("")]
        return self._count_duplicate_groups(valid, ["semestre", "dia", "inicio", "fim", "alocacao"])

    def _curriculum_conflicts(self, h: pd.DataFrame) -> int:
        valid = h.copy()
        valid["grupo"] = valid["curso"].astype(str) + "|" + valid["periodo"].map(self._period_key).fillna("")
        valid = valid[valid["grupo"].str.endswith(("-P1", "-P2", "-P3", "-P4", "-P5", "-P6", "-P7", "-P8"))]
        # Turmas paralelas da mesma disciplina não geram conflito curricular:
        # o aluno escolhe uma seção. Primeiro reduzimos para disciplina distinta.
        valid = valid.drop_duplicates(["semestre", "grupo", "codigo", "dia", "inicio", "fim"])
        return self._count_duplicate_groups(valid, ["semestre", "grupo", "dia", "inicio", "fim"])

    def _capacity_violations(self, h: pd.DataFrame) -> int:
        values = h[["turma_id", "capacidade", "sala", "capacidade_sala"]].drop_duplicates()
        values = values.dropna(subset=["capacidade", "capacidade_sala"])
        return int((values["capacidade"] > values["capacidade_sala"]).sum())

    def _capacity_waste(self, h: pd.DataFrame) -> float:
        values = h[["turma_id", "capacidade", "sala", "capacidade_sala"]].drop_duplicates()
        values = values.dropna(subset=["capacidade", "capacidade_sala"])
        return float((values["capacidade_sala"] - values["capacidade"]).clip(lower=0).sum())

    def _resource_violations(self, h: pd.DataFrame) -> int:
        values = h[h["sala"].fillna("").ne("")].copy()
        values = values[values["requer_laboratorio"].notna()]
        if values.empty:
            return 0
        assigned_lab = values["sala"].map(is_lab_room)
        required_lab = values["requer_laboratorio"].astype(bool)
        return int((assigned_lab != required_lab).sum())

    def _rest_violations(self, h: pd.DataFrame, min_rest_hours: int) -> int:
        count = 0
        for (_, professor), group in h[h["alocacao"].ne("")].groupby(["semestre", "alocacao"]):
            daily = group.groupby("dia").agg(first=("inicio_min", "min"), last=("fim_min", "max"))
            ordered = sorted(daily.iterrows(), key=lambda item: DAY_ORDER.get(item[0], 99))
            for (_, current), (_, following) in zip(ordered, ordered[1:]):
                if following["first"] + 24 * 60 - current["last"] < min_rest_hours * 60:
                    count += 1
        return count

    def _working_days(self, h: pd.DataFrame) -> int:
        return int(h[h["alocacao"].ne("")].groupby(["semestre", "alocacao", "dia"]).ngroups)

    def _windows(self, h: pd.DataFrame) -> int:
        total = 0
        for _, group in h[h["alocacao"].ne("")].groupby(["semestre", "alocacao", "dia"]):
            slots = group[["inicio_min", "fim_min"]].drop_duplicates().sort_values("inicio_min")
            if len(slots) < 2:
                continue
            # Conta os intervalos de 2h vazios entre a primeira e a última aula.
            for (_, current), (_, following) in zip(slots.iterrows(), slots.iloc[1:].iterrows()):
                gap = int(following["inicio_min"] - current["fim_min"])
                total += max(0, gap // 120)
        return int(total)

    def _rotation_penalty(self, t: pd.DataFrame) -> int:
        pairs = t[t["codigo"].notna()].copy()
        pairs["alocacao"] = pairs["alocacao"].fillna("")
        total = 0
        for _, group in pairs.groupby(["curso", "codigo"], dropna=False):
            impar = group[group["semestre"].eq("2025-1")]["alocacao"].drop_duplicates().tolist()
            par = group[group["semestre"].eq("2025-2")]["alocacao"].drop_duplicates().tolist()
            if impar and par and impar[0] == par[0]:
                total += 1
        return total

    def _annual_load_violations(self, t: pd.DataFrame) -> int:
        """Conta professores do IC abaixo do mínimo anual de obrigatórias."""
        if "origem" in t.columns:
            internal = t[t["origem"].astype(str).eq("IC")].copy()
        else:
            internal = t[t["codigo"].astype(str).str.startswith("TCC")].copy()
        internal = internal[internal["alocacao"].fillna("").ne("")]
        if "obrigatoria" in internal.columns:
            obligatory = internal["obrigatoria"].map(self._as_bool).fillna(False)
        elif "ch_ob" in internal.columns:
            obligatory = pd.to_numeric(internal["ch_ob"], errors="coerce").fillna(0).gt(0)
        else:
            return 0
        counts = obligatory.groupby(internal["alocacao"]).sum()
        teacher_universe = self.turmas.attrs.get("professores_ic", [])
        if teacher_universe:
            counts = counts.reindex(sorted(set(teacher_universe)), fill_value=0)
        return int((counts < self.min_obrigatorias_ano).sum())

    def _preference_score(self, t: pd.DataFrame) -> float | None:
        """Retorna bônus negativo de preferência quando a instância o fornece."""
        required = {"preferencia", "prioridade", "alocacao"}
        if not required.issubset(t.columns):
            return None
        values = t.copy()
        if "origem" in values.columns:
            values = values[values["origem"].astype(str).eq("IC")]
        values["preferencia"] = pd.to_numeric(values["preferencia"], errors="coerce")
        values["prioridade"] = pd.to_numeric(values["prioridade"], errors="coerce")
        values = values[values["alocacao"].fillna("").ne("")]
        values = values.dropna(subset=["preferencia", "prioridade"])
        if values.empty:
            return None
        return float(-(values["preferencia"] * values["prioridade"]).sum())


def evaluate_directory(directory: str | Path, profile: str = "cc_si") -> Evaluation:
    directory = Path(directory)
    turmas = pd.read_csv(directory / "turmas_2025.csv", dtype=str).fillna("")
    horarios = pd.read_csv(directory / "horarios_2025.csv", dtype=str).fillna("")
    rooms_path = directory / "salas_2025.csv"
    rooms = pd.read_csv(rooms_path, dtype=str).fillna("") if rooms_path.exists() else None
    if profile == "cc_si":
        # O quadro geral também contém pós-graduação e outros cursos. Para a
        # instância-alvo, preservamos CC, SI e disciplinas externas que possuem
        # período curricular CC/SI explícito.
        keep = turmas["curso"].isin({"31", "83"}) | (
            turmas["curso"].eq("") & turmas["periodo"].str.startswith(("CC-", "SI-"))
        )
        turmas = turmas[keep].copy()
        horarios = horarios[horarios["turma_id"].isin(set(turmas["id"]))].copy()
        evidence = lab_evidence_by_code(horarios.to_dict("records"))
        horarios["requer_laboratorio"] = horarios.apply(
            lambda row: infer_lab_requirement(row["sala"], row["codigo"], evidence)[0],
            axis=1,
        )
    return QHEvaluator(turmas, horarios, rooms).evaluate()


def evaluate_json(path: str | Path) -> Evaluation:
    turmas, horarios, rooms = load_instance_json(path)
    return QHEvaluator(turmas, horarios, rooms).evaluate()
