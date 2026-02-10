from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from BaseClasses import Region
from .names.regions import r
from .rules import true, false, can_climb, Rule, And, Or, can_walk_on_ice, can_dive, can_swim, can_bomb, can_hover

if TYPE_CHECKING:
    from .world import UfouriaWorld


connections: dict[str, dict[str, Rule]] = {
    r.start: {
        r.west_cliffs: can_climb,
        r.ice_corridor: can_walk_on_ice,
        r.water_system: can_dive,
    },
    r.west_cliffs: {
        r.dark_area: And(can_swim, can_bomb),
        r.final_boss_corridor: true,
    },
    r.ice_corridor: {
        r.final_boss_corridor: true,
        r.east_vertical_shaft: true,
    },
    r.water_system: {
        r.clouds: true,
        r.faucet_south: can_bomb,
        r.upper_cave_area: true,
    },
    r.dark_area: {},
    r.final_boss_corridor: {
        r.west_cliffs: can_climb,
        r.ice_corridor: false,
    },
    r.east_vertical_shaft: {
        r.ice_corridor: can_walk_on_ice,
        r.clouds: Or(can_hover, can_climb),
        r.lava_challenge: can_bomb,
        r.lower_cave_area: true,
    },
    r.faucet_north: {
        r.water_system: can_dive,
        r.clouds: can_climb,
        r.faucet_south: And(can_climb, can_dive),
    },
    r.faucet_south: {
        r.water_system: can_bomb,
        r.faucet_north: true,
    },
    r.upper_cave_area: {
        r.water_system: can_dive,
        r.snow_area: can_dive,
        r.lower_cave_area: true,
    },
    r.lower_cave_area: {
        r.snow_area: And(can_dive, can_climb),
        r.east_vertical_shaft: true,
        r.upper_cave_area: Or(can_swim, can_climb)
    },
    r.clouds: {
        r.faucet_north: can_climb,
        r.water_system: can_dive,
        r.east_vertical_shaft: true,
    },
    r.lava_challenge: {},
    r.snow_area: {},
}


def create_and_connect_regions(world: UfouriaWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: UfouriaWorld):
    for name in connections.keys():
        world.multiworld.regions.append(Region(name, world.player, world.multiworld))


def resolve_rule(state, world, rule: Rule):
    return rule.resolve(world, state)


def connect_regions(world: UfouriaWorld):
    for source_name, targets in connections.items():
        source_region = world.get_region(source_name)
        for target_name, access_rule in targets.items():
            target_region = world.get_region(target_name)
            state_rule = partial(resolve_rule, world=world, rule=access_rule)
            source_region.connect(target_region, f"{source_name} -> {target_name}", rule=state_rule)
