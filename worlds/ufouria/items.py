from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .names.items import i

if TYPE_CHECKING:
    from .world import UfouriaWorld


@dataclass
class ItemData:
    id: int
    name: str
    classification: ItemClassification
    """
    If global_flag is specified, upon receiving the item,
    that global is set. It's currently on all items, but later
    on, there may be things like traps.
    """
    global_flag: int | None


items = [
    ItemData(1, i.red_key, ItemClassification.progression, global_flag=0x07),
    ItemData(2, i.green_key, ItemClassification.progression, global_flag=0x06),
    ItemData(3, i.blue_key, ItemClassification.progression, global_flag=0x05),
    ItemData(4, i.medicine, ItemClassification.filler, global_flag=0x36),
    ItemData(5, i.water_of_life, ItemClassification.useful, global_flag=0x37),
    ItemData(6, i.freeon, ItemClassification.progression, global_flag=0x08),
    ItemData(7, i.shades, ItemClassification.progression, global_flag=0x09),
    ItemData(8, i.gil, ItemClassification.progression, global_flag=0x0a),
    ItemData(9, i.star_icon, ItemClassification.progression, global_flag=0x39),
    ItemData(10, i.snowman_icon, ItemClassification.useful, global_flag=0x01),
    ItemData(11, i.hammer_icon, ItemClassification.progression, global_flag=0x02),
    ItemData(12, i.bomb_icon, ItemClassification.progression, global_flag=0x03),
    ItemData(13, i.suction, ItemClassification.progression, global_flag=0x04),
    ItemData(14, i.life_container_1, ItemClassification.useful, global_flag=0x10),
    ItemData(15, i.life_container_2, ItemClassification.useful, global_flag=0x11),
    ItemData(16, i.life_container_3, ItemClassification.useful, global_flag=0x12),
    ItemData(17, i.life_container_4, ItemClassification.useful, global_flag=0x13),
    ItemData(18, i.crystal, ItemClassification.deprioritized, global_flag=0x30),
    ItemData(19, i.map, ItemClassification.deprioritized, global_flag=0x31),
    ItemData(20, i.compass, ItemClassification.deprioritized, global_flag=0x32),
    ItemData(21, i.red_power_ring, ItemClassification.deprioritized, global_flag=0x35),
    ItemData(22, i.green_power_ring, ItemClassification.deprioritized, global_flag=0x34),
    ItemData(23, i.blue_power_ring, ItemClassification.deprioritized, global_flag=0x33),
    ItemData(24, i.power_of_insight, ItemClassification.deprioritized, global_flag=0x38),
]


ITEM_NAME_TO_ITEM: dict[str, ItemData] = {
    item.name: item
    for item in items
}

ITEM_ID_TO_ITEM: dict[int, ItemData] = {
    item.id: item
    for item in items
}

ITEM_NAME_TO_ID = {
    item.name: item.id
    for item in items
}


class UfouriaItem(Item):
    game = "Ufouria"


def create_items(world: UfouriaWorld):
    itempool = []
    for item in items:
        if item.classification != ItemClassification.filler:
            itempool.append(create_item(world, item.name))

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
    world.multiworld.itempool += itempool


def create_item(world: UfouriaWorld, name: str):
    return UfouriaItem(name, ITEM_NAME_TO_ITEM[name].classification, ITEM_NAME_TO_ID[name], world.player)


def get_filler_item_name():
    return i.medicine
