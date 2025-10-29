#!/usr/bin/python3

import bpy
import addon_utils
import argparse
import os
import sys
import shutil

from pathlib import Path


INDENT = " " * 4


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


class DecompExporter:
    def __init__(self, scene_name: str, is_single_file: bool, cs_total: int, room_total: int, entr_objs: list[bpy.types.Object], draw_config: str, title_card: str):
        self.scene_name = scene_name
        self.is_single_file = is_single_file
        self.cs_total = cs_total
        self.room_total = room_total
        self.entr_objs = entr_objs
        self.draw_config = draw_config
        self.title_card = title_card

        self.entr_base = f"ENTR_{self.scene_name.upper()}"
        self.scene_id = f"SCENE_{self.scene_name.upper()}"

    def get_entry_base(self, name: str, compress: bool = True):
        segment = [f'name "{name}"']

        if compress:
            segment.append("compress")

        segment.append("romalign 0x1000")
        return segment
    
    def get_scene_entry(self):
        name = f"{self.scene_name}_scene"
        segment = self.get_entry_base(name)

        if self.is_single_file:
            includes = [f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}.o"']
        else:
            includes = [
                f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}_main.o"',
                f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}_col.o"',
            ]

            if self.cs_total > 0:
                for i in range(self.cs_total):
                    includes.append(f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}_cs_{i}.o"')

        segment.extend(includes)
        segment.append("number 2")
        return segment

    def get_room_entry(self, room_index: int):
        name = f"{self.scene_name}_room_{room_index}"
        segment = self.get_entry_base(name)

        if self.is_single_file:
            includes = [f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}.o"']
        else:
            includes = [
                f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}_main.o"',
                f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}_model_info.o"',
                f'include "$(BUILD_DIR)/assets/testsuite/scenes/{self.scene_name}/{name}_model.o"',
            ]

        segment.extend(includes)
        segment.append("number 3")
        return segment

    def get_scene_entries(self):
        scene_segment = f"beginseg\n{INDENT}" + f"\n{INDENT}".join(elem for elem in self.get_scene_entry()) + "\nendseg\n\n"

        room_segments = str()
        for i in range(self.room_total):
            room_segment = f"beginseg\n{INDENT}" + f"\n{INDENT}".join(elem for elem in self.get_room_entry(i)) + "\nendseg\n"
            room_segments += room_segment + "\n"

        return scene_segment + room_segments

    def get_map_select_entries(self):
        select_entry = f"// ----- Scene '{self.scene_name}' -----\n"
        
        for i in range(len(self.entr_objs)):
            select_entry += "{ " + f'"{self.scene_name} ({i})", (void*)MapSelect_LoadGame, {self.entr_base}_{i}' + " },\n"    

        return select_entry + "\n"

    def get_entrance_entries(self):
        entrance_entry = f"// ----- Scene '{self.scene_name}' -----\n\n"

        for i, entr_obj in enumerate(self.entr_objs):
            assert i == entr_obj.ootEntranceProperty.spawnIndex, f"index mismatch for entrance '{entr_obj.name}', are the spawn indices correct?"

            entrance_entry += (
                f"// Spawn No. {i}, Empty Name: '{entr_obj.name}'\n" 
                + f"DEFINE_ENTRANCE({self.entr_base}_{i}, {self.scene_id}, {i}, false, true, TRANS_TYPE_FADE_WHITE, TRANS_TYPE_FADE_WHITE)\n"
            )

            for j in range(1, 4):
                entrance_entry += f"DEFINE_ENTRANCE({self.entr_base}_{i}_{j}, {self.scene_id}, {i}, false, true, TRANS_TYPE_FADE_WHITE, TRANS_TYPE_FADE_WHITE)\n"
            
            entrance_entry += "\n"

        return entrance_entry

    def get_scene_table_entry(self):
        return f"DEFINE_SCENE({self.scene_name}_scene, {self.title_card}, {self.scene_id}, {self.draw_config}, 0, 0)\n"


