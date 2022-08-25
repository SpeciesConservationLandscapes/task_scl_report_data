import geopandas as gpd


def habitat_area_trends(data_file_path: str):
    df = gpd.read_file(data_file_path)
    return df.agg(
        {
            "indigenous_range_area": "sum",
            "str_hab_area": "sum",
            "eff_pot_hab_area": "sum",
            "occupied_eff_pot_hab_area": "sum",
        }
    ).to_dict()
