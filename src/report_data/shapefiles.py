import itertools
import subprocess
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, Union
from zipfile import ZipFile

from report_data import get_countries_list


SCL_STATES_SHP_FIELDS = (
    ("id", "id",),
    ("ENGTYPE_1", "ENGTYPE_1",),
    ("GID_1", "GID_1",),
    ("HASC_1", "HASC_1",),
    ("connected_eff_pot_hab_area", "ceph_area",),
    ("countrynam", "country",),
    ("eff_pot_hab_area", "eph_area",),
    ("gadm1code", "gadm1code",),
    ("gadm1name", "gadm1name",),
    ("indigenous_range_area", "ind_area",),
    ("iso2", "iso2",),
    ("iso3", "iso3",),
    ("isonumeric", "isonumeric",),
    ("occupied_eff_pot_hab_area", "oeph_area",),
    ("str_hab_area", "str_area",),
    ("total_area", "tot_area",),
)
SCL_LANDSCAPES_SHP_FIELDS = (
    ("id", "id",),
    ("connected_eff_pot_hab_area", "ceph_area",),
    ("country", "country",),
    ("eff_pot_hab_area", "eph_area",),
    ("gadm1code", "gadm1code",),
    ("indigenous_range_area", "ind_area",),
    ("iso2", "iso2",),
    ("isonumeric", "isonumeric",),
    ("kba_connected_eff_pot_hab_area", "kceph_area",),
    ("kba_eff_pot_hab_area", "keph_area",),
    ("kba_indigenous_range_area", "kind_area",),
    ("kba_occupied_eff_pot_hab_area", "koeph_area",),
    ("kba_str_hab_area", "kstr_area",),
    ("kba_total_area", "ktot_area",),
    ("ls_key", "ls_key",),
    ("lsid", "lsid",),
    ("occupied_eff_pot_hab_area", "oeph_area",),
    ("pa_connected_eff_pot_hab_area", "pceph_area",),
    ("pa_eff_pot_hab_area", "peph_area",),
    ("pa_indigenous_range_area", "pind_area",),
    ("pa_occupied_eff_pot_hab_area", "poeph_area",),
    ("pa_str_hab_area", "pstr_area",),
    ("pa_total_area", "ptot_area",),
    ("state", "state",),
    ("str_hab_area", "str_area",),
    ("total_area", "tot_area",),
)


def shell(cmd, *args):
    try:
        _cmd = [cmd, *args]
        subprocess.check_output(" ".join(_cmd), stderr=subprocess.STDOUT, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def create_country_shapefile(geojson_path, fields, country_iso=None):
    country_iso = country_iso or "GLOBAL"
    geojson_path = Path(geojson_path)
    dir_path = geojson_path.parent
    file_name = f"{geojson_path.stem}_{country_iso}.shp"
    output_path = Path(dir_path, file_name)

    field_renames = ",".join(f"{f[0]} AS {f[1]}" for f in fields)
    where = f" where iso2='{country_iso}'" if country_iso != "GLOBAL" else ""

    if shell(
        "ogr2ogr",
        "-of \"ESRI Shapefile\"",
        "-dialect \"sqlite\" "
        f"-sql \"select Geometry,{field_renames} from {geojson_path.stem}{where}\"",
        str(output_path),
        str(geojson_path)
    ):
        return output_path

    return None


def get_shapefile_paths(shapefile):
    extensions = [
        ".shp",
        ".shx",
        ".dbf",
        ".prj",
    ]
    shapefile_path = Path(shapefile)
    dir_path = shapefile_path.parent
    file_name = shapefile_path.stem
    return [Path(dir_path, f"{file_name}{ext}") for ext in extensions]


def zip_shapefiles(shapefiles):
    shapefile_path = Path(shapefiles[0])
    dir_path = shapefile_path.parent
    file_name = shapefile_path.stem
    zip_path = Path(dir_path, f"{file_name}.zip")
    with ZipFile(zip_path, "w") as zip:
        for file_path in shapefiles:
            name = Path(file_path).name
            zip.write(file_path, arcname=name)
    
    return zip_path
    

def generate_by_country(data_file_names, data_dir_path: Union[Path, str], country_iso: str):
    print(country_iso)

    shp_file_paths = []
    for data_file_name, fields in data_file_names:
        geojson_file_path = str(Path(data_dir_path, data_file_name))
        country_shapefile_path = create_country_shapefile(geojson_file_path, fields, country_iso)
        if country_shapefile_path is None:
            continue
        
        shp_file_paths.extend(get_shapefile_paths(country_shapefile_path))
    
    return zip_shapefiles(shp_file_paths)
    

def generate(
    taskdate: Union[date, str], data_dir_path: Union[Path, str]
) -> Dict[str, dict]:
    data_file_names = (
        ("scl_species.geojson", SCL_LANDSCAPES_SHP_FIELDS),
        ("scl_survey.geojson", SCL_LANDSCAPES_SHP_FIELDS),
        ("scl_restoration.geojson", SCL_LANDSCAPES_SHP_FIELDS),
        ("scl_species_fragment.geojson", SCL_LANDSCAPES_SHP_FIELDS),
        ("scl_survey_fragment.geojson", SCL_LANDSCAPES_SHP_FIELDS),
        ("scl_restoration_fragment.geojson", SCL_LANDSCAPES_SHP_FIELDS),
        ("scl_states.geojson", SCL_STATES_SHP_FIELDS),
    )

    _countries = []
    for geojson_path, _  in data_file_names:
        _countries.extend(get_countries_list(Path(data_dir_path, geojson_path)))
    
    country_isos = list(set(_countries))

    with ProcessPoolExecutor() as exc:
        return exc.map(generate_by_country, itertools.repeat(data_file_names), itertools.repeat(data_dir_path), country_isos)
