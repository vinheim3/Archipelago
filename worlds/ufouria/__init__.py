from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .client import UfouriaClient
from .world import UfouriaWorld


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
