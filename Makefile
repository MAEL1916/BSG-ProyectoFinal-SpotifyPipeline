.PHONY: install test run clean help

help:
	@echo "Comandos disponibles:"
	@echo "  make install    - Instalar dependencias"
	@echo "  make test       - Correr tests"
	@echo "  make run        - Ejecutar pipeline"
	@echo "  make clean      - Limpiar archivos temporales"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	python src/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete