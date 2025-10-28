#!/usr/bin/python3

import bpy
import addon_utils
import argparse
import os
import sys

from pathlib import Path


class Utils:
    """Host utility functions"""

    def __init__(self):
        pass

    @staticmethod
    def import_scene(scene_id: str):
        settings = bpy.context.scene.ootSceneImportSettings
        settings.option = scene_id
        settings.includeCutscenes = True
        bpy.ops.object.oot_import_level()

    @staticmethod
    def export_scene(is_single_file: bool, is_custom_export: bool, export_path: str, scene_name: str):
        settings = bpy.context.scene.ootSceneExportSettings
        settings.singleFile = is_single_file
        settings.customExport = is_custom_export
        settings.exportPath = export_path
        settings.name = scene_name
        bpy.ops.object.oot_export_level()

    @staticmethod
    def clean_scene():
        to_clean = []
        whitelist = {"EMPTY", "MESH", "CURVE", "CAMERA", "ARMATURE", "TYPE"}
        for obj in bpy.data.objects:
            if not obj.name.startswith("fast64_f3d_material_") and obj.type in whitelist:
                to_clean.append(obj)
        
        for obj in to_clean:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.outliner.orphans_purge(do_recursive=True)


class Tests:
    """Hosts test functions to try fast64 features"""

    def __init__(self, resources_path: Path, tests_path: Path):
        self.resources_path = resources_path
        self.tests_path = tests_path

    def export(self, is_hackeroot: bool):
        """Finds each blend from `Fast64/tests/export/' opens them and tries to export the scene with and without single file enabled"""

        export_path = self.tests_path / "export"
        decomp_type = "HackerOoT" if is_hackeroot else "oot"

        # print(bpy.context.mode)

        for blend in export_path.rglob("*.blend"):
            bpy.ops.wm.open_mainfile(filepath=str(blend))
            bpy.context.scene.ootDecompPath = str(self.resources_path / decomp_type)
            Utils.export_scene(True, True, str(export_path / "out"), f"{blend.stem}_{decomp_type.lower()}_singlefile")
            Utils.export_scene(False, True, str(export_path / "out"), f"{blend.stem}_{decomp_type.lower()}_multifile")


def main(args):
    resources_path = Path(args.resources_path).resolve()
    assert resources_path.exists()

    tests_path = Path(args.tests_path).resolve()
    assert tests_path.exists()

    tests = Tests(resources_path, tests_path)
    tests.export(False)
    tests.export(True)


if __name__ == "__main__":
    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    parser = argparse.ArgumentParser(description="Testing Playground")
    parser.add_argument(
        "--resources-path",
        dest="resources_path",
        help="Path to resources folder",
        required=True,
    )
    parser.add_argument(
        "--tests-path",
        dest="tests_path",
        help="Path to tests folder",
        required=True,
    )

    args = parser.parse_args(argv)

    try:
        path = Path(os.environ["BLENDER_USER_SCRIPTS"]) / "addons"
        assert "blender" not in str(path) and "Blender" not in str(path), "'blender' in path, is this the default user script path?"

        for dirpath in path.iterdir():
            if dirpath.is_dir():
                assert addon_utils.enable(dirpath.stem) is not None, f"enabling addon '{dirpath.stem}' failed!"

        main(args)

        exitCode = 0
        print("SUCCESS!")
    except Exception as e:
        exitCode = 1
        print(Exception(str(e)))
        print("FAILURE!")

    exit(exitCode)
