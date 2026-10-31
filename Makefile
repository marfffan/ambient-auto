VERSION := $(shell cat VERSION)
DEB     := build/ambient-auto_$(VERSION)_all.deb

.PHONY: all deb install clean test

all: deb

deb:
	./build-deb.sh

install: deb
	sudo apt install ./$(DEB)

test:
	python3 -m py_compile src/ambient-auto src/gui.py
	@echo "Синтаксис в порядке"

clean:
	rm -rf build src/__pycache__
