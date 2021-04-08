from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING, Iterable

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine


class RectangularRoom:
    def __init__(self, x: int, y: int, x_dir: int, y_dir: int, map_width: int, map_height: int, rooms: List, room_max_size: int, room_min_size: int, ooze_factor: int):
        self.door = (x, y)
        ooze_juice = [1,1]
        self.ooze_factor = ooze_factor
        self.x1 = self.x2 = self.door[0]
        self.y1 = self.y2 = self.door[1]
        self.is_vault = False
        self.map_width = map_width
        self.map_height = map_height
        self.rooms = rooms
        self.tunnels = []

        # while there's room to grow
        while self.width < room_max_size and self.height < room_max_size:
            # collect possible growth directions
            growths = []
            for d in ((0,-1),(0,1),(-1,0),(1,0)):
                if (
                    (d[0]+x_dir, d[1]+y_dir) == (0,0) or
                    (d[0] != 0 and ooze_juice[0] == 0) or
                    (d[1] != 0 and ooze_juice[1] == 0) or
                    (d[0] < 0 and self.x1 < 1) or
                    (d[0] > 0 and self.x2 >= map_width-1) or
                    (d[1] < 0 and self.y1 < 1) or
                    (d[1] > 0 and self.y2 >= map_height-1)
                ):
                    continue

                x1 = self.x1 if d[0] > -1 else self.x1-1
                x2 = self.x2 if d[0] < 1 else self.x2+1
                y1 = self.y1 if d[1] > -1 else self.y1-1
                y2 = self.y2 if d[1] < 1 else self.y2+1

                if (x1, x2, y1, y2) == (self.x1, self.x2, self.y1, self.y2):
                    break

                if any(self.would_intersect(x1, x2, y1, y2, room) for room in rooms):
                    continue

                growths.append([x1,x2,y1,y2])

            # if there aren't any, quit
            if len(growths) < 1:
                break

            growth = random.choice(growths)

            # deplete the ooze
            if (growth[0] != self.x1 or growth[1] != self.x2) and growth[1] - growth[0] >= room_min_size:
                if random.random() > ooze_juice[0]:
                    ooze_juice[0] = 0
                ooze_juice[0] *= ooze_factor

            if (growth[2] != self.y1 or growth[3] != self.y2) and growth[3] - growth[2] >= room_min_size:
                if random.random() > ooze_juice[1]:
                    ooze_juice[1] = 0
                ooze_juice[1] *= ooze_factor

            # grow
            self.x1, self.x2, self.y1, self.y2 = growth

    
    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y
    
    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1

    def has_tile(self, tile):
        return (
            self.x1 <= tile[0] and
            self.x2 >= tile[0] and
            self.y1 <= tile[1] and
            self.y2 >= tile[1]
        )

    def would_intersect(self, x1, x2, y1, y2, other):
        return(
            x1 < other.x2 and
            x2 > other.x1 and
            y1 < other.y2 and
            y2 > other.y1
        )

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 < other.x2
            and self.x2 > other.x1
            and self.y1 < other.y2
            and self.y2 > other.y1
        )

    def vaultify(self):
        # try to move
        ooze_juice = 1
        while ooze_juice == 1:
            moves = []
            for d in [[-1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,1]]:               
                x1 = self.x1 + d[0] + d[1]
                x2 = self.x2 + d[0] + d[1]
                y1 = self.y1 + d[2] + d[3]
                y2 = self.y2 + d[2] + d[3]

                if (x1, x2, y1, y2) == (self.x1, self.x2, self.y1, self.y2):
                    break

                if x1 < 0 or y1 < 0 or x2 >= self.map_width or y2 >= self.map_height:
                    continue

                if any(self.would_intersect(x1,x2,y1,y2, room) for room in self.rooms):
                    continue

                moves.append([x1,x2,y1,y2])

            if len(moves) < 1:
                break

            move = random.choice(moves)

            if random.random() > ooze_juice:
                ooze_juice = 0
            ooze_juice *= self.ooze_factor

            self.x1, self.x2, self.y1, self.y2 = move

        # tunnel to a room
        tunnel_to = self.rooms[:]
        random.shuffle(tunnel_to)
        for room in tunnel_to:
            tunnel1 = []
            tunnel2 = []
            dx = dy = 0
            if room.x2 < self.x1:
                dx -= 1
            if room.x1 > self.x2:
                dx += 1
            if room.y2 < self.y1:
                dy -= 1
            if room.y1 > self.y2:
                dy += 1

            if dx == 0 and dy == 0:
                continue

            if (dx != 0 and dy != 0 and random.random() < 0.5) or dx == 0:
                x = random.choice(range(self.x1, self.x2)) if dx != 0 else random.choice(range(
                    max(self.x1,room.x1),
                    min(self.x2,room.x2)+1
                ))
                y = self.y1 if dy < 0 else self.y2
                
                door = (x, y)
                
                if any(room.has_tile(self.door) for room in self.rooms):
                    continue

                while y > room.y2 or y < room.y1:
                    tunnel1.append((x, y))
                    y += dy
                    if any(room.has_tile((x,y)) for room in self.rooms):
                        break

                tunnel1.append((x, y))

                while x > room.x2 or x < room.x1:
                    x += dx
                    tunnel2.append((x, y))
                    if any(room.has_tile((x,y)) for room in self.rooms):
                        break

            else:
                y = random.choice(range(self.y1, self.y2)) if dy != 0 else random.choice(range(
                    max(self.y1,room.y1),
                    min(self.y2,room.y2)+1
                ))
                x = self.x1 if dx < 0 else self.x2
                self.door = (x, y)

                if any(room.has_tile((x,y)) for room in self.rooms):
                    continue

                while x > room.x2 or x < room.x1:
                    tunnel1.append((x, y))
                    x += dx
                    if any(room.has_tile((x,y)) for room in self.rooms):
                        break

                tunnel1.append((x,y))

                while y > room.y2 or y < room.y1:
                    y += dy
                    tunnel2.append((x, y))
                    if any(room.has_tile((x,y)) for room in self.rooms):
                        break

            if len(tunnel1) > 0:
                t1 = Tunnel(tunnel1)
                self.tunnels.append(t1)

            if len(tunnel2) > 0:
                t2 = Tunnel(tunnel2)
                self.tunnels.append(t2)

            if len(tunnel1) > 0 or len(tunnel2) > 0:
                break


