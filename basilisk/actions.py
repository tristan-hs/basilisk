from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from basilisk.render_functions import DIRECTIONS
from basilisk import color, exceptions
from basilisk.components.status_effect import Phasing

if TYPE_CHECKING:
    from basilisk.engine import Engine
    from basilisk.entity import Actor, Entity


class Action:
    meleed = False
    
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor, items=None):
        super().__init__(entity)
        self.items = items

    @property
    def items_here(self):
        return [i for i in self.engine.game_map.items if i.xy == self.entity.xy and i not in self.entity.inventory.items]

    def perform(self) -> None:
        if len(self.items_here) > 1 and not self.items:
            raise exceptions.UnorderedPickup("unordered item pickup")

        items = self.items if self.items else self.items_here

        for item in items:
            if len(self.engine.player.inventory.items) >= 26:
                raise exceptions.Impossible("Inventory full.")

            item.parent = self.entity.inventory
            item.parent.items.append(item)
            self.engine.check_word_mode()
            segment = "" if len(item.label) == 1 else " segment"
            self.engine.message_log.add_message(f"You pick up the ?{segment}.", color.offwhite, item.label, item.color)
            self.engine.history.append(("pickup item",f"{item.name} ({item.char})",self.engine.turn_count))


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None, target_item: Optional[Item] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy
        self._target_item = target_item

    @property
    def target_item(self) -> Optional[Item]:
        return self._target_item

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        self.engine.message_log.add_message(f"You digest the ? segment.", color.offwhite, self.item.label, self.item.color)
        self.item.edible.start_activation (self)
        self.engine.history.append(("digest item",f"{self.item.name} ({self.item.char})",self.engine.turn_count))

class ThrowItem(ItemAction):
    def perform(self, at="actor") -> None:
        if self.engine.player.is_choking:
            raise exceptions.Impossible("Can't spit while choking!")
        target = self.target_actor if at == "actor" else self.target_item
        at = f" at the {target.name}" if target and target is not self.engine.player else ''        
        self.engine.message_log.add_message(f"You spit the ? segment{at}.", color.offwhite, self.item.label, self.item.color)
        
        self.item.spitable.start_activation(self)
        self.engine.history.append(("spit item",f"{self.item.name} ({self.item.char})",self.engine.turn_count))

    @property
    def target_item(self) -> Optional[Item]:
        return self.engine.game_map.get_item_at_location(*self.target_xy)


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy
    
    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_item(self) -> Optional[Item]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_item_at_location(self.entity.x,self.entity.y)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        damage = 1
        i_tar = target in self.engine.player.inventory.items

        pred = "your ? segment" if i_tar else "?"
        label = target.char if i_tar else target.name
        attack_desc = f"{self.entity.name.capitalize()} attacks {pred}!"
            
        if damage > 0:
            t_color = target.color if i_tar else color.offwhite
            self.engine.message_log.add_message(
                attack_desc, color.offwhite, label, t_color
            )
            target.take_damage(damage)
            if target is self.engine.player and not target.is_alive:
                target.cause_of_death = self.entity.name
        else:
            t_color = target.color if i_tar else color.offwhite
            self.engine.message_log.add_message(
                f"{attack_desc} But it does no damage.", color.offwhite, label, t_color
            )


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.blocking_entity and self.entity is not self.engine.player:
            if self.blocking_entity is self.engine.player or self.blocking_entity in self.engine.player.inventory.items:
                self.meleed = True
                return MeleeAction(self.entity, self.dx, self.dy).perform()

        return MovementAction(self.entity, self.dx, self.dy).perform()


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        if self.entity is self.engine.player:
            if not self.engine.game_map.tile_is_snakeable(*self.dest_xy, any(isinstance(s, Phasing) for s in self.entity.statuses)):
                raise exceptions.Impossible("That way is blocked.")

            self.entity.move(self.dx,self.dy)

            for enemy in self.entity.get_adjacent_actors():
                enemy.constrict()
            if self.target_item:
                return PickupAction(self.entity).perform()

        else:
            if not self.engine.game_map.tile_is_walkable(*self.dest_xy):
                raise exceptions.Impossible("That way is blocked.")

            self.entity.move(self.dx,self.dy)


class WaitAction(Action):
    def perform(self) -> None:
        pass

class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            if self.engine.difficulty == "normal" and not self.engine.word_mode:
                raise exceptions.Impossible("Must be in WORD MODE to use stairs.")

            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.purple
            )
            self.engine.history.append(("descend stairs",self.engine.game_map.floor_number,self.engine.turn_count))
        else:
            raise exceptions.Impossible("There are no stairs here.")
