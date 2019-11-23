clean:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	rm -rf dist/

.PHONY: test_unit # run unit tests
test_unit:
	mkdir -p build
	py.test --junitxml=build/unit.xml --cov=omnibot_receiver --cov-report=xml --no-cov-on-fail tests/unit

test: test_unit
