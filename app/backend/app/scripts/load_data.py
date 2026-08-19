from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.config import get_settings
from app.core.database import SessionLocal, create_tables
from app.core.utils import clean_value, mean_present, normalize_text, numeric_or_none, parse_range
from app.modules.implements.repository import ImplementRepository
from app.modules.implements.schemas import ImplementCreate
from app.modules.recommendations.repository import RecommendationRepository
from app.modules.tractors.repository import TractorRepository
from app.modules.tractors.schemas import TractorCreate


PESO_COLS = [
    "PESO_18_KG",
    "PESO_20_KG",
    "PESO_22_KG",
    "PESO_24_KG",
    "PESO_26_KG",
    "PESO_28_KG",
    "PESO_30_KG",
    "PESO_32_KG",
    "PESO_34_KG",
    "PESO_36_KG",
    "PESO_APROX_GERAL_KG",
]


def col(row: dict, name: str):
    return clean_value(row.get(name))


def normalize_implement_row(row: dict) -> ImplementCreate:
    largura = numeric_or_none(col(row, "LARGURA_TRABALHO_MM"))
    largura_min = numeric_or_none(col(row, "LARGURA_TRABALHO_MIN_MM"))
    largura_max = numeric_or_none(col(row, "LARGURA_TRABALHO_MAX_MM"))
    if largura is None:
        low, high, avg = parse_range(col(row, "LARGURA_TRABALHO_MM"))
        largura_min = largura_min or low
        largura_max = largura_max or high
        largura = avg

    prof_min, prof_max, prof_avg = parse_range(col(row, "PROFUNDIDADE_TRABALHO_MM"))
    pot_min, pot_max, pot_avg = parse_range(col(row, "POTENCIA_TRATOR_HP"))
    esteira_min, esteira_max, _ = parse_range(col(row, "POTENCIA_TRATOR_ESTEIRA_HP"))
    peso_medio = mean_present([col(row, peso_col) for peso_col in PESO_COLS])
    search_parts = [col(row, name) for name in ["GRUPO", "FAMILIA", "DESCRICAO", "MODELO", "DIAMETRO_DOS_DISCOS", "RODEIRO", "OBSERVACOES"]]

    return ImplementCreate(
        grupo=col(row, "GRUPO") or "",
        familia=col(row, "FAMILIA"),
        descricao=col(row, "DESCRICAO"),
        modelo=col(row, "MODELO"),
        n_discos=numeric_or_none(col(row, "N_DE_DISCOS")),
        n_hastes=numeric_or_none(col(row, "N_DE_HASTES")),
        largura_mm=largura,
        largura_min_mm=largura_min,
        largura_max_mm=largura_max,
        profundidade_min_mm=prof_min,
        profundidade_max_mm=prof_max,
        profundidade_media_mm=prof_avg,
        espacamento_mm=numeric_or_none(col(row, "ESPACAMENTO_MM")),
        diametro_dos_discos=col(row, "DIAMETRO_DOS_DISCOS"),
        peso_18_kg=numeric_or_none(col(row, "PESO_18_KG")),
        peso_20_kg=numeric_or_none(col(row, "PESO_20_KG")),
        peso_22_kg=numeric_or_none(col(row, "PESO_22_KG")),
        peso_24_kg=numeric_or_none(col(row, "PESO_24_KG")),
        peso_26_kg=numeric_or_none(col(row, "PESO_26_KG")),
        peso_28_kg=numeric_or_none(col(row, "PESO_28_KG")),
        peso_30_kg=numeric_or_none(col(row, "PESO_30_KG")),
        peso_32_kg=numeric_or_none(col(row, "PESO_32_KG")),
        peso_34_kg=numeric_or_none(col(row, "PESO_34_KG")),
        peso_36_kg=numeric_or_none(col(row, "PESO_36_KG")),
        peso_aprox_geral_kg=numeric_or_none(col(row, "PESO_APROX_GERAL_KG")),
        peso_medio_kg=peso_medio,
        potencia_min_hp=pot_min,
        potencia_max_hp=pot_max,
        potencia_media_hp=pot_avg,
        potencia_esteira_min_hp=esteira_min,
        potencia_esteira_max_hp=esteira_max,
        rodeiro=col(row, "RODEIRO"),
        fonte_imagem=col(row, "FONTE_IMAGEM"),
        observacoes=col(row, "OBSERVACOES"),
        search_text=normalize_text(" ".join([part for part in search_parts if part])),
    )


def normalize_tractor_row(row: dict) -> TractorCreate:
    name_column = next(iter(row.keys()))
    search_parts = [clean_value(row.get(name_column)), clean_value(row.get("TRACAO")), clean_value(row.get("TIPO"))]
    return TractorCreate(
        nome=clean_value(row.get(name_column)),
        potencia_hp=numeric_or_none(row.get("POTENCIA")),
        peso_kg=numeric_or_none(row.get("PESO")),
        tracao=clean_value(row.get("TRACAO")),
        tdp=clean_value(row.get("TDP")),
        tipo_transmissao=clean_value(row.get("TIPO")),
        search_text=normalize_text(" ".join([part for part in search_parts if part])),
    )


def load_data() -> dict:
    settings = get_settings()
    create_tables()
    arados = pd.read_excel(settings.ocr_dir / "extracao_arados.xlsx", sheet_name="Arados", dtype=object).to_dict("records")
    grades = pd.read_excel(settings.ocr_dir / "extracao_grades.xlsx", sheet_name="Grades", dtype=object).to_dict("records")
    tractors = pd.read_excel(settings.ocr_dir / "anuario.xlsx", dtype=object).to_dict("records")

    implement_rows = [normalize_implement_row(row) for row in [*arados, *grades]]
    tractor_rows = [normalize_tractor_row(row) for row in tractors]
    implement_rows = [row for row in implement_rows if row.grupo and row.modelo]
    tractor_rows = [row for row in tractor_rows if row.nome]

    with SessionLocal() as db:
        RecommendationRepository(db).delete_all()
        ImplementRepository(db).delete_all()
        TractorRepository(db).delete_all()
        implement_count = ImplementRepository(db).create_many(implement_rows)
        tractor_count = TractorRepository(db).create_many(tractor_rows)
        db.commit()

    return {"implements": implement_count, "tractors": tractor_count}


if __name__ == "__main__":
    print(load_data())

