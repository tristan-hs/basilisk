
# place entities map-wide at the end

# write generate_final_maze

# 6x6 = 0-1 -- maybe each 6x6 chunk has 0-2 monsters w/ 0 in room 1 and w/ 1-3 in vaults?
# so for chunk in chunks:
	# if there's a valid vault section
		# put a monster there for sure
		# put an item there for sure

	# now, twice:
		# try to place a monster at random
		# if the tile has anything there already, move on (wall, door, stairs, vault foyer, etc)
		# if the tile is w/in sight of the player, move on

	# try to place an item, same principle goes

	# maybe add a chance to autofail to both of the above

""" boss placement code
engine.boss = entity_factories.final_boss.spawn(dungeon,center_of_last_room[0],center_of_last_room[1])
dungeon.tiles[rooms[-1].inner] = tile_types.boss_vault_floor 
"""  


from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING, Iterable

import tcod
import math
import numpy
import copy
import random

from basilisk.entity import Item

from basilisk import entity_factories, tile_types
from basilisk.game_map import GameMap

if TYPE_CHECKING:
	from basilisk.engine import Engine


class RectangularRoom:
	def __init__(self, x: int, y: int, x_dir: int, y_dir: int, map_width: int, map_height: int, rooms: List, room_max_size: int, room_min_size: int, door2: Tuple[int,int]):
		self.door = (x, y)
		self.x1 = self.x2 = self.door[0]
		self.y1 = self.y2 = self.door[1]
		self.is_vault = False
		self.map_width = map_width
		self.map_height = map_height
		self.rooms = rooms
		self.tunnels = []
		self.door2 = door2
		self.room_min_size = room_min_size
		self.room_max_size = room_max_size

		target = random.choice(range(room_min_size,room_max_size+1))
		target_area = self.target_area = target*target

		# while there's room to grow
		while self.area < target_area:
			# collect possible growth directions
			growths = []
			for d in ((0,-1),(0,1),(-1,0),(1,0)):
				if (
					(d[0]+x_dir, d[1]+y_dir) == (0,0) or
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

	@property
	def area(self):
		return self.width * self.height

	@property
	def valid(self):
		return (
			# not <4 length corridors
			not any(i < 5 for i in [self.width,self.height]) and 
			# we got to the right size
			self.area >= self.target_area and
			# main door isn't a corner door
			(
				self.door[0] not in [self.x1,self.x2] or
				self.door[1] not in [self.y1,self.y2]
			)
		)

	@property
	def is_vault_worthy(self):
		return (
			self.width > 6 and 
			self.height > 6 and 
			(
				self.door[0] in range(self.x1,self.x2)[3:-3] or
				self.door[1] in range(self.y1,self.y2)[3:-3]
			) and
			(
				not self.has_tile(self.door2) or
				(
					self.door2[0] in range(self.x1,self.x2)[3:-3] or
					self.door2[1] in range(self.y1,self.y2)[3:-3]
				)
			)
		)

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
		# d_dir is the direction from the door into the room
		d = self.door
		if d[0] == self.x1:
			d_dir = (2,0)
		if d[0] == self.x2:
			d_dir = (-2,0)
		if d[1] == self.y1:
			d_dir = (0,2)
		if d[1] == self.y2:
			d_dir = (0,-2)

		# b_dir is the direction the barrier grows in -- perpindicular to d_dir
		b_dir = 0 if d_dir[0] == 0 else 1
		# we'll start off 2 in from the door
		b_start = (d[0]+d_dir[0],d[1]+d_dir[1])

		if b_dir == 0:
			barrier = slice(self.x1+2,self.x2-1), slice(b_start[1],b_start[1]+1)
		else:
			barrier = slice(b_start[0],b_start[0]+1), slice(self.y1+2,self.y2-1)

		self.barrier = barrier


class Tunnel(RectangularRoom):
	def __init__(self, tunnel: List):
		self.is_vault = False

		self.x1 = min(c[0] for c in tunnel)-1
		self.x2 = max(c[0] for c in tunnel)+1
		self.y1 = min(c[1] for c in tunnel)-1
		self.y2 = max(c[1] for c in tunnel)+1


def generate_item_identities():
	letters = Item.letters()

	letters_weighted = []
	for k,v in letters.items():
		if k == 'y':
			continue
		letters_weighted += [k]*v

	all_items = []
	letters_weighted.sort(key=lambda l:letters[l]+random.random())

	# assign letters to items + print list
	while len(letters_weighted) > 0:
		item_fs = entity_factories.c_segments[:]
		random.shuffle(item_fs)
		for i in item_fs:
			letters_weighted_thirds = numpy.array_split(letters_weighted,3)
			third = letters_weighted_thirds[{'r':0,'u':1,'c':2}[i.rarity]]
			
			char = random.choice(third) if len(third) > 0 else random.choice(letters_weighted)

			item = Item(
				item_type='c',
				color=i._color,
				name=i.name,
				edible=copy.deepcopy(i.edible),
				spitable=copy.deepcopy(i.spitable),
				rarity=i.rarity,
				stat=i.stat,
				flavor=i._flavor
			)
			item.edible.parent = item.spitable.parent = item
			item.char = char
			all_items.append(item)
			letters_weighted = [l for l in letters_weighted if l != item.char]

			if len(letters_weighted) == 0:
				if not any(i.char == 'y' for i in all_items):
					letters_weighted = ['y']
				else:
					break

	return all_items


class MazeCell():
	def __init__(self,maze,x,y):
		self.L = self.R = self.U = self.D = self.visited = False
		self.x = x
		self.y = y
		self.maze = maze
		self.char_override = None

	def step_to(self,other):
		x = self.x - other.x
		y = self.y - other.y
		if x < 0: 
			self.R = other.L = True
		if x > 0:
			self.L = other.R = True
		if y < 0:
			self.D = other.U = True
		if y > 0:
			self.U = other.D = True
		other.visited = True

	@property
	def neighbors(self):
		dirs = [(0,1),(0,-1),(1,0),(-1,0)]
		n = []
		for d in dirs:
			cell = self.x + d[0], self.y + d[1]
			if cell[0] < 0 or cell[1] < 0 or cell[0] >= self.maze.width or cell[1] >= self.maze.height:
				continue
			cell = self.maze.cells[cell[0]][cell[1]]
			n.append(cell)
		return n

	@property
	def unvisited_neighbors(self):
		return [i for i in self.neighbors if not i.visited]

	@property
	def visited_neighbors(self):
		return [i for i in self.neighbors if i.visited]

	@property
	def chunk(self):
		dirs = [self.L,self.R,self.U,self.D]
		if dirs in [
			[True,True,False,False],
			[False,True,False,True],
			[True,True,False,True],
			[False,True,False,False]
		]:
			return ["xxxxx",".....",".....",".....","....."]

		if dirs in [
			[True,False,False,True],
			[True,False,False,False],
			[False,False,False,True]
		]:
			return ["xxxxx","....x","....x","....x","....x"]

		if dirs in [
			[False,True,True,False],
			[True,True,True,False],
			[False,True,True,True],
			[True,True,True,True]
		]:
			return ["....x",".....",".....",".....","....."]

		if dirs in [
			[True,False,True,False],
			[False,False,True,True],
			[True,False,True,True],
			[False,False,True,False]
		]:

			return ["....x","....x","....x","....x","....x"]

	def solidify(self,dungeon):
		for y,row in enumerate(self.chunk):
			for x,tile in enumerate(row):
				cx = self.x*5 + x + 1
				cy = self.y*5 + y

				dungeon.tiles[(cx,cy)] = tile_types.wall if tile == 'x' else tile_types.floor

	@property
	def map_coords(self):
		return (self.x*5+3,self.y*5+2)


	@property
	def char(self):
		if self.char_override:
			return self.char_override
		
		dirs = [self.L,self.R,self.U,self.D]
		
		if dirs == [True,True,True,True]:
			return '╬'
		if dirs == [False,True,True,False]:
			return '╚'
		if dirs == [False,True,False,True]:
			return '╔'
		if dirs == [True,True,True,False]:
			return '╩'
		if dirs == [True, True, False, True]:
			return '╦'
		if dirs == [False,True,True,True]:
			return '╠'
		if dirs == [True,True,False,False]:
			return '═'
		if dirs == [True,False,True,True]:
			return '╣'
		if dirs == [False,False,True,True]:
			return '║'
		if dirs == [True,False,False,True]:
			return '╗'
		if dirs == [True,False,True,False]:
			return '╝'
		if dirs == [True,False,False,False]:
			return '╡'
		if dirs == [False,True,False,False]:
			return '╞'
		if dirs == [False,False,True,False]:
			return '╨'
		if dirs == [False,False,False,True]:
			return '╥'
		if dirs == [False,False,False,False]:
			return 'x'


class Maze():
	def __init__(self, maze_width, maze_height):
		self.width = maze_width
		self.height = maze_height
		# grid of cells
		self.cells = [[MazeCell(self,x,y) for y in range(maze_height)] for x in range(maze_width)]
		self.last_cell = self.start = self.cells[random.choice(range(maze_width))][random.choice(range(maze_height))]
		self.start.visited = True
		self.start.char_override = 'S'

		self.path = []

		while len(self.unvisited_cells):
			start = self.last_good_cell if not len(self.last_cell.unvisited_neighbors) else self.last_cell
			if start == self.start and True in [start.L,start.R,start.U,start.D]:
				break
			step = random.choice(start.unvisited_neighbors)
			start.step_to(step)
			self.last_cell = step
			self.path += [step]

			# random branching to existing places
			if random.random() < 0.1 and len(step.visited_neighbors) > 1:
				step.step_to(random.choice(step.visited_neighbors))


			# self.print()
			# time.sleep(0.01)

		self.last_cell.char_override = 'E'

		# self.print()


	@property
	def last_good_cell(self):
		for i in reversed(self.path):
			if len(i.unvisited_neighbors):
				return i
		return self.path[0]


	@property
	def unvisited_cells(self):
		return [cell for row in self.cells for cell in row if not cell.visited]

	@property
	def visited_cells(self):
		return [cell for row in self.cells for cell in row if cell.visited]

	@property
	def viable_cells(self):
		return [cell for cell in self.visited_cells if len(cell.unvisited_neighbors)]

	@property
	def rows(self):
		return [list(i) for i in list(zip(*self.cells))]

	def print(self):
		print('='*self.width)
		for row in self.rows:
			print( ''.join([cell.char for cell in row]) )
		print('='*self.width)

def generate_maze(floor_number,map_width,map_height,engine,items):
	player = engine.player
	entities = set(player.inventory.items)
	entities.update([player])
	dungeon = GameMap(engine, map_width, map_height, floor_number, entities=entities, items=items, vowel=entity_factories.vowel_segment, decoy=entity_factories.decoy)

	maze_width = math.floor((map_width-1)/5)
	maze_height = math.floor((map_height-1)/5)
	maze = Maze(maze_width//2,maze_height)
	start = maze.start.map_coords
	end = maze.last_cell.map_coords

	for row in maze.rows:
		for cell in row:
			cell.solidify(dungeon)

	player.place(*start,dungeon)
	dungeon.upstairs_location = start
	for item in player.inventory.items:
		item.blocks_movement = False
		item.place(*start,dungeon)

	dungeon.tiles[end] = tile_types.down_stairs
	dungeon.downstairs_location = end

	return dungeon



def generate_dungeon(
	floor_number: int,
	map_width: int,
	map_height: int,
	engine: Engine,
	items: Iterable,
) -> GameMap:
	"""Generate a new dungeon map"""

	if floor_number == 6:
		return generate_maze(floor_number,map_width,map_height,engine,items)
	if floor_number == 10:
		return generate_final_maze(floor_number,map_width,map_height,engine,items)

	# set a bunch of parameters based on the given arguments
	room_range = {
		1:(4,5), 2:(5,6), 3:(5,6), 4:(6,7), 5:(5,6), 7:(12,13), 8:(6,7), 9:(8,9)
	}[floor_number]
	room_target = random.choice(range(room_range[0],room_range[1]+1))

	rooms_chain = floor_number == 1

	small, msmall, mlarge, large, varied = ((6,8),(8,9),(9,10),(10,13),(6,13))
	room_min_size, room_max_size = {
		1:msmall, 2:msmall, 3:mlarge, 4:varied, 5:large, 7:small, 8:large, 9:varied
	}[floor_number]

	snakestone_door_chance = {
		1:1, 2:1, 3:0, 4:0, 5:0, 7:0.15, 8:0.15, 9:0.15, 10:0
	}[floor_number]

	player = engine.player
	entities = set(player.inventory.items)
	entities.update([player])
	dungeon = GameMap(engine, map_width, map_height, floor_number, entities=entities, items=items, vowel=entity_factories.vowel_segment, decoy=entity_factories.decoy)

	rooms: List[RectangularRoom] = []
	vaults: List[RectangularRoom] = []

	center_of_last_room = (0,0)
	attempts = 0

	vault_count = 0
	vault_targets = [0]
	if floor_number > 1:
		vault_targets += [1]
	if floor_number > 5:
		vault_targets += [2]
	vault_target = random.choice(vault_targets)
	vault_chance = 1 / (4-vault_target)

	max_attempts = 10000

	while len(rooms) < room_target and attempts < max_attempts:
		attempts += 1
		# if this is the first room, start at a random point at least 2 away from the borders of the map
		if len(rooms) == 0:
			x = random.choice(range(map_width)[2:-2])
			y = random.choice(range(map_height)[2:-2])
			x_dir = y_dir = 0
			door2 = None
		else:
			other_room = random.choice(rooms) if not rooms_chain else rooms[-1]
			# heads: put a door in the top or bottom
			if random.random() < 0.5:
				# pick randomly from the x coords less the corners
				options = list(range(other_room.x1, other_room.x2)[1:-1])
				random.shuffle(options)
				x = options.pop()
				x2 = options.pop()
				# choose top or bottom wall
				y = random.choice([other_room.y1, other_room.y2])
				# other room grows in either x direction
				x_dir = 0
				# other room grows in the chosen y direction only
				y_dir = -1 if y == other_room.y1 else 1
				# connect all rooms via 2 doors where possible
				door2 = (x2,y)

			# tails: put a door in the left or right
			# same process swapping x and y
			else:
				options = list(range(other_room.y1, other_room.y2)[1:-1])
				random.shuffle(options)
				y = options.pop()
				y2 = options.pop()
				x = random.choice([other_room.x1,other_room.x2])
				y_dir = 0
				x_dir = -1 if x == other_room.x1 else 1
				door2 = (x,y2)

		# generate a room with the chosen parameters
		room = RectangularRoom(x, y, x_dir, y_dir, map_width, map_height, rooms+vaults, room_max_size, room_min_size, door2)
		if not room.valid:
			continue

		# if this is the first room, place the player here
		if len(rooms) == 0:
			dungeon.tiles[room.inner] = tile_types.floor
			player.place(*room.center,dungeon)
			dungeon.upstairs_location = room.center
			for item in player.inventory.items:
				item.blocks_movement = False
				item.place(*room.center,dungeon)

		else:
			room.is_vault = random.random() < vault_chance and room.is_vault_worthy and vault_count < vault_target
			# make this into a vault if the dice say so
			if room.is_vault:
				room.vaultify()
				dungeon.tiles[room.inner] = tile_types.vault_floor
				dungeon.tiles[room.door[0],room.door[1]] = tile_types.vault_floor
				dungeon.tiles[room.barrier] = tile_types.wall
				vault_count += 1
			# otherwise build the room on the map normally
			else:
				dungeon.tiles[room.inner] = tile_types.floor
				door_tile = tile_types.floor if random.random() > snakestone_door_chance else tile_types.snake_only
				dungeon.tiles[room.door[0],room.door[1]] = door_tile
				if room.door2 and room.has_tile(room.door2):
					dungeon.tiles[room.door2[0],room.door2[1]] = door_tile

		if not room.is_vault:
			center_of_last_room = room.center
			rooms.append(room)
		else:
			vaults.append(room)

	# start over if this attempt was botched
	if attempts == max_attempts:
		return generate_dungeon(floor_number,map_width,map_height,engine,items)

	dungeon.tiles[center_of_last_room] = tile_types.down_stairs
	dungeon.downstairs_location = center_of_last_room

	return dungeon    

def generate_consumable_testing_ground(engine,items, has_boss=False):
	# wide open space with all consumables scattered around
	player = engine.player
	entities = set(player.inventory.items)
	entities.update([player])
	dungeon = GameMap(engine, 76, 40, 1, entities=entities, items=items, vowel=entity_factories.vowel_segment, decoy=entity_factories.decoy, game_mode='consumable testing')
	rooms: List[RectangularRoom] = []
	vaults: List[RectangularRoom] = []
	center_of_last_room = (0, 0)
	attempts = 0

	x = int(76/2)
	y = int(40/2)
	x_dir = y_dir = 0
	door2 = None

	attempts = 0
	while attempts < 1000:
		attempts += 1
		room = RectangularRoom(x, y, x_dir, y_dir, 76, 40, [], 35, 30, 0.9, door2)
		if room.width < 30 or room.height < 30:
			continue
		else:
			break

	dungeon.tiles[room.inner] = tile_types.floor
	player.place(*room.center, dungeon)
	dungeon.upstairs_location = room.center
	for item in player.inventory.items:
		item.blocks_movement = False
		item.place(*room.center, dungeon)

	factory_set = dungeon.item_factories + ([entity_factories.vowel_segment]*5)

	if has_boss:
		engine.boss = entity_factories.final_boss.spawn(dungeon,room.x2-2,room.y2-2)
		factory_set *= 2

	for i in factory_set:
		attempts = 0
		while attempts < 1000:
			attempts += 1
			x = random.randint(room.x1+1,room.x2-1)
			y = random.randint(room.y1+1,room.y2-1)

			if any(entity.xy == (x,y) for entity in dungeon.entities):
				continue

			i.spawn(dungeon,x,y)
			break

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
	room: RectangularRoom, dungeon: GameMap, maximum_monsters: int, maximum_items: int, first_room: bool
) -> None:


	enemy_set = entity_factories.enemy_sets[dungeon.floor_number-1][:]
	monster_points = 0
	factor = dungeon.floor_number+1

	if random.random() > 0.3:
		monster_points += factor
		if random.random() > 0.3 or dungeon.floor_number < 4:
			monster_points *= factor
			if random.random() > 0.3 or dungeon.floor_number < 3:
				monster_points += factor

	if room.is_vault:
		monster_points += random.randint(1,factor*factor)
		if entity_factories.enemy_sets[dungeon.floor_number]:
			enemy_set.append(random.choice(entity_factories.enemy_sets[dungeon.floor_number]))

	def calc_mp(monster):
		return int(monster.char) * monster.move_speed + 1

	attempts = 0
	monsters = 0
	while monster_points > min(calc_mp(p) for p in enemy_set) and attempts < 1000 and monsters < maximum_monsters:
		attempts += 1
		monster = random.choice(enemy_set)
		mp = calc_mp(monster)
		if mp > monster_points:
			continue

		x = random.randint(room.x1 + 1, room.x2-1)
		y = random.randint(room.y1+1, room.y2-1)

		# nothing else is there and the space is out of fov of the stairs
		if not any(entity.x == x and entity.y == y for entity in dungeon.entities) and max(abs(dungeon.upstairs_location[0]-x),abs(dungeon.upstairs_location[1]-y)) > 9:
			monster.spawn(dungeon,x,y)
			monster_points -= calc_mp(monster)
			monsters += 1


	item_points = 0
	if random.random() < 0.4 or first_room:
		item_points = 1

	if room.is_vault:
		item_points += random.randint(1,factor)
		factory_set = dungeon.item_factories
	else:
		factory_set = [entity_factories.vowel_segment]

	attempts = 0
	while item_points > 0 and attempts < 1000:
		attempts += 1

		x = random.randint(room.x1 + 1, room.x2 - 1)
		y = random.randint(room.y1 + 1, room.y2 - 1)

		if dungeon.tiles[x,y] == tile_types.down_stairs:
			continue

		if dungeon.engine.player.xy == (x,y):
			continue

		if not any(entity.x == x and entity.y == y and isinstance(entity, Item) for entity in dungeon.entities):
			item = random.choice(factory_set)
			cost = {'c':1,'u':2,'r':3}[item.rarity] if item.rarity else 1
			if cost > item_points:
				continue
			item.spawn(dungeon,x,y)
			item_points -= cost

