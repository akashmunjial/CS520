INDEXLINK = index.html
INDEXFILE = ./docs/_build/html/index.html

clean-docs:
	(rm -f $(INDEXLINK); cd docs; rm -rf source/; make clean)

docs:
	(cd docs; mkdir -p source/; sphinx-apidoc -f -P -M -e -o source/ .. ../backend/keys.py ../test/ ../app.py ../conftest.py; make html)
	ln -s $(INDEXFILE) $(INDEXLINK)

.PHONY: clean-docs docs
