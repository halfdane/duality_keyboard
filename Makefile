SHELL := /bin/bash

run:
	npm run start

watch:
	npm run watch

display:
	for i in generated_files/outlines/[!_]*.svg; do ( feh --zoom 200 --image-bg white $$i &); done
	for i in *.svg; do ( feh --zoom 200 --image-bg white $$i &); done

