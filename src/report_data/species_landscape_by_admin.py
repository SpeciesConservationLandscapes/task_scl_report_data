from datetime import date
from pathlib import Path
from typing import Dict, Union

import geopandas as gpd

from report_data import find_landscape_name, get_countries_list, parse_landscape_name


def generate(
    taskdate: Union[date, str], data_file_path: Union[Path, str]
) -> Dict[str, list]:
    landscape_type = parse_landscape_name(data_file_path)

    countries = get_countries_list(data_file_path)

    overall_results = {}
    for country in countries:
        df = gpd.read_file(data_file_path)
        if country != "GLOBAL":
            df = df[df["iso2"] == country]

        agg_params = {
            "eff_pot_hab_area": "sum",
        }

        result = df.groupby(["lsid", "country"]).agg(agg_params)
        ls_totals = df.groupby(["lsid"]).agg({"eff_pot_hab_area": "sum"})

        result = result.join(ls_totals, rsuffix="_totals")
        result["percent_landscape"] = (
            result["eff_pot_hab_area"] / result["eff_pot_hab_area_totals"]
        )
        result["percent_landscape"].fillna(0, inplace=True)

        result.drop(
            ["eff_pot_hab_area", "eff_pot_hab_area_totals"], axis=1, inplace=True
        )

        result = result.transpose().stack(0).reset_index()
        result.drop(["level_0"], axis=1, inplace=True)
        result.fillna(0, inplace=True)

        result["analysis_date"] = str(taskdate)
        result["lstype"] = landscape_type
        result["name"] = find_landscape_name(None)

        overall_results[country] = list(result.to_dict("index").values())

    return overall_results
