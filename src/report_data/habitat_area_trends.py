from datetime import date
from pathlib import Path
from typing import Union

import geopandas as gpd


def generate(
    taskdate: Union[date, str], data_file_path: Union[Path, str]
) -> dict:
    df = gpd.read_file(data_file_path)
    agg_params = {
        "indigenous_range_area": "sum",
        "str_hab_area": "sum",
        "eff_pot_hab_area": "sum",
        "occupied_eff_pot_hab_area": "sum",
    }

    countries = df.groupby("iso2").agg(agg_params).to_dict("index")
    countries["GLOBAL"] = df.agg(agg_params).to_dict()
    for country in countries:
        countries[country]["analysis_date"] = str(taskdate)

    return countries