class Tests:
    """Hosts test functions to try fast64 features"""

    def __init__(self, resources_path: Path, tests_path: Path, export_path: Path, out_path: Path):
        self.resources_path = resources_path
        self.tests_path = tests_path
        self.export_path = export_path
        self.out_path = out_path

        print(f"Using:\n\tresources_path: {self.resources_path}\n\ttests_path: {self.tests_path}\n\texport_path: {self.export_path}\n\tout_path: {self.out_path}")

    def export(self, is_hackeroot: bool):
        """Finds each blend from `Fast64/tests/export/' opens them and tries to export the scene with and without single file enabled"""

        decomp_type = "HackerOoT" if is_hackeroot else "oot"
        out_decomp = self.out_path / decomp_type
        inc_folder = out_decomp / "include" / "testsuite"
        spec_folder = out_decomp / "spec"
        spec_entries = str()
        map_select_entries = str()
        entrance_entries = str()
        scene_entries = str()

        if out_decomp.exists():
            shutil.rmtree(out_decomp)
        out_decomp.mkdir(parents=True)
        inc_folder.mkdir(parents=True)
        spec_folder.mkdir(parents=True)

        for blend in (self.tests_path / "export").rglob("*.blend"):
            name_single = f"{blend.stem}_{decomp_type.lower()}_singlefile"
            name_multi = f"{blend.stem}_{decomp_type.lower()}_multifile"

            bpy.ops.wm.open_mainfile(filepath=str(blend))
            bpy.context.scene.ootDecompPath = str(self.resources_path / decomp_type)

            scene_objs = [obj for obj in bpy.data.objects if obj.type == "EMPTY" and obj.ootEmptyType == "Scene"]

            for scene_obj in scene_objs:
                scene_header = scene_obj.ootSceneHeader

                room_objs = [obj for obj in scene_obj.children_recursive if obj.type == "EMPTY" and obj.ootEmptyType == "Room"]
                entrance_objs = [obj for obj in scene_obj.children_recursive if obj.type == "EMPTY" and obj.ootEmptyType == "Entrance"]
                entrance_objs.sort(key=lambda obj: obj.ootEntranceProperty.spawnIndex)

                # TODO: fix issue with duplicated cutscene names
                scene_header.writeCutscene = False
                cs_objs = [
                    # obj for obj in bpy.data.objects
                    # if obj.type == "EMPTY" 
                    # and obj.ootEmptyType == "Cutscene" 
                    # and (scene_header.writeCutscene and scene_header.csWriteObject == obj or obj in scene_header.extraCutscenes)
                ]

                bpy.context.scene.ootSceneExportObj = scene_obj

                Utils.export_scene(True, True, str((out_decomp / "assets" / "testsuite" / "scenes")), name_single)
                exporter = DecompExporter(name_single, True, len(cs_objs), len(room_objs), entrance_objs, scene_header.sceneTableEntry.drawConfig, scene_header.title_card_name)
                spec_entries += exporter.get_scene_entries()
                map_select_entries += exporter.get_map_select_entries()
                entrance_entries += exporter.get_entrance_entries()
                scene_entries += exporter.get_scene_table_entry()

                Utils.export_scene(False, True, str((out_decomp / "assets" / "testsuite" / "scenes")), name_multi)
                exporter = DecompExporter(name_multi, False, len(cs_objs), len(room_objs), entrance_objs, scene_header.sceneTableEntry.drawConfig, scene_header.title_card_name)
                spec_entries += exporter.get_scene_entries()
                map_select_entries += exporter.get_map_select_entries()
                entrance_entries += exporter.get_entrance_entries()
                scene_entries += exporter.get_scene_table_entry()

        path = spec_folder / "testsuite.inc"
        path.write_text(spec_entries)

        path = inc_folder / "map_select.h"
        path.write_text(map_select_entries)

        path = inc_folder / "entrance_table.h"
        path.write_text(entrance_entries)

        path = inc_folder / "scene_table.h"
        path.write_text(scene_entries)


def main(args):
    resources_path = Path(args.resources_path).resolve()
    assert resources_path.exists()

    tests_path = Path(args.tests_path).resolve()
    assert tests_path.exists()

    if args.export_path is not None:
        export_path = Path(args.export_path).resolve()
        assert export_path.exists()
    else:
        export_path = tests_path / "export"

    tests = Tests(resources_path, tests_path, export_path, Path("./out").resolve())

    print(f"Using mode: '{args.mode}'")

    match args.mode:
        case "export":
            tests.export(False)
            tests.export(True)
        case _:
            print(f"Unknown mode '{args.mode}'")


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
        "--mode",
        dest="mode",
        help="Operating mode",
        required=True,
    )
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
    parser.add_argument(
        "--export-path",
        dest="export_path",
        help="Export path to use",
        required=False,
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
