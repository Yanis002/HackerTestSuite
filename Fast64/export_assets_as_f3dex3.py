#!/usr/bin/python3

import bpy
import addon_utils
import argparse
import os
import time
import sys
import zipfile


ootSceneIDToName = {
    "SCENE_DEKU_TREE": "ydan",
    "SCENE_DODONGOS_CAVERN": "ddan",
    "SCENE_JABU_JABU": "bdan",
    "SCENE_FOREST_TEMPLE": "Bmori1",
    "SCENE_FIRE_TEMPLE": "HIDAN",
    "SCENE_WATER_TEMPLE": "MIZUsin",
    "SCENE_SPIRIT_TEMPLE": "jyasinzou",
    "SCENE_SHADOW_TEMPLE": "HAKAdan",
    "SCENE_BOTTOM_OF_THE_WELL": "HAKAdanCH",
    "SCENE_ICE_CAVERN": "ice_doukutu",
    "SCENE_GANONS_TOWER": "ganon",
    "SCENE_GERUDO_TRAINING_GROUND": "men",
    "SCENE_THIEVES_HIDEOUT": "gerudoway",
    "SCENE_INSIDE_GANONS_CASTLE": "ganontika",
    "SCENE_GANONS_TOWER_COLLAPSE_INTERIOR": "ganon_sonogo",
    "SCENE_INSIDE_GANONS_CASTLE_COLLAPSE": "ganontikasonogo",
    "SCENE_TREASURE_BOX_SHOP": "takaraya",
    "SCENE_DEKU_TREE_BOSS": "ydan_boss",
    "SCENE_DODONGOS_CAVERN_BOSS": "ddan_boss",
    "SCENE_JABU_JABU_BOSS": "bdan_boss",
    "SCENE_FOREST_TEMPLE_BOSS": "moribossroom",
    "SCENE_FIRE_TEMPLE_BOSS": "FIRE_bs",
    "SCENE_WATER_TEMPLE_BOSS": "MIZUsin_bs",
    "SCENE_SPIRIT_TEMPLE_BOSS": "jyasinboss",
    "SCENE_SHADOW_TEMPLE_BOSS": "HAKAdan_bs",
    "SCENE_GANONDORF_BOSS": "ganon_boss",
    "SCENE_GANONS_TOWER_COLLAPSE_EXTERIOR": "ganon_final",
    "SCENE_MARKET_ENTRANCE_DAY": "entra",
    "SCENE_MARKET_ENTRANCE_NIGHT": "entra_n",
    "SCENE_MARKET_ENTRANCE_RUINS": "enrui",
    "SCENE_BACK_ALLEY_DAY": "market_alley",
    "SCENE_BACK_ALLEY_NIGHT": "market_alley_n",
    "SCENE_MARKET_DAY": "market_day",
    "SCENE_MARKET_NIGHT": "market_night",
    "SCENE_MARKET_RUINS": "market_ruins",
    "SCENE_TEMPLE_OF_TIME_EXTERIOR_DAY": "shrine",
    "SCENE_TEMPLE_OF_TIME_EXTERIOR_NIGHT": "shrine_n",
    "SCENE_TEMPLE_OF_TIME_EXTERIOR_RUINS": "shrine_r",
    "SCENE_KNOW_IT_ALL_BROS_HOUSE": "kokiri_home",
    "SCENE_TWINS_HOUSE": "kokiri_home3",
    "SCENE_MIDOS_HOUSE": "kokiri_home4",
    "SCENE_SARIAS_HOUSE": "kokiri_home5",
    "SCENE_KAKARIKO_CENTER_GUEST_HOUSE": "kakariko",
    "SCENE_BACK_ALLEY_HOUSE": "kakariko3",
    "SCENE_BAZAAR": "shop1",
    "SCENE_KOKIRI_SHOP": "kokiri_shop",
    "SCENE_GORON_SHOP": "golon",
    "SCENE_ZORA_SHOP": "zoora",
    "SCENE_POTION_SHOP_KAKARIKO": "drag",
    "SCENE_POTION_SHOP_MARKET": "alley_shop",
    "SCENE_BOMBCHU_SHOP": "night_shop",
    "SCENE_HAPPY_MASK_SHOP": "face_shop",
    "SCENE_LINKS_HOUSE": "link_home",
    "SCENE_DOG_LADY_HOUSE": "impa",
    "SCENE_STABLE": "malon_stable",
    "SCENE_IMPAS_HOUSE": "labo",
    "SCENE_LAKESIDE_LABORATORY": "hylia_labo",
    "SCENE_CARPENTERS_TENT": "tent",
    "SCENE_GRAVEKEEPERS_HUT": "hut",
    "SCENE_GREAT_FAIRYS_FOUNTAIN_MAGIC": "daiyousei_izumi",
    "SCENE_FAIRYS_FOUNTAIN": "yousei_izumi_tate",
    "SCENE_GREAT_FAIRYS_FOUNTAIN_SPELLS": "yousei_izumi_yoko",
    "SCENE_GROTTOS": "kakusiana",
    "SCENE_REDEAD_GRAVE": "hakaana",
    "SCENE_GRAVE_WITH_FAIRYS_FOUNTAIN": "hakaana2",
    "SCENE_ROYAL_FAMILYS_TOMB": "hakaana_ouke",
    "SCENE_SHOOTING_GALLERY": "syatekijyou",
    "SCENE_TEMPLE_OF_TIME": "tokinoma",
    "SCENE_CHAMBER_OF_THE_SAGES": "kenjyanoma",
    "SCENE_CASTLE_COURTYARD_GUARDS_DAY": "hairal_niwa",
    "SCENE_CASTLE_COURTYARD_GUARDS_NIGHT": "hairal_niwa_n",
    "SCENE_CUTSCENE_MAP": "hiral_demo",
    "SCENE_WINDMILL_AND_DAMPES_GRAVE": "hakasitarelay",
    "SCENE_FISHING_POND": "turibori",
    "SCENE_CASTLE_COURTYARD_ZELDA": "nakaniwa",
    "SCENE_BOMBCHU_BOWLING_ALLEY": "bowling",
    "SCENE_LON_LON_BUILDINGS": "souko",
    "SCENE_MARKET_GUARD_HOUSE": "miharigoya",
    "SCENE_POTION_SHOP_GRANNY": "mahouya",
    "SCENE_GANON_BOSS": "ganon_demo",
    "SCENE_HOUSE_OF_SKULLTULA": "kinsuta",
    "SCENE_HYRULE_FIELD": "spot00",
    "SCENE_KAKARIKO_VILLAGE": "spot01",
    "SCENE_GRAVEYARD": "spot02",
    "SCENE_ZORAS_RIVER": "spot03",
    "SCENE_KOKIRI_FOREST": "spot04",
    "SCENE_SACRED_FOREST_MEADOW": "spot05",
    "SCENE_LAKE_HYLIA": "spot06",
    "SCENE_ZORAS_DOMAIN": "spot07",
    "SCENE_ZORAS_FOUNTAIN": "spot08",
    "SCENE_GERUDO_VALLEY": "spot09",
    "SCENE_LOST_WOODS": "spot10",
    "SCENE_DESERT_COLOSSUS": "spot11",
    "SCENE_GERUDOS_FORTRESS": "spot12",
    "SCENE_HAUNTED_WASTELAND": "spot13",
    "SCENE_HYRULE_CASTLE": "spot15",
    "SCENE_DEATH_MOUNTAIN_TRAIL": "spot16",
    "SCENE_DEATH_MOUNTAIN_CRATER": "spot17",
    "SCENE_GORON_CITY": "spot18",
    "SCENE_LON_LON_RANCH": "spot20",
    "SCENE_OUTSIDE_GANONS_CASTLE": "ganon_tou",
    "SCENE_TEST01": "test01",
    "SCENE_BESITU": "besitu",
    "SCENE_DEPTH_TEST": "depth_test",
    "SCENE_SYOTES": "syotes",
    "SCENE_SYOTES2": "syotes2",
    "SCENE_SUTARU": "sutaru",
    "SCENE_HAIRAL_NIWA2": "hairal_niwa2",
    "SCENE_SASATEST": "sasatest",
    "SCENE_TESTROOM": "testroom",
}

