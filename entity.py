from __future__ import annotations

import copy
import color as Color
import math
import random
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union, Set

from render_order import RenderOrder

from components.inventory import Inventory
from components.ai import Constricted
from components import consumable

from render_functions import DIRECTIONS

if TYPE_CHECKING:
    from components.ai import BaseAI
    from game_map import GameMap
    from engine import Engine

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def xy(self) -> Tuple[int, int]:
        return (self.x, self.y)

    @property
    def engine(self) -> Engine:
        return self.gamemap.engine
    
    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.preSpawn()
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def preSpawn(self):
        return

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        footprint = self.xy
        self.x += dx
        self.y += dy

        # Snake thyself
        if self is self.engine.player:
            self.snake(footprint)

    def snake(self, footprint, start_at: int = 0) -> None:
        for item in self.inventory.items[start_at:]:
            if not item.blocks_movement:
                if self.gamemap.get_blocking_entity_at_location(*item.xy):
                    return
                else:
                    item.solidify()
                    return
            goto = footprint[0] - item.x, footprint[1] - item.y
            footprint = item.xy
            item.move(*goto)

    def unsnake(self, start_at: int) -> None:
        for item in self.inventory.items[start_at:]:
            self.engine.message_log.add_message(f"Your {item.char} segment falls off!", Color.grey)
            item.desolidify()
        self.engine.check_word_mode()


    def is_next_to_player(self):
        for d in DIRECTIONS:
            if self.gamemap.get_actor_at_location(d[0]+self.x,d[1]+self.y) is self.engine.player:
                return True
            if self.gamemap.get_item_at_location(d[0]+self.x,d[1]+self.y) in self.engine.player.inventory.items:
                return True
        return False

    def how_next_to_player(self):
        how = 0
        for d in DIRECTIONS:
            if self.gamemap.get_actor_at_location(d[0]+self.x,d[1]+self.y) is self.engine.player:
                how += 1
            if self.gamemap.get_item_at_location(d[0]+self.x,d[1]+self.y) in self.engine.player.inventory.items:
                how += 1
        return how

    def get_adjacent_actors(self)->List[Actor]:
        actors = []
        for d in DIRECTIONS:
            a = self.gamemap.get_actor_at_location(d[0]+self.x,d[1]+self.y)
            if a:
                actors.append(a)
        return actors



class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        move_speed: int = 1,
        ai_cls: Type[BaseAI],
        render_order: RenderOrder = RenderOrder.ACTOR
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=render_order,
        )

        self.inventory = Inventory()
        self.inventory.parent = self

        self.base_char = char
        self.move_speed = move_speed

        self.ai: Optional[BaseAI] = ai_cls(self)

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    def constrict(self) -> None:
        if isinstance(self.ai, Constricted):
            return
        self.engine.message_log.add_message(f"You constrict the {self.name}! It can't move!", Color.offwhite)
        self.ai = Constricted(self, self.ai, self.color)
        self.color = Color.statue
        char_num = int(self.char)-1
        if char_num < 0:
            self.die()
        else:
            self.char = str(char_num)

    def corpse(self) -> None:
        random.choice(self.gamemap.item_factories).spawn(self.gamemap,self.x,self.y)

    def die(self) -> None:
        if self.engine.player is self:
            death_message = "You died!"
            death_message_color = Color.dark_red
            self.char = "%"
            self.color = Color.corpse
            self.ai = None
            self.name = f"remains of {self.name}"
            self.render_order = RenderOrder.CORPSE
        else:
            death_message = f"{self.name} is dead!"
            death_message_color = Color.dark_red

            if self in self.gamemap.entities:
                self.gamemap.entities.remove(self)
            self.corpse()

        self.engine.message_log.add_message(death_message, death_message_color)

    def take_damage(self, amount: int) -> None:
        if self is not self.engine.player:
            new_c = int(self.char)-amount
            if new_c < 0:
                self.die()
                return
            self.char = str(new_c)
            new_c = int(self.base_char)-amount
            if new_c < 0:
                self.die()
                return
            self.base_char = str(new_c)
        else:
            self.die()

class Item(Entity):
    """Any letter"""
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        item_type: str,
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        edible: Consumable,
        spitable: Consumable,
        char: str = '?',
        description: str
    ):
        super().__init__(
            x=x,
            y=y,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )
        self.item_type = item_type
        self.edible = edible
        self.spitable = spitable
        self.spitable.parent = self
        self.edible.parent = self
        self.description=description
        self._identified = False
        self._color = color

    @property
    def label(self):
        return self.name if self.identified and self.item_type != 'v' else self.char

    @property
    def identified(self):
        if self.item_type == 'v':
            return True
        return [i for i in self.gamemap.item_factories if i.char == self.char][0]._identified

    @identified.setter
    def identified(self, new_val: bool):
        if self.item_type == 'v' or self._identified == True:
            return
        factory = [i for i in self.gamemap.item_factories if i.char == self.char][0]
        if factory._identified == True:
            self._identified = True
            return
        factory._identified = self._identified = new_val
        n = 'n' if self.label[0].lower() in ('a','e','i','o','u') else ''
        self.engine.message_log.add_message(f"It was a{n} {self.label} segment.", Color.grey)

    @property
    def color(self):
        if not self.identified:
            return Color.unidentified
        return self._color

    @color.setter
    def color(self, new_val):
        self._color = new_val

    def preSpawn(self):
        if self.item_type == 'v':
            self.char = random.choice(['a','e','i','o','u'])

    def solidify(self):
        self.blocks_movement = True
        self.render_order = RenderOrder.ACTOR
        if self.item_type == 'v':
            self.color = Color.player

    def desolidify(self):
        self.blocks_movement = False
        self.render_order = RenderOrder.ITEM
        if self.item_type == 'v':
            self.color = Color.vowel
        if self in self.engine.player.inventory.items:
            self.engine.player.inventory.items.remove(self)

    #remove the item from the game
    def consume(self):
        self.identified = True
        self.gamemap.entities.remove(self)
        self.engine.player.inventory.items.remove(self)
        self.engine.check_word_mode()

    def take_damage(self, amount: int):
        player = self.gamemap.engine.player
        if self in player.inventory.items:
            i = player.inventory.items.index(self)
            self.engine.message_log.add_message(f"Your {self.label} segment breaks apart!", Color.dark_red)
            self.consume()
            self.engine.player.unsnake(i)



