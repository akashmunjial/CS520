#!/bin/bash

# To manually build docs, enter the docs folder and call "make html",
# then open the file "_build/html/index.html" in your browser.

(cd docs; make html)
ln -s ./docs/_build/html/index.html index.html
