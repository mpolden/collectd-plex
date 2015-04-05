all: lint

lint:
	flake8 *.py

clean:
	rm -f *.pyc
