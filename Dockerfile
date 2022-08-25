FROM scl3/task_base:latest

RUN apt-get update
RUN apt-get install -y gdal-bin libgdal-dev

RUN /usr/local/bin/python -m pip install --no-cache-dir \
    git+https://github.com/SpeciesConservationLandscapes/task_base.git \
    pandas==1.4.3 \
    geopandas==0.11.0 \
    psycopg2==2.9.3

WORKDIR /app
COPY $PWD/src .