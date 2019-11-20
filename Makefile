clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

test:
	python -3 -m pytest tests
	python3 -bb -m pytest tests

lint:
	flake8 .
