SCL Report Data
---------------

Read geojson files generated via [SCL Stats task](https://github.com/SpeciesConservationLandscapes/task_scl_stats) and create summary data for SCL website reports.

## Reports

**Excel based Reports:**

* Habitat area trends
* Landscape area trends
* Landscapes
* Species landscape by admin
* Species landscape by biome

**Web page reports:**

* Tiger Landscapes over time chart

## Environment Variables

```
# Service account needs read access to bucket
SERVICE_ACCOUNT_KEY=

# SCL API Database connection
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Database table to write report data
DB_REPORT_TABLE=report_data
```

## Database

Database table creation is managed via in [SpeciesConservationLandscapes/scl-api](https://github.com/SpeciesConservationLandscapes/scl-api).

For testing purposes, the table creation looks like:


```
CREATE TABLE IF NOT EXISTS report_data(
	id SERIAL PRIMARY KEY,
	task_date DATE,
  report VARCHAR(50),
	updated_on TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
	"data" JSONB,

	UNIQUE (task_date, report)
)
```

## Usage

```
usage: task.py [-h] [-d TASKDATE] [--geojson_files_dir GEOJSON_FILES_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -d TASKDATE, --taskdate TASKDATE
  --geojson_files_dir GEOJSON_FILES_DIR
                        Define alternative source of where geojson files are located.
```
