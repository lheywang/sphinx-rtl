# Makefile
# 
# Define useful targets for the local testing.

# Public recipes
clean:
	rm -rf _build/web/html
	rm -rf _build/docs/html

web: _build/web/html/index.html
docs: _build/docs/html/index.html

help:
	@echo "Type make web | docs to get the websites to be hosted on localhost"
	@echo "- docs : Local testing, heavier on the edges cases."
	@echo "- web :  Public testing, more a demo than a test."

# Private recipes
_build:
	mkdir -p _build/

_web: _build
	mkdir -p _build/web/html

_docs: _build
	mkdir -p _build/docs/html

_build/web/html/index.html: _web
	sphinx-autobuild -E -a web/pages  _build/web/html --watch src/sphinx_rtl/ --port=0

_build/docs/html/index.html: _docs
	sphinx-autobuild -E -a docs _build/docs/html --watch src/sphinx_rtl/ --port=0