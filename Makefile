.PHONY: help install test generate run-pipeline dashboard docker-up docker-down clean

help:
	@echo "MarketShare-ETL Developer Commands:"
	@echo "  make install      Install Python dependencies"
	@echo "  make test         Execute full pytest test suite"
	@echo "  make generate     Generate 2019-2024 raw CSV market share feeds"
	@echo "  make run-pipeline Execute full ETL pipeline (Extract -> Transform -> Load)"
	@echo "  make dashboard    Launch Streamlit interactive analytics dashboard"
	@echo "  make docker-up    Spin up platform in Docker container"
	@echo "  make docker-down  Stop Docker container"
	@echo "  make clean        Clean temporary cache and pyc files"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests -v

generate:
	python scripts/generate_raw_csvs.py

run-pipeline:
	python scripts/run_pipeline.py

dashboard:
	streamlit run src/dashboard/app.py

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
