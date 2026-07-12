install:
	python -m pip install -r requirements.txt

run:
	uvicorn app.main:create_app --host 0.0.0.0 --port 8002

test:
	pytest -q

fmt:
	python -m black .

lint:
	python -m flake8 .
