from pathlib import Path
from typing import List, Optional, Union

import geopandas as gpd
from google.cloud.storage import Client


def copy_gcloud_storage_directories(
    gcloud_storage_client: Client,
    src_bucket: str,
    src_directory_path: str,
    target_bucket_name: str,
    target_directory_path: Optional[str] = None,
):
    bucket = gcloud_storage_client.get_bucket(src_bucket)
    target_bucket = gcloud_storage_client.get_bucket(target_bucket_name)
    blobs = bucket.list_blobs(prefix=src_directory_path)  # Get list of files
    for blob in blobs:
        bucket.copy_blob(
            blob, destination_bucket=target_bucket, new_name=target_directory_path
        )

    return True


def copy_geojson_files_to_cache(
    gcloud_storage_client: Client,
    source_bucket_name: str,
    target_bucket_name: str,
    taskdate: str,
):
    is_successful = copy_gcloud_storage_directories(
        gcloud_storage_client,
        source_bucket_name,
        f"ls_geometries/Panthera_tigris/canonical/{taskdate}/by_country",
        target_bucket_name,
    )

    return (
        copy_gcloud_storage_directories(
            gcloud_storage_client,
            source_bucket_name,
            f"ls_stats/Panthera_tigris/canonical/{taskdate}",
            target_bucket_name,
        )
        if is_successful
        else False
    )


def upload_shapefiles(gcloud_storage_client: Client, bucket, taskdate: str, shapefiles: List[Union[str, Path]]) -> bool: 
    ...


def sum_by_col(data_file_path: Union[Path, str], column_name: str) -> float:
    if Path(data_file_path).exists() is False:
        raise ValueError(f"Missing file [{data_file_path}]")
    df = gpd.read_file(data_file_path)

    countries = df.groupby("iso2").agg({column_name: "sum"}).to_dict("index")
    countries = {k: v[column_name] for k, v in countries.items()}
    countries["GLOBAL"] = df[column_name].sum()
    return countries


def parse_landscape_name(data_file_path: Union[Path, str]) -> str:
    return Path(data_file_path).stem[4:]


def get_countries_list(data_file_path: Union[Path, str]) -> list:
    df = gpd.read_file(data_file_path)
    countries = df["iso2"].unique().tolist()
    countries.append("GLOBAL")

    return countries


def find_landscape_name(lsid: int) -> Optional[str]:
    return "<TBD>"