ootSceneNameToID = {val: key for key, val in ootSceneIDToName.items()}


def import_scene(sceneID: str):
    # bpy.context.scene.f3d_type = "F3DEX2/LX2"
    settings = bpy.context.scene.ootSceneImportSettings
    settings.option = sceneID
    settings.includeCutscenes = True
    bpy.ops.object.oot_import_level()


def export_scene(isCustomExport: bool, exportPath: str, sceneName: str):
    # bpy.context.scene.f3d_type = "F3DEX3"
    settings = bpy.context.scene.ootSceneExportSettings
    settings.singleFile = True
    settings.customExport = isCustomExport
    settings.exportPath = exportPath
    settings.name = sceneName
    bpy.ops.object.oot_export_level()


def clean_scene():
    to_clean = []
    whitelist = {"EMPTY", "MESH", "CURVE", "CAMERA", "ARMATURE", "TYPE"}
    for obj in bpy.data.objects:
        if not obj.name.startswith("fast64_f3d_material_") and obj.type in whitelist:
            to_clean.append(obj)
    
    for obj in to_clean:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.outliner.orphans_purge(do_recursive=True)


def explore_assets(decompPath: str, sceneID: str):
    def getFileData(path: str):
        with open(path, "r") as file:
            return file.read()

    registeredScenes: set[str] = set()
    sceneToProcessTime: dict[str, tuple[str, str]] = dict()
    sceneName = ootSceneIDToName.get(sceneID)

    for dirpath, dirnames, filenames in os.walk(f"{decompPath}/assets/scenes"):
        allowScene = False
        for filename in filenames:
            if (sceneName is None or sceneName is not None and sceneName in filename) and "_room_" in filename and filename.endswith(".c"):
                filedata = getFileData(f"{dirpath}/{filename}")
                if (
                    "RoomShapeCullableEntry " not in filedata
                    and "RoomShapeImageSingle " not in filedata
                    and "RoomShapeImageMulti " not in filedata
                ):
                    allowScene = True
        if allowScene:
            split = dirpath.split("/")
            if len(split) > 1:
                split = dirpath.split("\\")
            registeredScenes.add(split[-1])
    
    for sceneName in registeredScenes:
        scene = ootSceneNameToID.get(sceneName)
        clean_scene()
        if scene is not None:
            try:
                times = []

                start = time.time()
                import_scene(scene)
                times.append(f"Import took {time.time() - start:.3f}s")

                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export/")
                start = time.time()
                export_scene(True, path, sceneName)
                times.append(f"Export took {time.time() - start:.3f}s")

                sceneToProcessTime[scene] = (times[0], times[1])
            except:
                blendPath = f"./errors/{scene.lower()}.blend"
                bpy.ops.wm.save_as_mainfile(filepath=blendPath)
                bpy.ops.wm.save_as_mainfile(filepath=f"./errors/latest.blend")
                print(f"Scene '{scene}' failed! Saved blend at '{blendPath}'")

    return sceneToProcessTime


