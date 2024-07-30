MOUNTPOINT := $(shell ls -d /media/tvollert/PARTICLE_*)

.DEFAULT: all

.PHONY: kmk

all: copy-kmk copy-lib copy-codepy 

copy-codepy:
	@echo "===> Copying python files to $(MOUNTPOINT)"
	@rsync -rhu --out-format="%n" *.py $(MOUNTPOINT)/
	touch $(MOUNTPOINT)/me
	@sync

copy-kmk:
	@echo "===> Copying KMK source folder to $(MOUNTPOINT)"
	@rsync -rhu --out-format="%n" kmk $(MOUNTPOINT)/
	@sync

copy-lib:
	@echo "===> Copying library files to $(MOUNTPOINT)"
	@rsync -rhu --out-format="%n" --ignore-missing-args lib/*.py lib/*.mpy $(MOUNTPOINT)/lib
	@sync

prepare: kmk cirquitpython cirque

kmk:
	rm -rf kmk_firmware kmk
	# bug in combos prevents debug mode, use own fork instead
	git clone git@github.com:KMKfw/kmk_firmware.git
	# git clone git@github.com:halfdane/kmk_firmware.git
	cd kmk_firmware && git checkout main
	rsync -rhu kmk_firmware/kmk .

cirquitpython:
	wget `curl -s https://api.github.com/repos/adafruit/Adafruit_CircuitPython_Bundle/releases/latest | jq -r '.assets.[].browser_download_url | select(.|test("8.x-mpy"))'`

cirque:
	wget https://raw.githubusercontent.com/2bndy5/CircuitPython_Cirque_Pinnacle/master/circuitpython_cirque_pinnacle.py -O lib/circuitpython_cirque_pinnacle.py

