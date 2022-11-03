import argparse
import json
import os
from pathlib import Path

import psycopg2
from google.cloud.storage import Client
from task_base import Task
from task_base.data_transfer import DataTransferMixin

from report_data import (copy_geojson_files_to_cache, habitat_area_trends, map_chart,
                         landscape_area_trends, landscapes,
                         shapefiles,
                         species_landscape_by_admin,
                         species_landscape_by_biome)

# 1. fetch geojson files based on taskdate
# 2. generate report data
# 3. write to postgres


class SCLReportData(Task, DataTransferMixin):
    SOURCE_DATA_BUCKET = "scl-pipeline"
    CACHE_BUCKET = "cache.speciescl.org"
    LANDSCAPE_STATS_BUCKET_PATH = "ls_stats/Panthera_tigris/canonical"
    DATA_FILE_NAMES = [
        "scl_restoration.geojson",
        "scl_restoration_fragment.geojson",
        "scl_species.geojson",
        "scl_species_fragment.geojson",
        "scl_states.geojson",
        "scl_survey.geojson",
        "scl_survey_fragment.geojson",
    ]
    service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")
    google_creds_path = "/.google_creds"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        creds_path = Path(self.google_creds_path)
        if creds_path.exists() is False:
            with open(creds_path, "w") as f:
                f.write(self.service_account_key)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_creds_path
        self.gcsclient = Client()
        self.geojson_files_dir = kwargs.get("geojson_files_dir")
        self.stdout = kwargs.get("stdout")

    def _insert_database(self, report, data):
        conn_string = (
            f"dbname={os.environ['DB_NAME']} "
            f"user={os.environ['DB_USER']} "
            f"password={os.environ['DB_PASSWORD']} "
            f"host={os.environ['DB_HOST']} "
            f"port={os.environ['DB_PORT']} "
        )

        sql = []
        for iso, country_data in data.items():
            task_date = self.taskdate
            country_data = json.dumps(country_data)

            sql.append(
                f"""
                INSERT INTO {os.environ["DB_REPORT_TABLE"]} ("task_date", "report", "country_iso", "data", "updated_on")
                    VALUES('{task_date}', '{report}', '{iso}' ,'{country_data}', now())
                    ON CONFLICT (task_date, report, country_iso) 
                    DO 
                    UPDATE SET data = '{country_data}', updated_on=now();
            """
            )

        with psycopg2.connect(conn_string) as conn:
            cursor = conn.cursor()
            cursor.execute("\n".join(sql))

    def check_inputs(self):
        super().check_inputs()

    def fetch_geojson_files(self):
        if self.geojson_files_dir:
            return {
                path.name: path.resolve()
                for path in Path(self.geojson_files_dir).rglob("*.geojson")
                if path.name in self.DATA_FILE_NAMES
            }

        blob_path = f"{self.LANDSCAPE_STATS_BUCKET_PATH}/{self.taskdate}"
        local_path = f"/tmp/{self.taskdate}"

        os.makedirs(local_path, exist_ok=True)
        data_file_paths = {}
        for data_file_name in self.DATA_FILE_NAMES:
            local_file_path = Path(local_path, data_file_name)
            blob_file_path = f"{blob_path}/{data_file_name}"
            data_file_paths[data_file_name] = self.download_from_cloudstorage(
                blob_file_path, local_file_path, self.SOURCE_DATA_BUCKET
            )

        return data_file_paths

    def create_report_data(self, geojson_file_paths):
        from timer import Timer

        with Timer("shapefiles"):
            shapefiles.generate(
                self.taskdate,
                Path(geojson_file_paths[self.DATA_FILE_NAMES[0]]).parent
            )
        return {}
        # with Timer("habitat_area_trends_data"):
        #     habitat_area_trends_data = habitat_area_trends.generate(
        #         self.taskdate, geojson_file_paths["scl_states.geojson"]
        #     )

        # with Timer("landscape_area_trends_data"):
        #     landscape_area_trends_data = landscape_area_trends.generate(
        #         self.taskdate, Path(geojson_file_paths[self.DATA_FILE_NAMES[0]]).parent
        #     )

        # with Timer("landscapes_data"):
        #     landscapes_data = landscapes.generate(
        #         self.taskdate, Path(geojson_file_paths[self.DATA_FILE_NAMES[0]]).parent
        #     )

        # with Timer("species_landscape_by_admin_data"):
        #     species_landscape_by_admin_data = species_landscape_by_admin.generate(
        #         self.taskdate, geojson_file_paths["scl_species.geojson"]
        #     )

        # with Timer("species_landscape_by_biome_data"):
        #     species_landscape_by_biome_data = species_landscape_by_biome.generate(
        #         self.taskdate, geojson_file_paths["scl_species.geojson"]
        #     )
        
        # with Timer("map_chart"):
        #     map_chart_data = map_chart.generate(
        #         self.taskdate, Path(geojson_file_paths[self.DATA_FILE_NAMES[0]]).parent
        #     )

        # return {
        #     "habitat_area_trends": habitat_area_trends_data,
        #     "landscape_area_trends": landscape_area_trends_data,
        #     "landscapes": landscapes_data,
        #     "species_landscape_by_admin": species_landscape_by_admin_data,
        #     "species_landscape_by_biome": species_landscape_by_biome_data,
        #     "map_chart": map_chart_data,
        # }

    def write_report_data_to_postgres(self, data):
        self._insert_database("habitat_area_trends", data["habitat_area_trends"])
        self._insert_database("landscape_area_trends", data["landscape_area_trends"])
        self._insert_database("landscapes", data["landscapes"])
        self._insert_database(
            "species_landscape_by_admin", data["species_landscape_by_admin"]
        )
        self._insert_database(
            "species_landscape_by_biome", data["species_landscape_by_biome"]
        )
        self._insert_database(
            "map_chart", data["map_chart"]
        )

    def print_report_data(self, data):
        print(json.dumps(data, indent=2))

    def calc(self):
        geojson_files = self.fetch_geojson_files()
        data = self.create_report_data(geojson_files)

        # if self.stdout:
        #     self.print_report_data(data)
        # else:
        #     self.write_report_data_to_postgres(data)

        # copy_geojson_files_to_cache(
        #     self.gcsclient, self.SOURCE_DATA_BUCKET, self.CACHE_BUCKET, self.taskdate
        # )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate")
    parser.add_argument(
        "--geojson_files_dir",
        help="Define alternative source of where geojson files are located.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print result to standard output.",
    )
    options = parser.parse_args()
    report_data_cache_task = SCLReportData(**vars(options))
    report_data_cache_task.run()
