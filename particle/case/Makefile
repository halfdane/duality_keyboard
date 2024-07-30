SHELL := /bin/bash

run:
	npm run start

watch:
	npm run watch

clean:
	rm -rf generated_files

display: clean run
	for i in generated_files/outlines/[!_]*.svg; do ( feh --zoom 200 --image-bg white $$i &); done
	for i in *.svg; do ( feh --zoom 200 --image-bg white $$i &); done

