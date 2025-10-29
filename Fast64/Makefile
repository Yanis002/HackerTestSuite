MAKE := make

# path to blender executable
HACKERTESTSUITE_BLENDER_PATH ?=

# path to the scripts folder from this repo
USER_SCRIPTS := $(shell realpath "../resources/scripts")

# blender execution command, we set the env variable to force using our scripts folder for convenience
# blender starts with background mode enabled, factory startup file loaded and export logs but that need improvements
BLENDER_EXE := BLENDER_USER_SCRIPTS=$(USER_SCRIPTS) "$(HACKERTESTSUITE_BLENDER_PATH)" --background --factory-startup --log-level -1 --log-file logs.txt

# OoT version to use (currently unused)
# VERSION ?= ntsc-1.2

N_THREADS ?= $(shell nproc)

test:
	$(BLENDER_EXE) --python test.py -- --mode export --resources-path "../resources" --tests-path "./tests"

hackeroot_setup: test
	rm -rf ../resources/HackerOoT/assets/testsuite
	rm -rf ../resources/HackerOoT/include/testsuite
	cp -rv ./out/HackerOoT/assets ../resources/HackerOoT/
	cp -rv ./out/HackerOoT/include ../resources/HackerOoT/
	cp -rv ./out/HackerOoT/spec/testsuite.inc ../resources/HackerOoT/spec
	$(MAKE) -C ../resources/HackerOoT/ clean

hackeroot_run: hackeroot_setup
	TESTSUITE_MODE=1 $(MAKE) -C ../resources/HackerOoT/ -j$(N_THREADS) run

hackeroot: hackeroot_setup
	TESTSUITE_MODE=1 $(MAKE) -C ../resources/HackerOoT/ -j$(N_THREADS)

.PHONY: test hackeroot_setup hackeroot_run hackeroot
