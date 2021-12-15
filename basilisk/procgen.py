from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING, Iterable

import tcod
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

			# foyer = (barrier w/o edges trimmed) + (same thing minus 1/2 b_dir)
			fx = range(self.x1,self.x2)
			f_dir = (-1,0) if d_dir[1] == 2 else (0,1)
			fy = range(b_start[1]+f_dir[0]-1,b_start[1]+f_dir[1]+1)


		else:
			barrier = slice(b_start[0],b_start[0]+1), slice(self.y1+2,self.y2-1)
			
			f_dir = (-1,0) if d_dir[0] == 2 else (0,1)
			fx = range(b_start[0]+f_dir[0]-1,b_start[0]+f_dir[1]+1)
			fy = range(self.y1,self.y2)

		self.barrier = barrier
		self.foyer = [(x,y) for y in fy for x in fx]
		print(self.foyer)


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
				cx = self.x*5 + x + self.maze.x_offset
				cy = self.y*5 + y + self.maze.y_offset
				floor_tile = tile_types.floor if not self.maze.boss_maze else tile_types.boss_vault_floor

				dungeon.tiles[(cx,cy)] = tile_types.wall if tile == 'x' else tile_types.floor

	@property
	def map_coords(self):
		return ((self.x*5)+2+self.maze.x_offset,(self.y*5)+2+self.maze.y_offset)


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
	def __init__(self, maze_width, maze_height, x_offset=1, y_offset=0, ends_at_edge=False, boss_maze=False):
		self.width = maze_width
		self.height = maze_height
		self.x_offset = x_offset
		self.y_offset = y_offset
		self.boss_maze = boss_maze
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

		if ends_at_edge:
			x = random.choice([0,maze_width-1])
			y = random.choice(range(maze_height))
			self.last_cell = self.cells[x][y]

			x = maze_width-1 if x == 0 else 0
			y = random.choice(range(maze_height))
			self.start = self.cells[x][y]

		self.last_cell.char_override = 'E'

		# self.print()

	@property
	def x1(self):
		return self.x_offset-1

	@property
	def x2(self):
		return self.x1 + (self.width*5)

	@property
	def y1(self):
		return self.y_offset

	@property
	def y2(self):
		return self.y1 + (self.height*5)


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

	maze_width = (map_width-1)//10
	maze_height = (map_height-1)//5
	maze_x_offset = (map_width//2) - ((maze_width*5)//2)
	maze = Maze(maze_width,maze_height,maze_x_offset)
	start = maze.start.map_coords
	end = maze.last_cell.map_coords

	for row in maze.rows:
		for cell in row:
			cell.solidify(dungeon)

	place_player(dungeon,start,player)
	dungeon.upstairs_location = start

	dungeon.tiles[end] = tile_types.down_stairs
	dungeon.downstairs_location = end

	place_entities(dungeon,map_width,map_height)
	return dungeon

def generate_final_maze(floor_number,map_width,map_height,engine,items):
	player = engine.player
	entities = set(player.inventory.items)
	entities.update([player])
	dungeon = GameMap(engine, map_width, map_height, floor_number, entities=entities, items=items, vowel=entity_factories.vowel_segment, decoy=entity_factories.decoy)

	maze_width = ((map_width-1)//10) + random.choice([0,1,2,3])
	maze_height = ((map_height-1)//5) - 2
	maze_x_offset = (map_width//2) - ((maze_width*5)//2)
	maze_y_offset = (map_height//2) - ((maze_height*5)//2)

	maze = Maze(maze_width,maze_height,maze_x_offset,maze_y_offset,ends_at_edge=True,boss_maze=True)
	start = maze.start.map_coords
	end = maze.last_cell.map_coords

	for row in maze.rows:
		for cell in row:
			cell.solidify(dungeon)

	dungeon.downstairs_location = start
	engine.boss = entity_factories.final_boss.spawn(dungeon,*start)

	room_target = 99
	rooms_chain = False
	room_min_size, room_max_size = (6,13)
	snakestone_door_chance = 0
	vault_target = 0
	vault_chance = 0

	vaults = [maze]
	frl_x = end[0] + 2 if end[0] > map_width//2 else end[0] - 3
	room_dir = 1 if end[0] > map_width//2 else -1
	first_room_location = [frl_x,end[1],room_dir]

	return generate_dungeon_map(floor_number,map_width,map_height,engine,items,room_target,rooms_chain,room_min_size,room_max_size,snakestone_door_chance,player,entities,dungeon,vault_target,vault_chance,vaults,first_room_location)


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
		1:(4,5), 2:(5,6), 3:(6,7), 4:(6,7), 5:(5,6), 7:(12,13), 8:(6,7), 9:(8,9)
	}[floor_number]
	room_target = random.choice(range(room_range[0],room_range[1]+1))

	rooms_chain = floor_number == 1

	small, msmall, mlarge, large, varied = ((6,8),(8,9),(9,10),(10,13),(6,13))
	room_min_size, room_max_size = {
		1:msmall, 2:msmall, 3:varied, 4:varied, 5:large, 7:small, 8:large, 9:varied
	}[floor_number]

	snakestone_door_chance = {
		1:1, 2:1, 3:0, 4:0, 5:0, 7:0.15, 8:0.15, 9:0.15, 10:0
	}[floor_number]

	player = engine.player
	entities = set(player.inventory.items)
	entities.update([player])
	dungeon = GameMap(engine, map_width, map_height, floor_number, entities=entities, items=items, vowel=entity_factories.vowel_segment, decoy=entity_factories.decoy)

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

	return generate_dungeon_map(floor_number,map_width,map_height,engine,items,room_target,rooms_chain,room_min_size,room_max_size,snakestone_door_chance,player,entities,dungeon,vault_target,vault_chance,vaults)


def generate_dungeon_map(floor_number,map_width,map_height,engine,items,room_target,rooms_chain,room_min_size,room_max_size,snakestone_door_chance,player,entities,dungeon,vault_target,vault_chance,vaults,first_room_location=None):
	vault_count = 0
	attempts = 0
	center_of_last_room = (0,0)
	rooms: List[RectangularRoom] = []
	max_attempts = 5000

	while len(rooms) < room_target and attempts < max_attempts:
		attempts += 1
		# if this is the first room, start at a random point at least 2 away from the borders of the map
		if len(rooms) == 0 and not first_room_location:
			x = random.choice(range(map_width)[2:-2])
			y = random.choice(range(map_height)[2:-2])
			x_dir = y_dir = 0
			door2 = None
		elif len(rooms) == 0:
			x = first_room_location[0]
			y = first_room_location[1]
			x_dir = first_room_location[2]
			y_dir = 0
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

		if floor_number == 10:
			door2 = None

		# generate a room with the chosen parameters
		room = RectangularRoom(x, y, x_dir, y_dir, map_width, map_height, rooms+vaults, room_max_size, room_min_size, door2)
		if not room.valid:
			continue

		# if this is the first room, place the player here
		if len(rooms) == 0 and floor_number != 10:
			place_player(dungeon,room.center,player)
			dungeon.tiles[room.inner] = tile_types.floor
			dungeon.upstairs_location = room.center

			xmods = random.choice([[-1,0,1],[-1,1]])
			ymods = [-1,0,1] if 0 not in xmods else [-1,1]
			vowel_spawn = (room.center[0] + random.choice(xmods), room.center[1] + random.choice(ymods))
			entity_factories.vowel_segment.spawn(dungeon,*vowel_spawn)

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
	if attempts == max_attempts and floor_number != 10:
		return generate_dungeon_map(floor_number,map_width,map_height,engine,items,room_target,rooms_chain,room_min_size,room_max_size,snakestone_door_chance,player,entities,dungeon,vault_target,vault_chance,vaults,first_room_location)
	elif attempts == max_attempts:
		place_player(dungeon,rooms[-1].center,player)


	if floor_number != 10:
		dungeon.tiles[center_of_last_room] = tile_types.down_stairs
		dungeon.downstairs_location = center_of_last_room
	else:
		dungeon.upstairs_location = center_of_last_room

	place_entities(dungeon,map_width,map_height,vaults)
	return dungeon

def place_player(dungeon,xy,player):
	player.place(*xy,dungeon)
	for item in player.inventory.items:
		item.blocks_movement = False
		item.place(*xy,dungeon)

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
	place_player(dungeon,room.center,player)
	dungeon.upstairs_location = room.center

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


class SpawnChunk():
	def __init__(self,chunk_coords,dungeon,map_width,map_height,vaults):
		tiles = []
		for x in range(6):
			map_x = (chunk_coords[0]) + x
			if map_x > map_width-1:
				continue
			for y in range(6):
				map_y = (chunk_coords[1]) + y
				if map_y > map_height-1:
					continue
				tiles.append((map_x,map_y))
		self.tiles = tiles
		self.dungeon = dungeon
		self.enemy_set = entity_factories.enemy_sets[dungeon.floor_number-1][:]
		self.vault_enemy = random.choice(entity_factories.enemy_sets[dungeon.floor_number][:])
		self.all_vaults = vaults

	@property
	def has_vault(self):
		return any(self.dungeon.tiles[i] == tile_types.vault_floor and not self.is_foyer_tile(i) for i in self.tiles)

	@property
	def vaults(self):
		return [vault for vault in self.all_vaults if any(vault.has_tile(tile) for tile in self.tiles)]

	@property
	def vault_tiles(self):
		return [i for i in self.tiles if self.dungeon.tiles[i] == tile_types.vault_floor and not self.is_foyer_tile(i)]

	def is_foyer_tile(self,tile):
		return any(tile in vault.foyer for vault in self.vaults)

	def place_monster_in_vault(self):
		potential_tiles = self.vault_tiles
		random.shuffle(potential_tiles)

		for tile in potential_tiles:
			# don't spawn on other monsters or in sight of the upstairs
			if (
				any(entity.xy == tile for entity in self.dungeon.entities) or
				max(abs(self.dungeon.upstairs_location[0]-tile[0]),abs(self.dungeon.upstairs_location[1]-tile[1])) < 10	
			):
				continue

			monster = random.choice(self.enemy_set + [self.vault_enemy])
			return monster.spawn(self.dungeon,*tile)

	def attempt_monster_placement(self):
		potential_tiles = self.tiles[:]
		random.shuffle(potential_tiles)

		for tile in potential_tiles:
			# use bad tile density as a spawn chance since crowded areas suck
			if (
				self.tile_name(tile) != 'floor' or 
				self.dungeon.tiles[tile] == tile_types.boss_vault_floor or 
				any(entity.xy == tile for entity in self.dungeon.entities) or 
				max(abs(self.dungeon.upstairs_location[0]-tile[0]),abs(self.dungeon.upstairs_location[1]-tile[1])) < 10 or
				self.is_foyer_tile(tile)
			):
				break

			eset = self.enemy_set
			if self.dungeon.tiles[tile] == tile_types.vault_floor:
				eset += [self.vault_enemy]

			monster = random.choice(eset)
			return monster.spawn(self.dungeon,*tile)

	def tile_name(self,tile):
		return tile_types.NAMES[self.dungeon.tiles[tile][5]]

	def attempt_item_placement(self):
		potential_tiles = [i for i in self.tiles if self.tile_name(i) == 'floor' and self.dungeon.tiles[i] != tile_types.boss_vault_floor]
		random.shuffle(potential_tiles)

		for tile in potential_tiles:
			if (
				self.dungeon.tiles[tile] == tile_types.down_stairs or
				self.dungeon.engine.player.xy == tile or
				any(entity.xy == tile and isinstance(entity,Item) for entity in self.dungeon.entities) or
				self.is_foyer_tile(tile)
			):
				break

			if random.random() < 0.85 and self.dungeon.tiles[tile] != tile_types.vault_floor:
				break

			item = entity_factories.vowel_segment if self.dungeon.tiles[tile] != tile_types.vault_floor else random.choice(self.dungeon.item_factories)
			return item.spawn(self.dungeon,*tile)


	def place_item_in_vault(self):
		potential_tiles = self.vault_tiles
		random.shuffle(potential_tiles)

		for tile in potential_tiles:
			if (
				self.dungeon.tiles[tile] == tile_types.down_stairs or
				self.dungeon.engine.player.xy == tile or
				any(entity.xy == tile and isinstance(entity,Item) for entity in self.dungeon.entities)
			):
				continue
			item = random.choice(self.dungeon.item_factories)
			return item.spawn(self.dungeon,*tile)
		return


def place_entities(dungeon,map_width,map_height,vaults=[]):
	chunks = []
	for x in range(map_width):
		for y in range(map_height):
			if x % 6 == 0 and y % 6 == 0:
				chunks.append(SpawnChunk((x,y),dungeon,map_width,map_height,vaults))

	for chunk in chunks:
		if chunk.has_vault:
			chunk.place_monster_in_vault()
		else:
			chunk.attempt_monster_placement()
		chunk.attempt_item_placement()
