from __future__ import annotations

from typing import TYPE_CHECKING

from .names.items import i

if TYPE_CHECKING:
    from .world import UfouriaWorld


def set_all_rules(world: UfouriaWorld) -> None:
    set_completion_condition(world)


def set_completion_condition(world: UfouriaWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all((i.red_key, i.blue_key, i.green_key), world.player)


class Rule:
    def resolve(self, world, state) -> bool:
        raise NotImplementedError


class Or(Rule):
    def __init__(self, *rules):
        self.rules = rules

    def resolve(self, world, state) -> bool:
        return any(
            rule.resolve(world, state)
            for rule in self.rules
        )
    

class And(Rule):
    def __init__(self, *rules):
        self.rules = rules

    def resolve(self, world, state) -> bool:
        return all(
            rule.resolve(world, state)
            for rule in self.rules
        )


class TrueRule(Rule):
    def resolve(self, world, state):
        return True
true = TrueRule()


class FalseRule(Rule):
    def resolve(self, world, state):
        return False
false = FalseRule()


class CanClimb(Rule):
    def resolve(self, world, state):
        return state.has(i.suction, world.player)
can_climb = CanClimb()


class CanSwim(Rule):
    def resolve(self, world, state):
        return state.has_any((i.freeon, i.gil), world.player)
can_swim = CanSwim()


class CanWalkOnIce(Rule):
    def resolve(self, world, state):
        return state.has(i.freeon, world.player)
can_walk_on_ice = CanWalkOnIce()


class CanHover(Rule):
    def resolve(self, world, state):
        return state.has(i.shades, world.player)
can_hover = CanHover()


class CanDive(Rule):
    def resolve(self, world, state):
        return state.has(i.gil, world.player)
can_dive = CanDive()


class CanBomb(Rule):
    def resolve(self, world, state):
        return state.has_all((i.gil, i.bomb_icon), world.player)
can_bomb = CanBomb()


class CanFreeze(Rule):
    def resolve(self, world, state):
        return state.has_all((i.freeon, i.snowman_icon), world.player)
can_freeze = CanFreeze()


class CanShootHead(Rule):
    def resolve(self, world, state):
        return state.has(i.star_icon, world.player) or state.has_all((i.shades, i.hammer_icon), world.player)
can_shoot = CanShootHead()
