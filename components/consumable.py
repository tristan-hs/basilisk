from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
    SingleProjectileAttackHandler,
    InventoryIdentifyHandler
)
import random

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_throw_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def get_eat_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory.
        Only player consumes for now."""
        footprint = self.parent.xy
        start_at = self.parent.gamemap.engine.player.inventory.items.index(self.parent)
        self.parent.consume()
        self.parent.gamemap.engine.player.snake(footprint, start_at)


class Projectile(Consumable):
    description = "launch a small projectile"

    def __init__(self,damage=1):
        self.damage = damage

    def get_throw_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        self.engine.message_log.add_message("Select a target.", color.cyan)
        return SingleProjectileAttackHandler(
            self.engine,
            callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy)
        )

    def activate(self, action: actions.ItemAction) -> None:
        """ Override this part"""
        consumer = action.entity
        target = action.target_actor

        self.engine.message_log.add_message(
                f"{target.name} takes {self.damage} damage!", color.offwhite
            )
        target.take_damage(self.damage)
        self.consume()


class ReversingConsumable(Consumable):
    description = "turn around"

    def activate(self, action: actions.ItemAction) -> None:
        # swap with the last /solid/ item
        # any that aren't solid stay at the end in reverse order
        consumer = action.entity
        tail = [i for i in consumer.inventory.items if i.blocks_movement][-1]
        x, y = tail.xy

        self.consume()

        items = consumer.inventory.items[:]

        solid_items = [i for i in items if i.blocks_movement]
        nonsolid_items = [i for i in items if not i.blocks_movement]

        solid_items.reverse()
        nonsolid_items.reverse()

        consumer.place(x,y)

        consumer.inventory.items = solid_items + nonsolid_items

        self.engine.message_log.add_message("You turn tail!", color.offwhite)

class ChangelingConsumable(Consumable):
    description = "transform this"

    def activate(self, action: actions.ItemAction) -> None:
        # add new item to snake
        items = action.entity.inventory.items
        new_i = random.choice(self.gamemap.item_factories).spawn(self.parent.gamemap,self.parent.x,self.parent.y)
        new_i.parent = action.entity
        items.insert(items.index(self.parent), new_i)
        new_i.solidify()
        self.engine.message_log.add_message(f"It turns into ?!", color.offwhite, new_i.char, new_i.color)

        # partial consume old item
        self.parent.consume()


class IdentifyingConsumable(Consumable):
    description = "identify another segment"

    @property
    def can_identify(self):
        return any(i.identified == False and i.char != self.parent.char for i in self.engine.player.inventory.items)

    def get_eat_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        if not self.can_identify and self.parent.identified:
            self.engine.message_log.add_message("You have no unidentified segments.", color.grey)
            return

        if self.can_identify:
            self.engine.message_log.add_message("Select a segment to identify.", color.cyan)
            return InventoryIdentifyHandler(self.engine, self.parent)

        return actions.ItemAction(consumer, self.parent)


    def activate(self, action:action.ItemAction) -> None:
        self.consume()
        item = action.target_item
        if not item:
            self.engine.message_log.add_message("You feel momentarily nostalgic.", color.grey)
            return

        self.engine.message_log.add_message(f"You identified the {item.char}.", color.offwhite)
        item.identified = True


class NothingConsumable(Consumable):
    description = None

    def activate(self, action: action.ItemAction) -> None:
        self.engine.message_log.add_message("Your stomach rumbles.", color.grey)
        self.consume()


class ConfusionConsumable(Projectile):
    description = "confuse an enemy"

    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_throw_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        if not self.parent.identified:
            return super().get_throw_action(consumer)

        self.engine.message_log.add_message(
            "Select a target.", color.cyan
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The eyes of the {target.name} glaze over as it stumbles about",
            color.offwhite,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
        )
        self.consume()


class LightningDamageConsumable(Projectile):
    description = "smite a random enemy"

    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def get_throw_action(self, consumer: Actor):
        return actions.ThrowItem(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"Lightning smites the {target.name} for {self.damage} damage!", color.offwhite,
            )
            target.take_damage(self.damage)
        else:
            self.engine.message_log.add_message(f"Lightning strikes the ground nearby.", color.offwhite)

        self.consume()

class FireballDamageConsumable(Projectile):
    description = "conjure an explosion"

    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_throw_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        if not self.parent.identified:
            return super().get_throw_action(consumer)
            
        self.engine.message_log.add_message(
            "Select a target location.", color.cyan
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The explosion engulfs the {actor.name}! It takes {self.damage} damage!", color.offwhite,
                )
                actor.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()