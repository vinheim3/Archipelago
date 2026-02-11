import os
import threading
import typing
from pkgutil import get_data

import bsdiff4

import settings
from BaseClasses import Tutorial
from worlds.AutoWorld import World, WebWorld

from . import items, regions, locations, rules
from .rom import UfouriaDeltaPatch, get_base_rom_path


class AP_UfouriaWebWorld(WebWorld):
    options_page = False
    theme = 'partyTime'

    setup_en = Tutorial(
        tutorial_name='Setup Guide',
        description='A guide to playing Ufouria',
        language='English',
        file_name='setup_en.md',
        link='setup/en',
        authors=['vinheim3']
    )
    
    tutorials = [setup_en]
    game_info_languages = ["en"]


class UfouriaSettings(settings.Group):
    class RomFile(settings.UserFilePath):
        """File name of Ufouria"""
        description = "Ufouria (EU) ROM File"
        copy_to = "Ufouria (EU).nes"
        md5s = [UfouriaDeltaPatch.hash]

    class RomStart(str):
        """
        Set this to false to never autostart a rom (such as after patching)
                    true  for operating system default program
        Alternatively, a path to a program to open the .nes file with
        """

    class DisplayMsgs(settings.Bool):
        """Display message inside of Bizhawk"""

    rom_file: RomFile = RomFile(RomFile.copy_to)
    rom_start: typing.Union[RomStart, bool] = True
    display_msgs: typing.Union[DisplayMsgs, bool] = True


class UfouriaWorld(World):
    game = "Ufouria"
    settings: typing.ClassVar[UfouriaSettings]
    web = AP_UfouriaWebWorld()

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "Start"

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)
        self.rom_name_available_event = threading.Event()

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)
    
    def set_rules(self) -> None:
        locations.set_all_rules(self)
        rules.set_all_rules(self)
    
    def create_items(self) -> None:
        items.create_items(self)
    
    def create_item(self, name) -> items.UfouriaItem:
        return items.create_item(self, name)
    
    def get_filler_item_name(self) -> str:
        return items.get_filler_item_name()
    
    def generate_output(self, output_directory):
        try:
            base_patch = get_data(__name__, "data/base_patch.bsdiff4")
            with open(get_base_rom_path(), 'rb') as rom:
                rom_data = bsdiff4.patch(rom.read(), base_patch)
            outfilebase = 'AP_' + self.multiworld.seed_name
            outfilepname = f'_P{self.player}'
            outfilepname += f"_{self.multiworld.get_file_safe_player_name(self.player).replace(' ', '_')}"
            outputFilename = os.path.join(output_directory, f'{outfilebase}{outfilepname}.nes')
            patched_filename = os.path.join(output_directory, outputFilename)
            with open(patched_filename, 'wb') as patched_rom_file:
                patched_rom_file.write(rom_data)
            patch = UfouriaDeltaPatch(os.path.splitext(outputFilename)[0] + UfouriaDeltaPatch.patch_file_ending,
                                      player=self.player,
                                      player_name=self.multiworld.player_name[self.player],
                                      patched_path=outputFilename)
            patch.write()
            os.unlink(patched_filename)
        finally:
            self.rom_name_available_event.set()
