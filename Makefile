.PHONY: install test lint check demo

install:
	python -m pip install -e '.[dev]'

test:
	pytest -q

lint:
	ruff check .

check: lint test

demo:
	aegislog analyze examples/auth.log
	aegislog incidents examples/auth.log
