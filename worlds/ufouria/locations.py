from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from BaseClasses import Location
from worlds.generic.Rules import set_rule

from .names.locations import l
from .names.regions import r
from .rules import Rule, And, Or, can_bomb, can_swim, can_dive, can_climb, can_walk_on_ice, can_hover, can_shoot

if TYPE_CHECKING:
    from .world import UfouriaWorld


class UfouriaLocation(Location):
    game = "Ufouria"


LOCATION_NAME_TO_ID = {
    l.freeon: 1,
    l.shades: 2,
    l.gil: 3,
    l.starting_area_hill_chest: 4,
    l.starting_area_below_water: 5,
    l.starting_area_miniboss_reward: 6,
    l.west_cliffs_floating_island_cave: 7,
    l.west_cliffs_hidden_door: 8,
    l.west_cliffs_underwater_room: 9,
    l.dark_area_in_pit: 10,
    l.dark_area_by_light: 11,
    l.dark_area_miniboss_reward: 12,
    l.cave_area_alcove_near_pool: 13,
    l.cave_area_in_pool: 14,
    l.cave_area_past_lava_hopping: 15,
    l.faucet_area_miniboss_reward: 16,
    l.faucet_area_in_water_column: 17,
    l.faucet_area_above_faucet_cave: 18,
    l.snow_area_above_chimney: 19,
    l.snow_area_miniboss_reward: 20,
    l.lava_challenge_climbing_ice: 21,
    l.lava_challenge_miniboss_reward: 22,
    l.east_vertical_shaft_hover_chest: 23,
    l.east_vertical_shaft_by_long_drop: 24,
    l.clouds_area_miniboss_reward: 25,
    l.clouds_area_entrance_chest: 26,
    l.final_boss_corridor_chest: 27,
}

# The flags 0x40-0x45 are fake new AP location flags converted from
# medicine/water of chest global flags 0xe0-0xe5 (excluding 0x42/0xe2)
LOCATION_GLOBAL_FLAG_TO_ID = {
    0x08: LOCATION_NAME_TO_ID[l.freeon],
    0x09: LOCATION_NAME_TO_ID[l.shades],
    0x0a: LOCATION_NAME_TO_ID[l.gil],
    0x30: LOCATION_NAME_TO_ID[l.starting_area_hill_chest],
    0x11: LOCATION_NAME_TO_ID[l.starting_area_below_water],
    0x39: LOCATION_NAME_TO_ID[l.starting_area_miniboss_reward],
    0x13: LOCATION_NAME_TO_ID[l.west_cliffs_floating_island_cave],
    0x07: LOCATION_NAME_TO_ID[l.west_cliffs_hidden_door],
    0x44: LOCATION_NAME_TO_ID[l.west_cliffs_underwater_room],
    0x12: LOCATION_NAME_TO_ID[l.dark_area_in_pit],
    0x40: LOCATION_NAME_TO_ID[l.dark_area_by_light],
    0x06: LOCATION_NAME_TO_ID[l.dark_area_miniboss_reward],
    0x32: LOCATION_NAME_TO_ID[l.cave_area_alcove_near_pool],
    0x33: LOCATION_NAME_TO_ID[l.cave_area_in_pool],
    0x35: LOCATION_NAME_TO_ID[l.cave_area_past_lava_hopping],
    0x03: LOCATION_NAME_TO_ID[l.faucet_area_miniboss_reward],
    0x34: LOCATION_NAME_TO_ID[l.faucet_area_in_water_column],
    0x43: LOCATION_NAME_TO_ID[l.faucet_area_above_faucet_cave],
    0x10: LOCATION_NAME_TO_ID[l.snow_area_above_chimney],
    0x01: LOCATION_NAME_TO_ID[l.snow_area_miniboss_reward],
    0x41: LOCATION_NAME_TO_ID[l.lava_challenge_climbing_ice],
    0x05: LOCATION_NAME_TO_ID[l.lava_challenge_miniboss_reward],
    0x02: LOCATION_NAME_TO_ID[l.east_vertical_shaft_hover_chest],
    0x31: LOCATION_NAME_TO_ID[l.east_vertical_shaft_by_long_drop],
    0x04: LOCATION_NAME_TO_ID[l.clouds_area_miniboss_reward],
    0x38: LOCATION_NAME_TO_ID[l.clouds_area_entrance_chest],
    0x45: LOCATION_NAME_TO_ID[l.final_boss_corridor_chest],
}


# Mapped to region and access rule
locations: dict[str, tuple[str, None | Rule]] = {
    l.freeon: (r.start, None),
    l.shades: (r.upper_cave_area, None),
    l.gil: (r.west_cliffs, can_swim),
    l.starting_area_hill_chest: (r.start, None),
    l.starting_area_below_water: (r.water_system, None),
    l.starting_area_miniboss_reward: (r.start, can_swim),
    l.west_cliffs_floating_island_cave: (r.west_cliffs, And(can_swim, can_bomb)),
    l.west_cliffs_hidden_door: (r.west_cliffs, can_swim),
    l.west_cliffs_underwater_room: (r.west_cliffs, can_dive),
    l.dark_area_in_pit: (r.dark_area, None),
    l.dark_area_by_light: (r.dark_area, None),
    l.dark_area_miniboss_reward: (r.dark_area, can_dive),
    l.cave_area_alcove_near_pool: (r.upper_cave_area, None),
    l.cave_area_in_pool: (r.lower_cave_area, can_dive),
    l.cave_area_past_lava_hopping: (r.upper_cave_area, Or(can_dive, can_hover)),
    l.faucet_area_miniboss_reward: (r.faucet_south, None),
    l.faucet_area_in_water_column: (r.faucet_south, None),
    l.faucet_area_above_faucet_cave: (r.faucet_north, can_climb),
    l.snow_area_above_chimney: (r.snow_area, can_climb),
    l.snow_area_miniboss_reward: (r.snow_area, And(can_climb, can_walk_on_ice)),
    l.lava_challenge_climbing_ice: (r.lava_challenge, And(can_hover, can_climb)),
    l.lava_challenge_miniboss_reward: (r.lava_challenge, And(can_hover, can_shoot, can_climb)),
    l.east_vertical_shaft_hover_chest: (r.east_vertical_shaft, can_hover),
    l.east_vertical_shaft_by_long_drop: (r.east_vertical_shaft, None),
    l.clouds_area_miniboss_reward: (r.clouds, can_climb),
    l.clouds_area_entrance_chest: (r.clouds, None),
    l.final_boss_corridor_chest: (r.final_boss_corridor, None),
}


def create_all_locations(world: UfouriaWorld) -> None:
    for location_name, details in locations.items():
        region_name, access_rule = details
        region = world.get_region(region_name)
        loc = UfouriaLocation(world.player, location_name, world.location_name_to_id[location_name], region)
        region.locations.append(loc)


def resolve_rule(state, world, rule: Rule):
    return rule.resolve(world, state)


def set_all_rules(world: UfouriaWorld) -> None:
    for location_name, details in locations.items():
        region_name, access_rule = details
        if access_rule is not None:
            location = world.get_location(location_name)
            state_rule = partial(resolve_rule, world=world, rule=access_rule)
            set_rule(location, state_rule)
