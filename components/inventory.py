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