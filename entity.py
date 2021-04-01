from __future__ import annotations

import copy
import color
import math
import random
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union, Set

from render_order import RenderOrder

from components.inventory import Inventory

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.fighter import Fighter
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
        fighter: Fighter,
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

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = Inventory()
        self.inventory.parent = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

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
