from datetime import date
from pathlib import Path
from typing import Dict, Union

import geopandas as gpd

from report_data import (find_landscape_name, get_countries_list,
                         parse_landscape_name)


def generate(
    taskdate: Union[date, str], data_dir_path: Union[Path, str]
) -> Dict[str, dict]:
    data_file_names = [
        "scl_species.geojson",
        "scl_survey.geojson",
        "scl_restoration.geojson",
        "scl_species_fragment.geojson",
        "scl_survey_fragment.geojson",
        "scl_restoration_fragment.geojson",
    ]

    dataframes = [
        gpd.read_file(Path(data_dir_path, data_file_name))
        for data_file_name in data_file_names
    ]
    ls_types = [
        parse_landscape_name(data_file_name) for data_file_name in data_file_names
    ]

    countries = get_countries_list(Path(data_dir_path, data_file_names[0]))

    overall_results = {}
    for country in countries:
        results = []
        for src_df, ls_type in zip(dataframes, ls_types):
            df = src_df[src_df["iso2"] == country] if country != "GLOBAL" else src_df

            agg_params = {
                "lsid": "min",
                "str_hab_area": "sum",
                "eff_pot_hab_area": "sum",
                "occupied_eff_pot_hab_area": "sum",
                "kba_eff_pot_hab_area": "sum",
                "pa_eff_pot_hab_area": "sum",
            }

            data = df.groupby("lsid").agg(agg_params)
            data["analysis_date"] = str(taskdate)
            data["lstype"] = ls_type
            data["name"] = find_landscape_name(None)
            data["kba_percentage"] = (
                data["kba_eff_pot_hab_area"] / data["eff_pot_hab_area"]
            )
            data["protected_percentage"] = (
                data["pa_eff_pot_hab_area"] / data["eff_pot_hab_area"]
            )

            data["kba_percentage"].fillna(0, inplace=True)
            data["protected_percentage"].fillna(0, inplace=True)
            
            data.reset_index(drop = True, inplace = True)
            data.sort_values(by=["eff_pot_hab_area", "lsid"], ascending = [False, True], inplace=True)
            
            results.extend(data.to_dict("records"))

        overall_results[country] = results

    return overall_results
