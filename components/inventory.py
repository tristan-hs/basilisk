from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item

import color
from render_order import RenderOrder


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self):
        self.items: List[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        self.items.remove(item)
        item.color = color.droppings
        item.render_order = RenderOrder.CORPSE
        item.blocks_movement = False

        self.parent.gamemap.engine.check_word_mode()

        self.engine.message_log.add_message(f"You dropped the {item.name}.")