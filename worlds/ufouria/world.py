from worlds.AutoWorld import World

from . import items, regions, locations, rules


class UfouriaWorld(World):
    game = "Ufouria"

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "Start"

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
