.PHONY: run superset

run:
	python3 0_dbs.py
	python3 1_scrap.py
	python3 2_geocode.py
	python3 3_locais.py
	python3 4_prepos.py
	python3 5_model.py

superset:
	superset run -p 8088 --with-threads --reload --debugger