IMAGE=scl3/task_scl_report_data


build:
	docker build --no-cache -t $(IMAGE) .


push:
	docker image push $(IMAGE)

test_run:
	docker run  --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --geojson_files_dir="/tmp/2020-01-01" --taskdate="2020-01-01"
	# docker run --network tcl_default  --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --geojson_files_dir=/tmp/2020-01-01 --taskdate="2020-01-01"

shell:
	docker run -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app -v `pwd`/.git:/app/.git $(IMAGE) bash

cleanup:
	isort `pwd`/src/*.py
	black `pwd`/src/*.py
	flake8 `pwd`/src/*.py
	mypy `pwd`/src/*.py

bulk:
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2001-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2002-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2003-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2004-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2005-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2006-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2007-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2008-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2009-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2010-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2011-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2012-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2013-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2014-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2015-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2016-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2017-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2018-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2019-01-01"
	docker run --network tcl_default --rm -it --env-file .env -v `pwd`/data:/tmp -v `pwd`/src:/app $(IMAGE) python task.py --taskdate="2020-01-01"
