from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console
from tcod.map import compute_fov
import random

from basilisk import color, tile_types
from basilisk.entity import Actor, Item
from basilisk.actions import ActionWithDirection
from basilisk.render_functions import DIRECTIONS, D_ARROWS
from basilisk.components.status_effect import ThirdEyeBlind, Petrified, PetrifEyes
from basilisk.components.ai import Statue

if TYPE_CHECKING:
    from basilisk.engine import Engine
    from basilisk.entity import Entity


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, floor_number: int, items: Iterable, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before
        self.mapped = np.full(
            (width, height), fill_value=False, order="F"
        )

        self.downstairs_location = (0, 0)
        self.floor_number = floor_number
        self.item_factories = items

    @property
    def actors(self) -> Iterable[Actor]:
        """Iterate over this maps living actors."""
        return [
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        ]

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))


    def smellable(self,entity: Entity, super_smell:bool=False):
        dx = entity.x-self.engine.player.x
        dy = entity.y-self.engine.player.y
        distance = max(abs(dx),abs(dy))

        if super_smell:
            return distance <= self.engine.foi_radius
        else:
            return distance <= self.engine.fos_radius


    def make_mapped(self):
        for i,row in enumerate(self.mapped):
            for j, tile in enumerate(row):
                if self.tiles[i,j] in (tile_types.floor, tile_types.door):
                    self.mapped[i,j] = True
                if self.tiles[i,j] == tile_types.down_stairs:
                    self.explored[i,j] = True

    
    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def get_item_at_location(self, x: int, y: int) -> Optional[Item]:
        for item in self.items:
            if item.x == x and item.y == y:
                return item

        return None

    def tile_is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        if not self.tiles["walkable"][x, y]:
            return False
        if self.get_blocking_entity_at_location(x, y):
            return False
        return True

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def print_intent(self, console: Console, entity: Actor, highlight: bool = False):
        if (
            any(isinstance(s,ThirdEyeBlind) for s in self.engine.player.statuses) or
            entity is self.engine.player or
            not isinstance(entity, Actor) or
            any(isinstance(s,Petrified) for s in entity.statuses) or
            not any(isinstance(intent, ActionWithDirection) for intent in entity.ai.intent) or
            (
                any(isinstance(s,PetrifEyes) for s in self.engine.player.statuses) and
                self.visible[entity.x,entity.y]
            )
        ):
            return

        if not self.engine.word_mode:
            self.print_enemy_fom(console,entity)
            return

        x, y = entity.xy
        bgcolor = color.intent_bg if not highlight else color.highlighted_intent_bg
        for intent in entity.ai.intent:
            x += intent.dx
            y += intent.dy
            if self.visible[entity.x, entity.y] or self.visible[x, y]:
                console.print(
                    x=x,
                    y=y,
                    string=D_ARROWS[DIRECTIONS.index((intent.dx,intent.dy))],
                    fg=color.intent,
                    bg=bgcolor
                )

    def print_enemy_fom(self, console: Console, entity: Actor):
        if not self.visible[entity.x,entity.y] and not self.smellable(entity, True):
            return

        fom = compute_fov(
            self.tiles["transparent"],
            (entity.x,entity.y),
            radius=entity.move_speed,
            light_walls=False
        )

        for x,row in enumerate(fom):
            for y,cel in enumerate(row):
                if cel and self.visible[x,y] and (x != entity.x or y != entity.y):
                    console.tiles_rgb[x,y]['bg'] = color.highlighted_fom

    def print_enemy_fov(self, console: Console, entity: Actor):
        if (
            entity is self.engine.player or
            not isinstance(entity, Actor) or
            (not self.visible[entity.x,entity.y] and not self.smellable(entity, True))
        ):
            return

        fov = compute_fov(
            self.tiles["transparent"],
            (entity.x, entity.y),
            radius=8,
            light_walls=False
        )

        for x,row in enumerate(fov):
            for y,cel in enumerate(row):
                if cel and self.visible[x,y] and (x != entity.x or y != entity.y):
                    console.tiles_rgb[x,y]['bg'] = color.highlighted_fov
                    console.tiles_rgb[x,y]['fg'] = (40,40,40)
                    #console.print(x=x,y=y,string=" ",bg=color.highlighted_fov)


    def render(self, console: Console) -> None:
        """
        Renders the map.
 
        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.tiles_rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored, self.mapped],
            choicelist=[self.tiles["light"], self.tiles["dark"], tile_types.MAPPED],
            default=tile_types.SHROUD,
            #default=self.tiles["dark"]
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            self.print_intent(console, entity)          

        # display entities
        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                if entity in self.engine.player.inventory.items:
                    if self.engine.player.is_shielded:
                        fg=color.grey
                    else:
                        fg=color.player
                else:
                    fg=entity.color
                if isinstance(entity, Actor) and entity is not self.engine.player: 
                    fov = compute_fov(
                        self.tiles["transparent"],
                        (entity.x, entity.y),
                        radius=8,
                        light_walls=False
                    )
                    if fov[self.engine.player.x, self.engine.player.y]:
                        bg = color.enemy_bg
                    else:
                        bg = None
                else:
                    bg = None
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=fg, bg=bg
                )

            elif entity in self.engine.player.inventory.items:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=color.player_dark
                )

            elif isinstance(entity, Item) and self.explored[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=color.grey
                )

            elif isinstance(entity, Actor) and self.explored[entity.x, entity.y] and isinstance(entity.ai, Statue):
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=color.grey
                )

            elif self.smellable(entity, True) and isinstance(entity, Actor):
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color, bg=color.grey
                )

            elif self.smellable(entity) and isinstance(entity, Actor):
                console.print(
                    x=entity.x, y=entity.y, string='?', fg=color.yellow, bg=color.grey
                )


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        max_monsters_per_room: int,
        max_items_per_room: int,
        current_floor: int = 0,
        ooze_factor: float,
        vault_chance: float
    ):
        from basilisk.procgen import generate_item_identities
        self.items = generate_item_identities()

        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room

        self.current_floor = current_floor
        self.ooze_factor = ooze_factor
        self.vault_chance = vault_chance

    def generate_floor(self) -> None:
        from basilisk.procgen import generate_dungeon

        self.current_floor += 1

        ooze_factor = self.ooze_factor - (0.5*self.current_floor*0.02) + (random.random()*self.current_floor*0.02)
        vault_chance = self.vault_chance + (self.current_floor*0.005)

        room_dice = max(5,self.current_floor)
        room_buffer = int(round((random.randint(1,room_dice) + random.randint(1,room_dice) + random.randint(1,room_dice))/2))

        self.engine.game_map = generate_dungeon(
            max_rooms=self.current_floor*2+room_buffer,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            max_monsters_per_room=self.max_monsters_per_room,
            max_items_per_room=self.max_items_per_room,
            engine=self.engine,
            floor_number=self.current_floor,
            items=self.items,
            ooze_factor = ooze_factor,
            vault_chance = vault_chance
        )