def create_zip(folderpath: str, filename: str):
    with zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_LZMA) as zip_file:
        for dirpath, dirnames, filenames in os.walk(folderpath):
            lastFolder = dirpath.split("/")[-1]
            if not ".git" in dirpath and not ".vscode" in dirpath and not ".github" in dirpath:
                for file in filenames:
                    zip_file.write(os.path.join(dirpath, file), os.path.join(lastFolder, file))


def main(args):
    bpy.context.scene.gameEditorMode = "OOT"
    bpy.context.scene.ootDecompPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.decompPath)

    start = time.time()
    sceneToProcessTime = explore_assets(bpy.context.scene.ootDecompPath, args.sceneID)
    stop = time.time()

    if len(sceneToProcessTime) > 0:
        for key, val in ootSceneNameToID.items():
            if val in sceneToProcessTime.keys():
                times = sceneToProcessTime[val]
                print(f"Scene '{val}': {times[0]}, {times[1]}")
    print(f"Time Total: {stop - start:.3f}")


if __name__ == "__main__":
    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    parser = argparse.ArgumentParser(description="Import then export DLs as F3DEX3")
    parser.add_argument(
        "--addons",
        dest="addons",
        help="List of addon paths to enable (folders or zip files)",
        required=True,
    )
    parser.add_argument(
        "--decompPath",
        dest="decompPath",
        help="Offset to the data (uses hex)",
        required=True,
    )
    parser.add_argument(
        "--single",
        dest="sceneID",
        help="Offset to the data (uses hex)",
        required=True,
    )

    args = parser.parse_args(argv)

    addons: list[str] = []
    addonPaths: list[str] = []
    for addon in args.addons.split(","):
        if not addon.endswith(".zip"):
            zipFile = "fast64.zip"
            print("Folder found! Creating zip archive...")
            create_zip(addon, zipFile)
        else:
            zipFile = addon
        addons.append(addon.split("/")[-1].removesuffix(".zip"))
        addonPaths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), zipFile))

    try:
        for addon, path in zip(addons, addonPaths):
            _, is_loaded = addon_utils.check(addon)
            if not is_loaded:
                bpy.ops.preferences.addon_install(filepath=path)
                addon_utils.enable(addon)
        main(args)
        exitCode = 0
        print("SUCCESS!")
    except Exception as e:
        exitCode = 1
        print(Exception(str(e)))
        print("FAILURE!")

    exit(exitCode)
