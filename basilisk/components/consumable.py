from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import random

from basilisk import actions, color

import basilisk.components.ai

from basilisk.components.base_component import BaseComponent
from basilisk.exceptions import Impossible
from basilisk.input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
    SingleDrillingProjectileAttackHandler,
    SingleProjectileAttackHandler,
    InventoryIdentifyHandler,
    InventoryRearrangeHandler
)
from basilisk.components.status_effect import *
import basilisk.tile_types as tile_types


if TYPE_CHECKING:
    from basilisk.entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_throw_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ThrowItem(consumer, self.parent)

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

    def apply_status(self, action, status, duration=10) -> None:
        st = [s for s in action.target_actor.statuses if isinstance(s,status)]
        if st:
            st[0].strengthen()
        else:
            st = status(duration, action.target_actor)


class Projectile(Consumable):
    description = "launch a small projectile"

    def __init__(self,damage=1):
        self.damage = damage
        if damage > 4:
            descriptor = "large "
        elif damage > 2:
            descriptor = ""
        else:
            descriptor = "small "    
        self.description = f"launch a {descriptor}projectile"

    @property
    def modified_damage(self):
        return self.damage + self.engine.player.BILE

    def get_throw_action(self, consumer: Actor, thru_tail=True) -> Optional[ActionOrHandler]:
        self.engine.message_log.add_message("Select a target.", color.cyan)
        seeking = "anything" #if not self.parent.identified else "actor"
        return SingleProjectileAttackHandler(
            self.engine,
            callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy),
            seeking=seeking,
            thru_tail = thru_tail
        )

    def activate(self, action: actions.ItemAction) -> None:
        """ Override this part"""
        consumer = action.entity
        target = action.target_actor

        if target:
            self.engine.message_log.add_message(
                    f"{target.name} takes {self.modified_damage} damage!", color.offwhite
            )
            target.take_damage(self.modified_damage)
        else:
            self.engine.message_log.add_message("Nothing happens.", color.grey)

        self.consume()

    def consume(self) -> None:
        if any(isinstance(s,FreeSpit) for s in self.engine.player.statuses):
            return

        super().consume()


class SpittingConsumable(Projectile):
    description = "get spat"

    def __init__(self):
        pass

    def get_throw_action(self, consumer: Actor):
        if not self.parent.identified:
            return super().get_throw_action(consumer)

        return super().get_throw_action(consumer, thru_tail=False)

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        path = consumer.ai.get_path_to(*action.target_xy,0)

        for tile in path:
            if not self.engine.game_map.tile_is_walkable(*tile):
                break
            dx = tile[0] - consumer.x
            dy = tile[1] - consumer.y
            consumer.move(dx,dy)

        self.engine.message_log.add_message("Scratch that. It spits you!")
        self.consume()

        for enemy in consumer.get_adjacent_actors():
            enemy.constrict()
        if action.target_item:
                PickupAction(consumer).perform()


class HookshotProjectile(Projectile):
    description = "hookshot an enemy or item"

    def __init__(self):
        pass

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None

        if action.target_actor and action.target_actor is not consumer:
            target = action.target_actor
            tile = consumer.ai.get_path_to(*action.target_xy,0)[0]
            target.place(*tile)
            target.constrict()

        if not target and action.target_item and action.target_item not in consumer.inventory.items:
            target = action.target_item
            tile = consumer.xy
            target.place(*tile)
            actions.PickupAction(consumer).perform()

        if target:
            self.engine.message_log.add_message(f"It pulls the {target.label} back to you!")
        else:
            self.engine.message_log.add_message("Nothing happens.")

        self.consume()




class DrillingProjectile(Projectile):
    description = "pierce the dungeons"

    def __init__(self, damage=1):
        self.damage = damage

    def get_throw_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        if not self.parent.identified:
            return super().get_throw_action(consumer)
        else:
            self.engine.message_log.add_message("Select a target tile.", color.cyan)
            return SingleDrillingProjectileAttackHandler(
                self.engine,
                callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy),
                walkable=False
            )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        walkable = not self.identified
        path = self.engine.player.ai.get_path_to(*action.target_xy,0,walkable)
        gm = self.engine.game_map

        for tile in path:
            actor = gm.get_actor_at_location(*tile)
            if actor and actor is not consumer:
                actor.take_damage(self.modified_damage)
                self.engine.message_log.add_message(f"It drills through the ?!", color.grey, actor.name, actor.color)

            if not gm.tiles['walkable'][tile[0],tile[1]]:
                gm.tiles[tile[0],tile[1]] = tile_types.floor
                self.engine.message_log.add_message("It drills through the dungeon wall!", color.grey)

        self.consume()


class LeakingProjectile(Projectile):
    description = "make an enemy fall to pieces"

    def __init__(self):
        pass

    def get_throw_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        if not self.parent.identified:
            return super().get_throw_action(consumer)

        self.engine.message_log.add_message("Select a target.", color.cyan)
        return SingleRangedAttackHandler(self.engine, callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy))

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            self.engine.message_log.add_message("Nothing happens.",color.grey)
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        if target:
            self.apply_status(action, Leaking)
        self.consume()


