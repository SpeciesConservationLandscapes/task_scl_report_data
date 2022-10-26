from datetime import date
from pathlib import Path
from typing import Dict, Union

from report_data import sum_by_col


def generate(
    taskdate: Union[date, str], data_dir_path: Union[Path, str]
) -> Dict[str, float]:
    column_name = "eff_pot_hab_area"

    species_conservation_landscape_occupieds = sum_by_col(
        Path(data_dir_path, "scl_species.geojson"), "occupied_eff_pot_hab_area"
    )
    species_fragments = sum_by_col(
        Path(data_dir_path, "scl_species_fragment.geojson"), column_name
    )
    survey_landscapes = sum_by_col(
        Path(data_dir_path, "scl_survey.geojson"), column_name
    )
    survey_fragments = sum_by_col(
        Path(data_dir_path, "scl_survey_fragment.geojson"), column_name
    )
    restoration_landscapes = sum_by_col(
        Path(data_dir_path, "scl_restoration.geojson"), column_name
    )
    restoration_fragments = sum_by_col(
        Path(data_dir_path, "scl_restoration_fragment.geojson"), column_name
    )

    # Need to check all results to get a unique list of country iso codes
    country_isos = {k for k in species_conservation_landscape_occupieds.keys()}
    country_isos.update(species_fragments.keys())
    country_isos.update(survey_landscapes.keys())
    country_isos.update(survey_fragments.keys())
    country_isos.update(restoration_landscapes.keys())
    country_isos.update(restoration_fragments.keys())

    countries = {}
    for iso in country_isos:
        species_conservation_landscape_occupied = species_conservation_landscape_occupieds.get(iso) or 0.0
        species_fragment = species_fragments.get(iso) or 0.0
        survey_landscape = survey_landscapes.get(iso) or 0.0
        survey_fragment = survey_fragments.get(iso) or 0.0
        restoration_landscape = restoration_landscapes.get(iso) or 0.0
        restoration_fragment = restoration_fragments.get(iso) or 0.0

        total = (
            species_conservation_landscape_occupied
            + species_fragment
            + survey_landscape
            + survey_fragment
            + restoration_landscape
            + restoration_fragment
        )

        countries[iso] = {
            "analysis_date": str(taskdate),
            "species_conservation_landscape_occupied": species_conservation_landscape_occupied,
            "species_fragment": species_fragment,
            "survey_landscape": survey_landscape,
            "survey_fragment": survey_fragment,
            "restoration_landscape": restoration_landscape,
            "restoration_fragment": restoration_fragment,
            "total": total,
        }

    return countries