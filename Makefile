.PHONY: up down test

up:
	docker compose up -d --build

down:
	docker compose down

test:
	python -m pytest -q
