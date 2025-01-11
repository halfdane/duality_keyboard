ZMK_APP := $(CURDIR)/zmk/app
SHIELD_NAME ?= particle
BOARD_NAME ?= waveshare_rp2040_zero
MOUNTPOINT_NAME ?= RPI-RP2
BOOTLOADER_NAME := RPI RP2
RAW_BOARD_MOUNTPOINT := /media/$(USER)/$(MOUNTPOINT_NAME)
BUILD := build

# check if zephyr has already been cloned - use their requirements.txt.
# if not, use our own as fallback - it's just to install `west`
ifeq ($(wildcard zephyr/scripts/requirements.txt),) 
	REQUIREMENTS_TXT = requirements.txt
else 
	REQUIREMENTS_TXT = zephyr/scripts/requirements.txt
endif

.PHONY: all update setup verify-zmk compile_app copy_zmk clean deep_clean mount_board follow

.DEFAULT: all

all: compile_app copy_zmk


west_init: .west
.west: venv
	@echo "===> Initializing west"
	@$(VENV)/west init -l config

west_update: venv
	$(VENV)/west update
	$(VENV)/west zephyr-export

verify-zmk:
	@ls $(ZMK_APP) >/dev/null 2>&1 || ( echo "Expected zmk code at $(ZMK_APP), but didn't find anything" && exit 1 )	

compile_app: verify-zmk venv
	@echo "===> Compiling app "
	@$(VENV)/west build -p -s $(ZMK_APP) -b "$(BOARD_NAME)" -S zmk-usb-logging -- -DSHIELD="$(SHIELD_NAME)" -DZMK_CONFIG="$(CURDIR)/config"

clean:
	@echo "===> Deleting build directory $(BUILD)"
	rm -rf $(BUILD)

deep_clean: clean clean-venv
	rm -rf zmk
	rm -rf zephyr
	rm -rf .west
	rm -rf modules


mount_board:
	@echo "Please reset the board into bootloader mode"
	@while [ -z "$$(udisksctl status | grep '$(BOOTLOADER_NAME)' | awk '{print $$NF}')" ]; do sleep 0.5; done
	@echo "===> Trying to mount the board"
	@udisksctl mount -b /dev/$$(udisksctl status | grep '$(BOOTLOADER_NAME)' | awk '{print $$NF}')1

copy_zmk: verify-zmk mount_board
	@echo "===> Copying UF2 file to $(RAW_BOARD_MOUNTPOINT)"
	cp $(BUILD)/zephyr/zmk.uf2 $(RAW_BOARD_MOUNTPOINT)/

follow:
	tio --baudrate 115200 /dev/ttyACM1
 


include Makefile.venv