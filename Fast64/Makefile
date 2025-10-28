MAKE := make

# path to blender executable
HACKERTESTSUITE_BLENDER_PATH ?=

# path to the scripts folder from this repo
USER_SCRIPTS := $(shell realpath "../resources/scripts")

# blender execution command, we set the env variable to force using our scripts folder for convenience
# blender starts with background mode enabled, factory startup file loaded and export logs but that need improvements
BLENDER_EXE := BLENDER_USER_SCRIPTS=$(USER_SCRIPTS) "$(HACKERTESTSUITE_BLENDER_PATH)" --background --factory-startup --log-level -1 --log-file logs.txt

# OoT version to use (currently unused)
VERSION ?= gc-eu-mq-dbg

test:
	$(BLENDER_EXE) --python test.py -- --resources-path "../resources" --tests-path "./tests"

.PHONY: test
