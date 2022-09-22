from pathlib import Path
from typing import Dict, Optional, Union

import geopandas as gpd
from google.cloud.storage import Client


def _copy_gcloud_storage_directories(
    gcloud_storage_client: Client,
    src_bucket: str,
    src_directory_path: str,
    target_bucket_name: str,
    target_directory_path: Optional[str]=None,
):
    bucket = gcloud_storage_client.get_bucket(src_bucket)
    target_bucket = gcloud_storage_client.get_bucket(target_bucket_name)
    blobs = bucket.list_blobs(prefix=src_directory_path)  # Get list of files
    for blob in blobs:
        bucket.copy_blob(blob, destination_bucket=target_bucket, new_name=target_directory_path)
    
    return True

def copy_geojson_files_to_cache(gcloud_storage_client: Client, source_bucket_name: str, target_bucket_name: str, taskdate: str):
    is_successful = _copy_gcloud_storage_directories(
        gcloud_storage_client,
        source_bucket_name,
        f"ls_geometries/Panthera_tigris/canonical/{taskdate}/by_country",
        target_bucket_name
    )

    return _copy_gcloud_storage_directories(
        gcloud_storage_client,
        source_bucket_name,
        f"ls_stats/Panthera_tigris/canonical/{taskdate}",
        target_bucket_name
    ) if is_successful else False


def habitat_area_trends(data_file_path: str) -> dict:
    df = gpd.read_file(data_file_path)
    return df.agg(
        {
            "indigenous_range_area": "sum",
            "str_hab_area": "sum",
            "eff_pot_hab_area": "sum",
            "occupied_eff_pot_hab_area": "sum",
        }
    ).to_dict()


def _sum_by_col(data_file_path: Union[Path, str], column_name: str) -> float:
    if Path(data_file_path).exists() is False:
        raise ValueError(f"Missing file [{data_file_path}]")
    df = gpd.read_file(data_file_path)

    return df[column_name].sum()


def landscape_area_trends(data_dir_path: Union[Path, str]) -> Dict[str, float]:
    column_name = "connected_eff_pot_hab_area"
    species_conservation_landscape = _sum_by_col(Path(data_dir_path, "scl_species.geojson"), column_name)
    species_fragment = _sum_by_col(Path(data_dir_path, "scl_species_fragment.geojson"), column_name)
    survey_landscape = _sum_by_col(Path(data_dir_path, "scl_survey.geojson"), column_name)
    survey_fragment = _sum_by_col(Path(data_dir_path, "scl_survey_fragment.geojson"), column_name)
    restoration_landscape = _sum_by_col(Path(data_dir_path, "scl_restoration.geojson"), column_name)
    restoration_fragment = _sum_by_col(Path(data_dir_path, "scl_restoration_fragment.geojson"), column_name)

    total = (
        species_conservation_landscape +
        species_fragment +
        survey_landscape +
        survey_fragment +
        restoration_landscape +
        restoration_fragment
    )

    return {
        "species_conservation_landscape": species_conservation_landscape,
        "species_fragment": species_fragment,
        "survey_landscape": survey_landscape,
        "survey_fragment": survey_fragment,
        "restoration_landscape": restoration_landscape,
        "restoration_fragment": restoration_fragment,
        "total": total,
    }
