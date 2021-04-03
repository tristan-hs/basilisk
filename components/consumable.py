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
        entity = self.parent
        inventory = self.engine.player.inventory.items
        key = self.parent.char

        entity.identified = True
        
        footprint = entity.xy
        startat = inventory.index(self.parent)

        self.gamemap.entities.remove(entity)
        inventory.remove(entity)
        self.engine.check_word_mode()
        self.engine.player.snake(footprint,startat)


class Projectile(Consumable):
    description = "deals 1 damage to the target"

    def __init__(self,damage=1):
        self.damage = damage

    def get_throw_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        self.engine.message_log.add_message("Select a target.", color.needs_target)
        return SingleProjectileAttackHandler(
            self.engine,
            callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy)
        )

    def activate(self, action: actions.ItemAction) -> None:
        """ Override this part"""
        consumer = action.entity
        target = action.target_actor

        self.engine.message_log.add_message(
                f"You spit your {self.parent.char} at the {target.name} for {self.damage} damage!"
            )
        target.take_damage(self.damage)
        self.consume()


class ReversingConsumable(Consumable):
    description = "swaps your head and your tail"

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        items = consumer.inventory.items[:]
        last_item = items.pop()
        ox = consumer.x
        oy = consumer.y

        consumer.place(last_item.x, last_item.y)
        last_item.place(ox,oy)
        items.reverse()
        items.append(last_item)
        consumer.inventory.items = items

        self.engine.message_log.add_message("Your head and tail swap places!")
        self.consume()

class ChangelingConsumable(Consumable):
    description = "changes its shape"

    def activate(self, action: actions.ItemAction) -> None:
        # add new item to snake
        items = action.entity.inventory.items
        new_i = random.choice(self.gamemap.item_factories).spawn(self.parent.gamemap,self.parent.x,self.parent.y)
        new_i.parent = action.entity
        items.insert(items.index(self.parent), new_i)
        new_i.solidify()
        self.engine.message_log.add_message(f"Your {self.parent.char} morphs into a {new_i.char}!")

        # partial consume old item
        self.parent.identified = True
        
        self.gamemap.entities.remove(self.parent)
        items.remove(self.parent)
        self.engine.check_word_mode()


class ConfusionConsumable(Projectile):
    description = "confuses an enemy"

    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_throw_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        if not self.parent.identified:
            return super().get_throw_action(consumer)

        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
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
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",
            color.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
        )
        self.consume()


class LightningDamageConsumable(Projectile):
    description = "smites a random nearby enemy"

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
                f"A lightning bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")

class FireballDamageConsumable(Projectile):
    description = "blasts an area with a fireball"

    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_throw_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        if not self.parent.identified:
            return super().get_throw_action(consumer)
            
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
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
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()