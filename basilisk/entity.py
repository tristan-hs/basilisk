from __future__ import annotations

import copy
import math
import random
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union, Set

from tcod.map import compute_fov

from basilisk.render_order import RenderOrder

from basilisk import color as Color

from basilisk.components.inventory import Inventory
from basilisk.components.ai import Constricted, Statue
from basilisk.components.status_effect import StatBoost, Petrified, PetrifiedSnake, PetrifEyes, Shielded, Phasing, PhasedOut, ThirdEyeBlind, Choking
from basilisk.components import consumable

from basilisk.render_functions import DIRECTIONS

from basilisk.actions import ActionWithDirection

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
        description: str = None,
        rarity: Optional[str] = None,
        flavor: str = None
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
        self.statuses=[]
        self.base_stats = {"BILE":0,"MIND":0,"TAIL":0,"TONG":0}
        self._flavor = flavor
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)
        self.unpetrified_on = 0
        self.petrified_on = 0

    @property
    def char(self):
        val = self._char if not self.is_phased_out else ' '
        return self._char

    @char.setter
    def char(self,new_val):
        self._char = new_val

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

    @property
    def BILE(self) -> int:
        return self.get_stat("BILE")

    @property
    def MIND(self) -> int:
        return self.get_stat("MIND")

    @property
    def TONG(self) -> int:
        return self.get_stat("TONG")

    @property
    def TAIL(self) -> int:
        return self.get_stat("TAIL")

    @property
    def stats(self) -> int:
        return {"BILE":self.BILE,"MIND":self.MIND,"TONG":self.TONG,"TAIL":self.TAIL}

    @property
    def is_phased_out(self) -> bool:
        return any(isinstance(s,PhasedOut) for s in self.statuses)

    @property
    def flavor(self):
        return self._flavor

    def get_word_mode_boost(self, stat:str):
        return len([i for i in self.inventory.items if i.stat == stat and i.identified]) if self.engine.word_mode else 0

    def get_status_boost(self, stat:str):
        return sum([s.amount for s in self.statuses if isinstance(s, StatBoost) and s.stat == stat])

    def get_stat(self, stat: str):
        return self.base_stats[stat] + self.get_word_mode_boost(stat) + self.get_status_boost(stat)

    def get_stat_boost_duration(self, stat: str):
        return [s for s in self.statuses if isinstance(s, StatBoost) and s.stat == stat][0].duration
    
    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        clone.id = gamemap.next_id
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

        if (
            self is self.engine.player and 
            not self.engine.game_map.tile_is_snakeable(self.x+dx,self.y+dy,phasing=False) and 
            self.is_phasing
        ):
            [s for s in self.statuses if isinstance(s,Phasing)][0].decrement(False)

        self.x += dx
        self.y += dy

        # Snake thyself
        if self is self.engine.player:
            self.snake(footprint)


    def snake(self, footprint, start_at: int = 0) -> None:
        items_to_snake = self.inventory.items[start_at:]

        for i,item in enumerate(items_to_snake):
            goto = footprint[0] - item.x, footprint[1] - item.y

            # if doesn't block + covered + isn't followed by a blocker:
            if (not item.blocks_movement and 
                self.gamemap.get_blocking_entity_at_location(*item.xy) and
                not any(j.blocks_movement for j in items_to_snake[i:])):
                break

            # if target tile is occupied:
            if self.gamemap.get_blocking_entity_at_location(*footprint):
                break

            footprint = item.xy
            item.move(*goto)

            # if not covered and doesn't block:
            if not item.blocks_movement and not self.gamemap.get_blocking_entity_at_location(*item.xy):
                item.solidify()

    def unsnake(self, start_at: int) -> None:
        self.engine.animation_beat()
        to_unsnake = self.inventory.items[start_at:]
        t = 0.24/len(to_unsnake)
        for item in to_unsnake:
            self.engine.message_log.add_message(f"Your ? segment falls off!", Color.offwhite, item.char, item.color)
            item.desolidify()
            self.engine.animation_beat(t)
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
        description: str = None,
        drop_tier: str = 'c',
        is_boss: bool = False,
        flavor: str = None
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=render_order,
            description=description,
            flavor=flavor
        )

        self.inventory = Inventory()
        self.inventory.parent = self

        self.max_char = self.base_char = char
        self.move_speed = move_speed

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.statuses = []
        self.drop_tier = drop_tier
        self.is_boss = is_boss

        self.cause_of_death = ''

    @property
    def color(self):
        if (
            any( isinstance(s,Petrified) for s in self.statuses ) or
            self.is_shielded or
            ( 
                any( isinstance(s,PetrifEyes) for s in self.engine.player.statuses ) and
                not self is self.engine.player and
                not self.is_boss
            )
        ):
            return Color.grey

        if self.is_constricted:
            return Color.statue

        return self._color

    @property
    def is_constricted(self):
        return isinstance(self.ai,Constricted)

    @property
    def is_petrified(self):
        if self is self.engine.player:
            return any(isinstance(s,PetrifiedSnake) for s in self.statuses)
        else:
            return any(isinstance(s,Petrified) for s in self.statuses)

    @color.setter
    def color(self, new_val):
        self._color = new_val

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    @property
    def is_shielded(self) -> bool:
        return any(isinstance(s, Shielded) for s in self.statuses)

    @property
    def is_phasing(self) -> bool:
        return any(isinstance(s,Phasing) for s in self.statuses)

    @property
    def is_choking(self) -> bool:
        return any(isinstance(s,Choking) for s in self.statuses)

    @property
    def in_danger(self) -> bool:
        # check if any entity intends to move into this location
        for entity in self.gamemap.actors:
            # don't check actors that can't getcha
            if(
                entity is self or
                entity.is_constricted or
                any(isinstance(s,Petrified) for s in entity.statuses) or
                any(isinstance(s,PhasedOut) for s in entity.statuses) or
                (
                    any(isinstance(s,PetrifEyes) for s in self.engine.player.statuses) and
                    self.gamemap.visible[entity.x,entity.y]
                )
            ):
                continue

            # check fom if you can't see intents
            if not self.engine.word_mode or any(isinstance(s,ThirdEyeBlind) for s in self.statuses):
                if not self.gamemap.visible[entity.x,entity.y] or entity.move_speed < 1:
                    continue

                fom = compute_fov(
                    self.gamemap.tiles["transparent"],
                    (entity.x,entity.y),
                    radius=entity.move_speed,
                    light_walls=False
                )

                for x,row in enumerate(fom):
                    for y,cel in enumerate(row):
                        if cel and self.xy == (x,y):
                            return True

            # otherwise check intents
            else:
                if not any(isinstance(intent, ActionWithDirection) for intent in entity.ai.intent):
                    continue

                x, y = entity.xy
                for intent in entity.ai.intent:
                    x += intent.dx
                    y += intent.dy
                    if self.xy == (x,y):
                        return True

        return False

    def hit_shield(self):
        [s for s in self.statuses if isinstance(s, Shielded)][0].decrement(False)

    def can_move(self):
        # Make sure player can move, otherwise die    
        for direction in DIRECTIONS:
            tile = self.x + direction[0], self.y + direction[1]
            if ( self.engine.game_map.tile_is_walkable(*tile, self.is_phasing) ) or (self is self.engine.player and self.engine.game_map.tile_is_snakeable(*tile,self.is_phasing)):
                return True

        if (self.engine.player.x, self.engine.player.y) == self.engine.game_map.downstairs_location:
            return True

        return False

    def update_constrict(self) -> None:
        new_char = int(self.base_char)-self.how_next_to_player()
        if not self.is_boss:
            new_char -= self.engine.player.TAIL
        if new_char < 0:
            self.die()
            return
        if self.is_boss and self.how_next_to_player() > 7:
            if self.engine.word_mode:
                self.engine.boss_killed = True
                return
            elif self.engine.message_log.messages[-1].text != "You hope to defeat me with this incoherent jibberish???":
                self.engine.message_log.add_message(f"You hope to defeat me with this incoherent jibberish???", Color.red)
        self.char = str(new_char)

    def pre_turn(self) -> None:
        if self.is_constricted:
            self.update_constrict()

    def on_turn(self) -> None:
        if isinstance(self.ai, Constricted):
            self.update_constrict()
        for status in self.statuses:
            status.decrement()

    def constrict(self) -> None:
        if self.is_constricted or self.name == "Decoy":
            return
        self.engine.message_log.add_message(f"You constrict the {self.name}!", Color.offwhite)
        self.ai = Constricted(self, self.ai, self.color)
        char_num = int(self.char)- (1 + self.engine.player.TAIL) if not self.is_boss else int(self.char) - 1
        if char_num < 0:
            self.die()
        else:
            self.char = str(char_num)

    def corpse(self) -> None:
        self.gamemap.bloody_floor(self.x,self.y)

        if self.name == "Decoy":
            return

        my_factor = (int(self.char) + self.move_speed + 1)*0.1

        # 0.16 + (0.64 * factor) = chance of corpsing
        #if (random.random() > my_factor and random.random() > 0.2) or random.random() > 0.8:
        #    return

        my_drops = []
        for i in self.gamemap.item_factories:
            factor = Item.letters()[i.char]
            additions = [i] * factor if i.rarity != self.drop_tier else [i] * (factor+2) * (factor+2)
            my_drops += additions

        random.choice(my_drops).spawn(self.gamemap,self.x,self.y)

    def die(self) -> None:
        self.ai = None
        if self.engine.player is self:
            death_message = "You died!"
            death_message_color = Color.dark_red
            self.char = "%"
            self.color = Color.corpse
            self.name = f"remains of {self.name}"
            self.render_order = RenderOrder.CORPSE
        else:
            death_message = f"{self.name} is dead!"
            death_message_color = Color.dark_red

            self.engine.history.append(("kill enemy",self.name,self.engine.turn_count))

            if self in self.gamemap.entities:
                self.gamemap.entities.remove(self)

            if self.is_boss:
                self.engine.boss_killed = True
            else:
                self.corpse()

        self.engine.message_log.add_message(death_message, death_message_color)

    def take_damage(self, amount: int) -> None:
        if self.name == "Decoy" or self.is_boss:
            return
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
            if self.is_shielded:
                self.hit_shield()
                return
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
        description: str = None,
        rarity: Optional[str] = None,
        stat: str,
        flavor: str = None
    ):
        super().__init__(
            x=x,
            y=y,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
            description=description,
            rarity=rarity,
            flavor=flavor
        )
        self.item_type = item_type
        self.edible = edible
        self.spitable = spitable
        self.spitable.parent = self
        self.edible.parent = self
        self._identified = False
        self._color = color
        self.rarity = rarity
        self.stat = stat
        self.is_boss = False

    @property
    def label(self):
        return self.name if self.identified else self.char

    @property
    def identified(self):
        if self.item_type != 'c':
            return True
        if self.gamemap.game_mode in ['consumable testing','boss testing']:
            return True
        return [i for i in self.gamemap.item_factories if i.char == self.char][0]._identified

    @property
    def flavor(self):
        return self._flavor if self.identified else "An obnubliated segment of stitious potential. Destroy it to reify its ilk."

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
        self.engine.history.append(("identify item", self.label, self.engine.turn_count))
        self.engine.message_log.add_message(f"The {self.char} was a{n} ? segment.", Color.offwhite, self.label, self.color)

    @property
    def color(self):
        if not self.identified:
            return Color.unidentified
        return self._color

    @property
    def description(self):
        return self._description

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
        'y':1,
        'z':1
    }

    def preSpawn(self):
        if self.item_type == 'v':
            self.char = random.choice(['a','e','i','o','u']*2 + ['y'])

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
        self.gamemap.entities.remove(self)
        if self in self.engine.player.inventory.items:
            self.engine.player.inventory.items.remove(self)
        self.engine.check_word_mode()

    def take_damage(self, amount: int):
        player = self.gamemap.engine.player

        if self in player.inventory.items:
            if player.is_shielded:
                player.hit_shield()
                return
            i = player.inventory.items.index(self)
            self.engine.message_log.add_message(f"Your ? segment breaks apart!", Color.dark_red, self.label, self.color)
            self.consume()
            self.identified = True
            self.engine.player.unsnake(i)
            self.engine.history.append(("break item",f"{self.name} ({self.char})",self.engine.turn_count))
        
        else:
            self.gamemap.entities.remove(self)

    def die(self):
        self.take_damage(1)

