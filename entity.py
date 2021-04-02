from __future__ import annotations

import copy
import color
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
        if self is self.gamemap.engine.player:
            self.snake(footprint)

    def snake(self, footprint, start_at: int = 0) -> None:
        for i, item in enumerate(self.inventory.items):
            if i < start_at:
                continue
            if not item.blocks_movement:
                if self.gamemap.get_blocking_entity_at_location(*item.xy):
                    return
                else:
                    item.blocks_movement = True
                    item.render_order = RenderOrder.ACTOR
                    item.color = color.player
                    return
            goto = footprint[0] - item.x, footprint[1] - item.y
            footprint = item.xy
            item.move(*goto)

    def is_next_to_player(self):
        for d in DIRECTIONS:
            if self.gamemap.get_actor_at_location(d[0]+self.x,d[1]+self.y) is self.gamemap.engine.player:
                return True
            if self.gamemap.get_item_at_location(d[0]+self.x,d[1]+self.y) in self.gamemap.engine.player.inventory.items:
                return True
        return False

    def how_next_to_player(self):
        how = 0
        for d in DIRECTIONS:
            if self.gamemap.get_actor_at_location(d[0]+self.x,d[1]+self.y) is self.gamemap.engine.player:
                how += 1
            if self.gamemap.get_item_at_location(d[0]+self.x,d[1]+self.y) in self.gamemap.engine.player.inventory.items:
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

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.inventory = Inventory()
        self.inventory.parent = self

        self.base_char = char

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    def constrict(self) -> None:
        if isinstance(self.ai, Constricted):
            return
        self.gamemap.engine.message_log.add_message(f"You constrict the {self.name}!", color.status_effect_applied)
        self.ai = Constricted(self, self.ai, self.color)
        self.color = color.statue
        char_num = int(self.char)-1
        if char_num < 0:
            self.die()
        else:
            self.char = str(char_num)

    def corpse(self) -> None:
        Item(
            charset=('b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z'),
            color=color.corpse,
            name="Consonant",
            edible=consumable.ReversingConsumable(amount=10),
            spitable=consumable.Projectile(damage=1)
        ).spawn(self.gamemap,self.x,self.y)

    def die(self) -> None:
        if self.gamemap.engine.player is self:
            death_message = "You died!"
            death_message_color = color.player_die
            self.char = "%"
            self.color = color.corpse
            self.ai = None
            self.name = f"remains of {self.name}"
            self.render_order = RenderOrder.CORPSE
        else:
            death_message = f"{self.name} is dead!"
            death_message_color = color.enemy_die

            self.gamemap.entities.remove(self)
            self.corpse()

        self.gamemap.engine.message_log.add_message(death_message, death_message_color)

    def take_damage(self, amount: int) -> None:
        if self is not self.gamemap.engine.player:
            new_c = int(self.char)-1
            if new_c < 0:
                self.die()
                return
            self.char = str(new_c)
            new_c = int(self.base_char)-1
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
        charset: Set[str] = ["?"],
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        edible: Consumable,
        spitable: Consumable
    ):
        super().__init__(
            x=x,
            y=y,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )
        self.charset = charset
        self.edible = edible
        self.spitable = spitable
        self.spitable.parent = self
        self.edible.parent = self

    def preSpawn(self):
        self.char = random.choice(self.charset)
        self.name = self.char
