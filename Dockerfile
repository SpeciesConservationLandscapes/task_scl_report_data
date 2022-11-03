FROM scl3/task_base:latest

RUN apt-get update
RUN apt-get install -y wget gdal-bin libgdal-dev

RUN /usr/local/bin/python -m pip install --no-cache-dir \
    git+https://github.com/SpeciesConservationLandscapes/task_base.git \
    pandas==1.4.3 \
    geopandas==0.11.0 \
    psycopg2==2.9.3

RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /cloud_sql_proxy
RUN chmod +x /cloud_sql_proxy

WORKDIR /app
COPY $PWD/src .