class ShieldingConsumable(Consumable):
    description = "shrug off the next hit you take"

    def activate(self, action: actions.ItemAction) -> None:
        self.apply_status(action,Shielded,1)
        self.consume()


class PhasingConsumable(Consumable):
    description = "phase through walls"

    def activate(self, action: actions.ItemAction) -> None:
        self.apply_status(action,Phasing,4)
        self.consume()


class NotConsumable(Consumable):
    description = "know futility"

    def activate(self, action: actions.ItemAction) -> None:
        self.engine.message_log.add_message("The segment refuses your command!", color.mind)
        if not self.parent.identified:
            self.parent.identified = True


class StatBoostConsumable(Consumable):
    messages = {
        "BILE":"A more dangerous ? rises in your throat.",
        "MIND":"Time's weave floods the creases of your ?.",
        "TAIL":"Your ? thrashes with a new strength.",
        "TONG":"Your ? whips the air with increased sensitivity."
    }

    def __init__(self, amount, stat=None, permanent=False):
        self.stat = stat if stat else "a stat"
        self.amount = amount
        forever = " permanently" if permanent else ""
        self.description = f"increases {self.stat} by {amount}{forever}"
        self.permanent = permanent

    def activate(self, action: actions.ItemAction) -> None:
        stat = self.stat if self.stat != "a stat" else random.choice(['BILE','MIND','TAIL','TONG'])
        stat_str = "TONGUE" if stat == "TONG" else stat
        self.engine.message_log.add_message(self.messages[stat], color.grey, stat_str, color.stats[stat])
        if self.permanent:
            action.target_actor.base_stats[self.stat] += self.amount
        else:
            StatBoost(10, action.target_actor, stat, self.amount)
        self.consume()


class FreeSpitConsumable(Consumable):
    description = "spit spit spit"

    def activate(self, action: actions.ItemAction) -> None:
        self.apply_status(action,FreeSpit,4)
        self.consume()


class PetrifEyesConsumable(Consumable):
    description = "be your best self"

    def activate(self, action: actions.ItemAction) -> None:        
        self.apply_status(action, PetrifEyes, 4)
        self.consume()


class ChokingConsumable(Consumable):
    description = "at your own risk"

    def activate(self, action: actions.ItemAction) -> None:
        self.engine.message_log.add_message("The segment bubbles up and gets caught in your throat!")
        self.apply_status(action, Choking)
        self.consume()


class DroppingConsumable(Consumable):
    description = "drop everything"

    def activate(self, action: actions.ItemAction) -> None:
        self.engine.message_log.add_message("As you eject the segment you realize it had become your lynchpin.")
        self.consume()
        self.engine.message_log.add_message("You fall apart!", color.red)
        self.engine.player.unsnake(0)


class ConsumingConsumable(Consumable):
    description = "lose weight"

    def activate(self, action: actions.ItemAction) -> None:
        items = action.entity.inventory.items
        i = items.index(self.parent)
        neighbours = []
        if i > 0:
            neighbours.append(items[i-1])
        if i < len(items)-1:
            neighbours.append(items[i+1])

        self.consume()
        self.engine.message_log.add_message("A spatial rift opens within you!", color.red)

        if neighbours:
            neighbour = random.choice(neighbours)
            self.engine.message_log.add_message(f"The rift swallows your {neighbour.char}!", color.red)
            neighbour.edible.consume()
        else:
            self.engine.message_log.add_message("But it closes harmlessly.", color.grey)


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
        self.engine.check_word_mode()

        self.engine.message_log.add_message("You turn tail!", color.offwhite)


class ChangelingConsumable(Consumable):
    description = "???"

    def activate(self, action: actions.ItemAction) -> None:
        # add new item to snake
        items = action.entity.inventory.items
        changeset = self.gamemap.item_factories
        new_i = random.choice(self.gamemap.item_factories).spawn(self.parent.gamemap,self.parent.x,self.parent.y)
        new_i.parent = action.entity
        items.insert(items.index(self.parent), new_i)
        new_i.solidify()
        self.engine.message_log.add_message(f"It turns into ?!", color.offwhite, new_i.char, new_i.color)

        # partial consume old item
        self.parent.consume()


class IdentifyingConsumable(Consumable):
    description = "identify a segment on your tail"

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
            self.engine.message_log.add_message("You feel nostalgic.", color.grey)
            return

        self.engine.message_log.add_message(f"You identified the {item.char}.", color.offwhite)
        item.identified = True


class IdentifyingProjectile(Projectile):
    description = "identify a segment on the ground"

    def get_throw_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        if not self.parent.identified:
            return super().get_throw_action(consumer)

        self.engine.message_log.add_message("Select a target item.", color.cyan)
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy)
        )


    def activate(self, action:action.ItemAction) -> None:
        self.consume()
        item = action.target_item
        if not item:
            self.engine.message_log.add_message("The segment shatters uselessly on the ground.", color.grey)
            return

        self.engine.message_log.add_message(f"You identified the {item.char}.", color.offwhite)
        item.identified = True


