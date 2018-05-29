default: install

install:
	pip install -r ./requirements.txt

run:
	python3 crawler.py

clean:
	rm -f *.json

.PHONY: default install run clean
