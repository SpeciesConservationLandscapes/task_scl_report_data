import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple, Union

from report_data import find_landscape_name, get_countries_list, parse_landscape_name

BIOME_NAMES = [
    "Tropical & Subtropical Moist Broadleaf Forests",
    "Tropical & Subtropical Dry Broadleaf Forests",
    "Tropical & Subtropical Grasslands",
    "Savannas & Shrublands",
    "Tropical & Subtropical Coniferous Forests",
    "Mangroves",
    "Temperate Broadleaf & Mixed Forests",
    "Temperate Conifer Forests",
    "Flooded Grasslands & Savannas",
    "Montane Grasslands & Shrublands",
    "Boreal Forests/Taiga",
    "Deserts",
    "Xeric Shrublands",
]


def create_records(
    features: List[dict], analysis_date: str, landscape_type: str, country: str
) -> Tuple[dict, float]:
    data = {}
    total_areas = defaultdict(float)

    for feature in features:
        record = feature["properties"]
        iso2 = record.get("iso2")

        if country != "GLOBAL" and iso2 != country:
            continue

        lsid = record.get("lsid")
        eff_pot_hab_area = record.get("eff_pot_hab_area")
        if lsid not in data:
            data[lsid] = {
                "analysis_date": analysis_date,
                "lstype": landscape_type,
                "name": find_landscape_name(None),
                "lsid": lsid,
            }

        for biome in record["ecoregions"]:
            biome_name = biome["biome_name"]
            biome_eff_pot_hab_area = biome["eff_pot_hab_area"]
            if biome_name not in data[lsid]:
                data[lsid][biome_name] = biome_eff_pot_hab_area
            else:
                data[lsid][biome_name] += biome_eff_pot_hab_area

        total_areas[lsid] += eff_pot_hab_area

    return data, total_areas


def calc_biome_percentages(
    data: dict, total_areas: Dict[int, float], meta_columns: List[str]
) -> dict:
    result = {}
    sorted_lsids = sorted(data.keys())
    for lsid in sorted_lsids:
        record = data[lsid]
        ls_total_area = total_areas[lsid]
        if lsid not in result:
            result[lsid] = {}

        for meta_column in meta_columns:
            result[lsid][meta_column] = record[meta_column]

        for biome_name in BIOME_NAMES:
            if biome_name in record:
                result[lsid][biome_name] = (
                    record[biome_name] / ls_total_area if ls_total_area > 0 else 0.0
                )
            else:
                result[lsid][biome_name] = 0.0

    return result


def generate(
    taskdate: Union[date, str], data_file_path: Union[Path, str]
) -> Dict[str, list]:
    landscape_type = parse_landscape_name(data_file_path)
    analysis_date = str(taskdate)

    countries = get_countries_list(data_file_path)

    with open(data_file_path) as f:
        features = json.loads(f.read()).get("features")
    meta_columns = ("analysis_date", "lstype", "name", "lsid")

    overall_result = {}
    for country in countries:
        data, total_areas = create_records(
            features, analysis_date, landscape_type, country
        )
        result = calc_biome_percentages(data, total_areas, meta_columns)
        overall_result[country] = list(result.values())

    return overall_result