class RearrangingConsumable(Consumable):
    description = "rearrange yourself"

    @property
    def can_rearrange(self):
        return len(self.engine.player.inventory.items) > 2

    def get_eat_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        if not self.can_rearrange and self.parent.identified:
            self.engine.message_log.add_message("You don't have enough segments.", color.grey)
            return

        if self.can_rearrange:
            self.engine.message_log.add_message("Type out your new self.", color.cyan)
            return InventoryRearrangeHandler(self.engine, self.parent)

        return actions.ItemAction(consumer, self.parent)

    def activate(self, action:action.ItemAction) -> None:
        self.consume()
        self.engine.message_log.add_message("You feel self-assured.", color.grey)


class NothingConsumable(Consumable):
    description = None

    def activate(self, action: action.ItemAction) -> None:
        self.engine.message_log.add_message("Your stomach rumbles.", color.grey)
        self.consume()


class ThirdEyeBlindConsumable(Consumable):
    description = "blind your third eye"

    def activate(self, action: actions.ItemAction) -> None:
        self.engine.message_log.add_message("The segment dissolves in the air, leaving a shroud of temporal ambiguity.")
        self.apply_status(action, ThirdEyeBlind)
        self.consume()


class PetrifyConsumable(Consumable):
    description = "petrify thyself"

    def activate(self, action: actions.ItemAction) -> None:
        self.engine.message_log.add_message("The taste of earth and bone permeates your being.")
        self.apply_status(action, PetrifiedSnake, 3)
        self.consume()


class RandomProjectile(Projectile):
    description = "???"

    def activate(self, action: actions.ItemAction) -> None:
        effect = copy.deepcopy(random.choice(self.gamemap.item_factories).spitable)
        self.parent.spitable = effect
        self.parent.spitable.activate(action)


class PetrifyEnemyConsumable(Projectile):
    description = "petrify an enemy"

    def __init__(self):
        pass

    def get_throw_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        if not self.parent.identified:
            return super().get_throw_action(consumer)

        self.engine.message_log.add_message("Select a target.", color.cyan)
        return SingleRangedAttackHandler(self.engine, callback=lambda xy: actions.ThrowItem(consumer, self.parent, xy))

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            self.engine.message_log.add_message("Nothing happens.",color.grey)
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        if target:
            self.apply_status(action, Petrified)
        self.consume()


class ClingyConsumable(Projectile):
    description = ":("

    def activate(self, action: actions.ItemAction) -> None:
        inv = self.parent.gamemap.engine.player.inventory.items
        index = inv.index(self.parent)
        xy = self.parent.xy

        if index == 0:
            self.plop(action)
            return

        other_index = index-1
        other_item = inv[other_index]

        inv[other_index] = self.parent
        inv[index] = other_item

        self.parent.place(*other_item.xy)
        other_item.place(*xy)

        self.parent.solidify()

        self.engine.message_log.add_message("The segment clings and whines, only moving forward a little bit.")

    def plop(self, action: actions.ItemAction):
        xy = self.parent.xy
        space = self.engine.player.ai.get_path_to(*action.target_xy,0)[0]
        self.parent.desolidify()
        self.parent.place(*space)
        self.engine.player.snake(xy)




class ConfusionConsumable(Projectile):
    description = "confuse an enemy"

    def __init__(self, number_of_turns: int=10):
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
            self.engine.message_log.add_message("Nothing happens.",color.grey)
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        if target:
            self.engine.message_log.add_message(
                f"The eyes of the {target.name} glaze over as it stumbles about",
                color.offwhite,
            )
            target.ai = basilisk.components.ai.ConfusedEnemy(
                entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
            )
        self.consume()


class MappingConsumable(Consumable):
    description = "map this floor"

    def activate(self, action: actions.ItemAction) -> None:
        self.engine.message_log.add_message("The segment splatters and spreads across the dungeon, and with it goes your mind")
        self.engine.game_map.make_mapped()
        self.consume()


class LightningDamageConsumable(Projectile):
    description = "smite a random enemy"

    def __init__(self, damage: int=4, maximum_range: int=5):
        self.damage = damage
        self.maximum_range = maximum_range

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
                f"Lightning smites the {target.name} for {self.modified_damage} damage!", color.offwhite,
            )
            target.take_damage(self.modified_damage)
        else:
            self.engine.message_log.add_message(f"Lightning strikes the ground nearby.", color.offwhite)

        self.consume()


class FireballDamageConsumable(Projectile):
    description = "conjure an explosion"

    def __init__(self, damage: int=2, radius: int=2):
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
                    f"The explosion engulfs the {actor.name}! It takes {self.modified_damage} damage!", color.offwhite,
                )
                actor.take_damage(self.modified_damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()