class Tunnel(RectangularRoom):
    def __init__(self, tunnel: List):
        self.is_vault = False

        self.x1 = min(c[0] for c in tunnel)-1
        self.x2 = max(c[0] for c in tunnel)+1
        self.y1 = min(c[1] for c in tunnel)-1
        self.y2 = max(c[1] for c in tunnel)+1


def generate_item_identities():
    cons = entity_factories.consonants[:]
    random.shuffle(cons)
    items = entity_factories.c_segments[:]
    for i in items:
        i.char = cons.pop()
    return items

def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    max_monsters_per_room: int,
    max_items_per_room: int,
    engine: Engine,
    floor_number: int,
    items: Iterable,
    ooze_factor: int,
    vault_chance: float
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player

    entities = set(player.inventory.items)
    entities.update([player])
    dungeon = GameMap(engine, map_width, map_height, floor_number, entities=entities, items=items)

    rooms: List[RectangularRoom] = []
    vaults: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        # unless this is the first room, pick a point adjacent to another room
        if len(rooms) == 0:
            x = int(map_width/2) if map_width % 2 == 0 else int((map_width-1)/2)
            y = int(map_height/2) if map_height % 2 == 0 else int((map_height-1)/2)
            x_dir = y_dir = 0
        else:
            other_room = random.choice(rooms)
            if random.random() < 0.5:
                # top or bottom
                x = random.choice(range(other_room.x1, other_room.x2))
                y = random.choice([other_room.y1, other_room.y2])
                x_dir = 0
                y_dir = -1 if y == other_room.y1 else 1
            else:
                # left or right
                x = random.choice([other_room.x1, other_room.x2])
                y = random.choice(range(other_room.y1, other_room.y2))
                x_dir = -1 if x == other_room.x1 else 1
                y_dir = 0

        room = RectangularRoom(x, y, x_dir, y_dir, map_width, map_height, rooms+vaults, room_max_size, room_min_size, ooze_factor)

        if room.width < room_min_size or room.height < room_min_size:
            continue

        if len(rooms) == 0:
            dungeon.tiles[room.inner] = tile_types.floor
            player.place(*room.center, dungeon)
            for item in player.inventory.items:
                item.blocks_movement = False
                item.place(*room.center, dungeon)
        else:
            room.is_vault = random.random() < vault_chance
            if room.is_vault:
                room.vaultify()
                dungeon.tiles[room.inner] = tile_types.vault_floor
                for t in room.tunnels:
                    dungeon.tiles[t.inner] = tile_types.vault_floor
                    rooms.append(t)
                dungeon.tiles[room.door[0],room.door[1]] = tile_types.vault_floor
            else:
                dungeon.tiles[room.inner] = tile_types.floor
                dungeon.tiles[room.door[0],room.door[1]] = tile_types.door

        if not room.is_vault:
            center_of_last_room = room.center

        monsters = 0 if len(rooms) == 0 else max_monsters_per_room
        place_entities(room, dungeon, monsters, max_items_per_room)

        if room.is_vault:
            vaults.append(room)
        else:
            rooms.append(room)
    
    dungeon.tiles[center_of_last_room] = tile_types.down_stairs
    dungeon.downstairs_location = center_of_last_room

    return dungeon

def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y

def place_entities(
    room: RectangularRoom, dungeon: GameMap, maximum_monsters: int, maximum_items: int
) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)
    number_of_items = random.randint(0, maximum_items)
    min_monster = dungeon.floor_number-1
    max_monster = dungeon.floor_number*2

    if room.is_vault:
        number_of_monsters += 1
        number_of_items += 1
        min_monster += 1
        max_monster += 1

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        factory = random.choice(entity_factories.enemies[max(0,min_monster):min(10,max_monster)])

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            factory.spawn(dungeon, x, y)

    for i in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if dungeon.tiles[x,y] == tile_types.down_stairs:
            continue

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random.random() > 0.9:
                entity_factories.y_segment.spawn(dungeon,x,y)
            else:
                entity_factories.vowel_segment.spawn(dungeon,x,y)

