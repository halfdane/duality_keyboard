ZMK_APP := $(CURDIR)/zmk/app
SHIELD_NAME ?= particle
BOARD_NAME ?= waveshare_rp2040_zero
MOUNTPOINT_NAME ?= RPI-RP2
BOOTLOADER_NAME := RPI RP2
RAW_BOARD_MOUNTPOINT := /media/$(USER)/$(MOUNTPOINT_NAME)
BUILD := build
SIDE ?= left

REQUIREMENTS_TXT = zephyr/scripts/requirements.txt

.DEFAULT: left 

left:
	SIDE=left $(MAKE) compile_app copy_zmk
right:
	SIDE=right $(MAKE) compile_app copy_zmk

west: .west
.west:
	uvx west init -l config
	uvx west update
	uvx west zephyr-export
	cd zephyr && git remote add johanson git@github.com:petejohanson/zephyr.git && git fetch johanson && git checkout v3.5.0+zmk-fixes+rp2040-uart-fifo


verify-zmk:
	@ls $(ZMK_APP) >/dev/null 2>&1 || ( echo "Expected zmk code at $(ZMK_APP), but didn't find anything" && exit 1 )	

compile_app: west verify-zmk venv
	. .venv/bin/activate && \
	west build -p -s $(ZMK_APP) -b "$(BOARD_NAME)" \
		-d "$(BUILD)/$(SIDE)" \
		-S zmk-usb-logging -S studio-rpc-usb-uart \
		-- \
		-DSHIELD="$(SHIELD_NAME)_$(SIDE)" -DZMK_CONFIG="$(CURDIR)/config" \
		-DCONFIG_ZMK_STUDIO=y 

clean:
	rm -rf $(BUILD)

deep_clean: clean clean-venv
	rm -rf zmk
	rm -rf zephyr
	rm -rf .west
	rm -rf modules

mount_board:
	@echo "Please reset the $(SIDE) board into bootloader mode"
	@while [ -z "$$(udisksctl status | grep '$(BOOTLOADER_NAME)' | awk '{print $$NF}')" ]; do sleep 0.5; done
	@echo "===> Sleeping a bit to let the system settle"
	@sleep 2
	@echo "===> Trying to mount the board"
	@udisksctl mount -b /dev/$$(udisksctl status | grep '$(BOOTLOADER_NAME)' | awk '{print $$NF}')1

copy_zmk: verify-zmk mount_board
	@echo "===> Copying UF2 file to $(RAW_BOARD_MOUNTPOINT)"
	cp $(BUILD)/$(SIDE)/zephyr/zmk.uf2 $(RAW_BOARD_MOUNTPOINT)/

follow:
	tio --baudrate 115200 /dev/ttyACM2
 


include Makefile.venv
