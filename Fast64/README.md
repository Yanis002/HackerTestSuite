# Fast64 Test Suite

Available scripts:
- `export_assets_as_f3dex3.py`: imports then exports vanilla OoT scenes with F3DEX3 (TODO: fix things)
- `test.py`: test script used to play around, I'm currently working on exporting scenes from existing blends. Will try to export scenes from any blends in the `tests/export` folder.

Requirements:
- run `git submodule update --init`
- set the environment variable `HACKERTESTSUITE_BLENDER_PATH` to the path of your blender executable
- optional but you can install `make` to use the makefile that was made for convenience

You can add any addon you want in the `resources/scripts/addons` folder, the scripts will enable them all by default.
