from __future__ import annotations

import copy
import math
import random
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union, Set

from basilisk.render_order import RenderOrder

from basilisk import color as Color

from basilisk.components.inventory import Inventory
from basilisk.components.ai import Constricted
from basilisk.components import consumable

from basilisk.render_functions import DIRECTIONS

if TYPE_CHECKING:
    from basilisk.components.ai import BaseAI
    from basilisk.game_map import GameMap
    from basilisk.engine import Engine

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
        description: str = "???",
        rarity: Optional[str] = None,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self._description=description
        self.rarity = rarity
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

    @property
    def label(self) -> str:
        return self.name

    @property
    def description(self) -> str:
        return self._description
    
    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        clone.preSpawn()
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
            self.engine.message_log.add_message(f"Your ? segment falls off!", Color.grey, item.char, item.color)
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
            elif self.gamemap.get_item_at_location(d[0]+self.x,d[1]+self.y) in self.engine.player.inventory.items:
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
        render_order: RenderOrder = RenderOrder.ACTOR,
        description: str = "???",
        drop_tier: str = 'c',
        is_boss: bool = False
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=render_order,
            description=description
        )

        self.inventory = Inventory()
        self.inventory.parent = self

        self.base_char = char
        self.move_speed = move_speed

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.statuses = []
        self.drop_tier = drop_tier
        self.is_boss = is_boss

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)


    def on_turn(self) -> None:
        for status in self.statuses:
            status.decrement()

    def constrict(self) -> None:
        if isinstance(self.ai, Constricted):
            return
        self.engine.message_log.add_message(f"You constrict the {self.name}!", Color.offwhite)
        self.ai = Constricted(self, self.ai, self.color)
        self.color = Color.statue
        char_num = int(self.char)-1
        if char_num < 0:
            self.die()
        else:
            self.char = str(char_num)

    def corpse(self) -> None:
        my_factor = (int(self.char) + self.move_speed + 1)*0.1

        # 0.16 + (0.64 * factor) = chance of corpsing
        if (random.random() > my_factor and random.random() > 0.2) or random.random() > 0.8:
            return

        my_drops = []
        for i in self.gamemap.item_factories:
            factor = Item.letters()[i.char]
            additions = [i] * factor if i.rarity != self.drop_tier else [i] * (factor+2) * (factor+2)
            my_drops += additions

        random.choice(my_drops).spawn(self.gamemap,self.x,self.y)

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

            if self.is_boss:
                self.engine.boss_killed = True
            else:
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
        description: str = '???',
        rarity: Optional[str] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
            description=description,
            rarity=rarity
        )
        self.item_type = item_type
        self.edible = edible
        self.spitable = spitable
        self.spitable.parent = self
        self.edible.parent = self
        self._identified = False
        self._color = color
        self.rarity = rarity

    @property
    def label(self):
        return self.name if self.identified else self.char

    @property
    def identified(self):
        if self.item_type == 'v':
            return True
        if self.item_type == 'y':
            return False
        return [i for i in self.gamemap.item_factories if i.char == self.char][0]._identified

    @identified.setter
    def identified(self, new_val: bool):
        if self.item_type != 'c' or self._identified:
            return
        factory = [i for i in self.gamemap.item_factories if i.char == self.char][0]
        if factory._identified == True:
            self._identified = True
            return
        factory._identified = self._identified = new_val
        n = 'n' if self.label[0].lower() in ('a','e','i','o','u') else ''
        self.engine.message_log.add_message(f"It was a{n} ? segment.", Color.grey, self.label, self.color)

    @property
    def color(self):
        if not self.identified and self.item_type != 'y':
            return Color.unidentified
        if self.item_type == 'y' and random.random() > 0.5:
            return random.choice([Color.electric, Color.tongue, Color.electric, Color.reversal, Color.fire, Color.vowel])
        return self._color

    @property
    def description(self):
        if self.identified:
            d = ''
            if self.edible.description:
                d += f"Digest: {self.edible.description}"
            if self.spitable.description:
                if self.edible.description:
                    d += "\n\n"
                d += f"Spit: {self.spitable.description}"
            return d
        else:
            return '???'

    @color.setter
    def color(self, new_val):
        self._color = new_val

    @staticmethod
    def letters():
        return {
        'b':2,
        'c':2,
        'd':4,
        'f':2,
        'g':3,
        'h':2,
        'j':1,
        'k':1,
        'l':4,
        'm':2,
        'n':6,
        'p':2,
        'q':1,
        'r':6,
        's':4,
        't':6,
        'v':2,
        'w':2,
        'x':1,
        'z':1
    }

    def preSpawn(self):
        if self.item_type == 'v':
            self.char = random.choice(['a','e','i','o','u'])
        if self.item_type == 'y':
            self.char = 'y'
            self.edible = random.choice([
                consumable.ReversingConsumable,
                consumable.ChangelingConsumable,
                consumable.IdentifyingConsumable,
                consumable.RearrangingConsumable,
                consumable.NothingConsumable,
                consumable.ChokingConsumable,
                consumable.MappingConsumable,
            ])()
            self.spitable = random.choice([
                consumable.Projectile,
                consumable.MappingConsumable,
                consumable.LightningDamageConsumable,
                consumable.FireballDamageConsumable,
                consumable.ConfusionConsumable,
                consumable.ThirdEyeBlindConsumable,
                consumable.NothingConsumable
            ])()
            self.edible.description = self.spitable.description = '????'
            self.edible.parent = self.spitable.parent = self

    def solidify(self):
        self.blocks_movement = True
        self.render_order = RenderOrder.ACTOR
        if self.item_type == 'v':
            self.color = Color.player
        if self.item_type == 'y' and random.random() > 0.5:
            self.color = Color.player

    def desolidify(self):
        self.blocks_movement = False
        self.render_order = RenderOrder.ITEM
        if self.item_type == 'v':
            self.color = Color.vowel
        if self.item_type == 'y' and random.random() > 0.5:
            self.color = Color.player
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
            self.engine.message_log.add_message(f"Your ? segment breaks apart!", Color.dark_red, self.label, self.color)
            self.consume()
            self.engine.player.unsnake(i)



