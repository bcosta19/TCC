"""Avaliador independente do OptFrame para quadros de horários.

O avaliador trabalha sobre CSVs normalizados ou instâncias JSON. As alocações
observadas podem ser usadas como baseline, sem que isso as transforme em
parâmetros fixos do problema.
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
        return sum(value for value in self.hard.values() if value is not None)

    @property
    def score(self) -> float:
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
        self.politica_cotutoria = self.turmas.attrs.get("politica_cotutoria", {})
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
    def _overlaps(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
        return max(start_a, start_b) < min(end_a, end_b)

    @staticmethod
    def _teachers_for_class(row) -> list[str]:
        if "professores_observados" in row and isinstance(row["professores_observados"], (list, set, tuple)):
            names = [str(p).strip() for p in row["professores_observados"] if str(p).strip()]
            if names:
                return names
        if "professores" in row and str(row["professores"]).strip():
            names = [str(p).strip() for p in str(row["professores"]).split(";") if str(p).strip()]
            if names:
                return names
        if "alocacao" in row and str(row["alocacao"]).strip():
            return [str(row["alocacao"]).strip()]
        return []

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
        t["professores_lista"] = t.apply(self._teachers_for_class, axis=1)

        h = self.horarios.copy()
        h["curso"] = h["turma_id"].map(t["curso"]).fillna("")
        h["periodo"] = h["turma_id"].map(t["periodo"]).fillna("")
        if "grupos_curriculares" in t.columns:
            h["grupos_curriculares"] = h["turma_id"].map(t["grupos_curriculares"])
        h["capacidade"] = h["turma_id"].map(t["capacidade"]).map(self._as_int)
        h["capacidade_sala"] = h["sala"].map(self.room_capacity)
        h["professores_lista"] = h["turma_id"].map(t["professores_lista"])

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

        all_observed_teachers = sorted({
            teacher
            for teachers in t["professores_lista"]
            for teacher in teachers
            if teacher
        })
        metadata = {
            "turmas": int(len(t)),
            "encontros": int(len(h)),
            "professores": int(len(all_observed_teachers)),
            "salas": int(h["sala"].replace("", pd.NA).dropna().nunique()),
            "laboratorios": sorted(room for room in self.room_capacity if is_lab_room(room)),
            "min_obrigatorias_ano": self.min_obrigatorias_ano,
        }
        return Evaluation(hard, soft, metadata)

    def _room_conflicts(self, h: pd.DataFrame) -> int:
        valid = h[h["sala"].fillna("").astype(str).ne("")]
        count = 0
        for (_, _, _), group in valid.groupby(["semestre", "dia", "sala"]):
            recs = group.to_dict("records")
            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    if recs[i]["turma_id"] != recs[j]["turma_id"] and self._overlaps(
                        recs[i]["inicio_min"], recs[i]["fim_min"],
                        recs[j]["inicio_min"], recs[j]["fim_min"]
                    ):
                        count += 1
        return count

    def _teacher_conflicts(self, h: pd.DataFrame) -> int:
        exploded = h.assign(professor=h["professores_lista"]).explode("professor")
        exploded["professor"] = exploded["professor"].fillna("").astype(str).str.strip()
        valid = exploded[exploded["professor"].ne("")]
        count = 0
        for (_, _, _), group in valid.groupby(["semestre", "dia", "professor"]):
            recs = group.to_dict("records")
            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    if recs[i]["turma_id"] != recs[j]["turma_id"] and self._overlaps(
                        recs[i]["inicio_min"], recs[i]["fim_min"],
                        recs[j]["inicio_min"], recs[j]["fim_min"]
                    ):
                        count += 1
        return count

    def _curriculum_conflicts(self, h: pd.DataFrame) -> int:
        valid = h.copy()
        if "grupos_curriculares" in valid.columns:
            def groups(value) -> list[str]:
                if isinstance(value, (list, set, tuple)):
                    return list(value)
                return [item for item in str(value or "").split(";") if item]

            valid["grupo"] = valid["grupos_curriculares"].map(groups)
            valid = valid.explode("grupo")
            valid = valid[valid["grupo"].fillna("").str.match(r"^(?:CC|SI)-P[1-8]$")]
        else:
            valid["grupo"] = valid["curso"].astype(str) + "|" + valid["periodo"].map(self._period_key).fillna("")
            valid = valid[valid["grupo"].str.endswith(("-P1", "-P2", "-P3", "-P4", "-P5", "-P6", "-P7", "-P8"))]

        valid = valid.drop_duplicates(["semestre", "grupo", "codigo", "dia", "inicio_min", "fim_min"])
        count = 0
        for (_, _, _), group in valid.groupby(["semestre", "grupo", "dia"]):
            recs = group.to_dict("records")
            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    if recs[i]["codigo"] != recs[j]["codigo"] and self._overlaps(
                        recs[i]["inicio_min"], recs[i]["fim_min"],
                        recs[j]["inicio_min"], recs[j]["fim_min"]
                    ):
                        count += 1
        return count

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
        exploded = h.assign(professor=h["professores_lista"]).explode("professor")
        exploded["professor"] = exploded["professor"].fillna("").astype(str).str.strip()
        valid = exploded[exploded["professor"].ne("")]
        count = 0
        for (_, _), group in valid.groupby(["semestre", "professor"]):
            daily = group.groupby("dia").agg(first=("inicio_min", "min"), last=("fim_min", "max"))
            ordered = sorted(daily.iterrows(), key=lambda item: DAY_ORDER.get(item[0], 99))
            for (_, current), (_, following) in zip(ordered, ordered[1:]):
                if following["first"] + 24 * 60 - current["last"] < min_rest_hours * 60:
                    count += 1
        return count

    def _working_days(self, h: pd.DataFrame) -> int:
        exploded = h.assign(professor=h["professores_lista"]).explode("professor")
        exploded["professor"] = exploded["professor"].fillna("").astype(str).str.strip()
        valid = exploded[exploded["professor"].ne("")]
        return int(valid.groupby(["semestre", "professor", "dia"]).ngroups)

    def _windows(self, h: pd.DataFrame) -> int:
        exploded = h.assign(professor=h["professores_lista"]).explode("professor")
        exploded["professor"] = exploded["professor"].fillna("").astype(str).str.strip()
        valid = exploded[exploded["professor"].ne("")]
        total = 0
        for _, group in valid.groupby(["semestre", "professor", "dia"]):
            slots = group[["inicio_min", "fim_min"]].drop_duplicates().sort_values("inicio_min")
            if len(slots) < 2:
                continue
            merged_intervals = []
            for _, row in slots.iterrows():
                start, end = int(row["inicio_min"]), int(row["fim_min"])
                if not merged_intervals:
                    merged_intervals.append([start, end])
                else:
                    if start <= merged_intervals[-1][1]:
                        merged_intervals[-1][1] = max(merged_intervals[-1][1], end)
                    else:
                        merged_intervals.append([start, end])
            for curr, foll in zip(merged_intervals, merged_intervals[1:]):
                gap = foll[0] - curr[1]
                total += max(0, gap // 120)
        return int(total)

    def _rotation_penalty(self, t: pd.DataFrame) -> int:
        pairs = t[t["codigo"].notna()].copy()
        pairs["ano"] = pairs["semestre"].astype(str).str.extract(r"^(\d{4})-", expand=False).fillna("")
        total = 0
        for (_, _, _), group in pairs.groupby(["ano", "curso", "codigo"], dropna=False):
            impar_group = group[group["semestre"].astype(str).str.endswith("-1")]
            par_group = group[group["semestre"].astype(str).str.endswith("-2")]
            impar_profs = {p for profs in impar_group["professores_lista"] for p in profs if p}
            par_profs = {p for profs in par_group["professores_lista"] for p in profs if p}
            if impar_profs and par_profs and (impar_profs & par_profs):
                total += len(impar_profs & par_profs)
        return total

    def _annual_load_violations(self, t: pd.DataFrame) -> int | None:
        """Conta professores do IC abaixo do mínimo anual de obrigatórias."""
        if "origem" in t.columns:
            internal = t[t["origem"].astype(str).eq("IC")].copy()
        else:
            internal = t[t["codigo"].astype(str).str.startswith("TCC")].copy()

        if "obrigatoria" in internal.columns:
            internal["is_ob"] = internal["obrigatoria"].map(self._as_bool).fillna(False)
        elif "ch_ob" in internal.columns:
            internal["is_ob"] = pd.to_numeric(internal["ch_ob"], errors="coerce").fillna(0).gt(0)
        else:
            return 0

        obligatory_classes = internal[internal["is_ob"]].copy()
        has_multiple_teachers = any(len(profs) > 1 for profs in obligatory_classes["professores_lista"])

        policy_map = self.politica_cotutoria if isinstance(self.politica_cotutoria, dict) else {}
        teacher_counts: dict[str, float] = defaultdict(float)

        for row in obligatory_classes.itertuples():
            profs = getattr(row, "professores_lista", [])
            if not profs:
                continue
            if len(profs) == 1:
                teacher_counts[profs[0]] += 1.0
            else:
                policy_entry = policy_map.get(getattr(row, "id", "")) or policy_map.get(getattr(row, "turma_id", "")) or {}
                policy_name = policy_entry.get("politica_h12") if isinstance(policy_entry, dict) else str(policy_entry or "")
                policy_name = str(policy_name or "").strip()
                if not policy_name:
                    # Sem política definida para a cotutoria, H12 fica indisponível
                    return None
                if policy_name == "integral_para_cada_docente":
                    for p in profs:
                        teacher_counts[p] += 1.0
                elif policy_name == "fracionada":
                    share = 1.0 / len(profs)
                    for p in profs:
                        teacher_counts[p] += share
                elif policy_name == "contar_para_um_responsavel":
                    resp = policy_entry.get("professor_responsavel") if isinstance(policy_entry, dict) else None
                    if resp and resp in profs:
                        teacher_counts[resp] += 1.0
                    else:
                        return None
                elif policy_name == "nao_contabilizar_em_h12":
                    pass
                else:
                    return None

        teacher_universe = self.turmas.attrs.get("professores_ic", [])
        if teacher_universe:
            universe_set = set(teacher_universe)
            for teacher in universe_set:
                teacher_counts.setdefault(teacher, 0.0)
            return sum(1 for teacher in universe_set if teacher_counts[teacher] < self.min_obrigatorias_ano)

        if not teacher_counts:
            return 0
        return sum(1 for count in teacher_counts.values() if count < self.min_obrigatorias_ano)

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


def evaluate_directory(
    directory: str | Path,
    profile: str = "cc_si",
    year: int | str = 2025,
) -> Evaluation:
    directory = Path(directory)
    year = str(year)
    turmas = pd.read_csv(directory / f"turmas_{year}.csv", dtype=str).fillna("")
    horarios = pd.read_csv(directory / f"horarios_{year}.csv", dtype=str).fillna("")
    rooms_path = directory / f"salas_{year}.csv"
    rooms = pd.read_csv(rooms_path, dtype=str).fillna("") if rooms_path.exists() else None
    if profile == "cc_si":
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


def evaluate_json(path: str | Path, allow_incomplete: bool = False) -> Evaluation:
    turmas, horarios, rooms = load_instance_json(path)
    if not allow_incomplete and turmas.attrs.get("pronta_para_experimento") is False:
        raise ValueError(
            "a instância está marcada com pronta_para_experimento=false; "
            "consulte a auditoria de dados antes de avaliá-la"
        )
    return QHEvaluator(turmas, horarios, rooms).evaluate()
