from __future__ import annotations

from typing import List, TYPE_CHECKING

from basilisk.components.base_component import BaseComponent
from basilisk import color
from basilisk.render_order import RenderOrder

if TYPE_CHECKING:
    from basilisk.entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self):
        self.items: List[Item] = []