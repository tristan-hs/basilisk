from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from render_functions import DIRECTIONS

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity


class Action:
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

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                item.parent = self.entity.inventory
                inventory.items.append(item)
                self.engine.check_word_mode()

                description = item.name if item.identified and item.item_type != 'v' else item.char

                self.engine.message_log.add_message(f"You picked up the {description}!")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        self.item.edible.activate(self)

class ThrowItem(ItemAction):
    def perform(self) -> None:
        self.item.spitable.activate(self)


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

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk
            
        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.take_damage(damage)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.blocking_entity and self.entity is not self.engine.player:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        return MovementAction(self.entity, self.dx, self.dy).perform()

class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        if not self.engine.game_map.tile_is_walkable(*self.dest_xy):
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)

        if self.entity is self.engine.player:
            if self.target_item:
                PickupAction(self.entity).perform()
            for enemy in self.entity.get_adjacent_actors():
                enemy.constrict()
        
        # Make sure player can move, otherwise die    
        for direction in ((0,-1),(0,1),(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)):
            tile = self.engine.player.x + direction[0], self.engine.player.y + direction[1]
            if self.engine.game_map.tile_is_walkable(*tile):
                return None

        if (self.engine.player.x, self.engine.player.y) == self.engine.game_map.downstairs_location:
            return None
        
        self.engine.player.die()

class WaitAction(Action):
    def perform(self) -> None:
        pass

class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")