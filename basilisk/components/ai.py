from __future__ import annotations

import random
from typing import List, Tuple, TYPE_CHECKING
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from basilisk.exceptions import Impossible

from basilisk.actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction
from basilisk import color

if TYPE_CHECKING:
    from basilisk.entity import Actor
    from basilisk.action import Action

class BaseAI(Action):

    _intent = None

    @property
    def intent(self) -> Optional[List[Action]]:
        if self._intent:
            return self._intent
        self.decide()
        return self._intent

    @property
    def fov(self):
        return tcod.map.compute_fov(
            self.engine.game_map.tiles["transparent"],
            (self.entity.x, self.entity.y),
            radius=8,
        )

    def clear_intent(self):
        self._intent = None

    def decide(self) -> Optional[Action]:
        raise NotImplementedError()

    def perform(self) -> None:
        for i in self.intent:
            try:
                i.perform()
            except Impossible:
                break
        self._intent = None
        self.entity.on_turn()

    def get_path_to(self, dest_x: int, dest_y: int, path_cost:int = 10, walkable=True) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.

        gm = self.entity.gamemap
        tiles = gm.tiles["walkable"] if walkable else np.full((gm.width,gm.height),fill_value=1,order="F")
        cost = np.array(tiles, dtype=np.int8)

        for entity in gm.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y] and (entity.x != dest_x or entity.y != dest_y):
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += path_cost

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=3, diagonal=4)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


    def get_path_past(self, dest_x,dest_y,path_cost=0,walkable=True):
        path = self.get_path_to(dest_x,dest_y,path_cost,walkable)
        if len(path) < 1:
            return path

        new_path = []
        i = 0

        while True:
            key = i % len(path)
            tile = path[key]
            if key == 0:
                diff = (tile[0]-self.entity.x,tile[1]-self.entity.y)
            else:
                prev = path[key-1]
                diff = (tile[0]-prev[0],tile[1]-prev[1])

            new_o = new_path[i-1] if i > 0 else (dest_x,dest_y)
            new_tile = (new_o[0]+diff[0],new_o[1]+diff[1])

            if not self.engine.game_map.tile_is_walkable(*new_tile):
                break
            new_path.append(new_tile)
            i += 1

        return new_path





class HostileEnemy(BaseAI):

    def __init__(self, entity: Actor,):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = None
        self.move_speed = entity.move_speed
        self.last_target = None

    @property
    def description(self):
        return "hostile" if self.last_target else "asleep"

    def distance_to(self, tx, ty):
        dx = tx-self.entity.x
        dy = ty-self.entity.y
        return max(abs(dx),abs(dy))

    def pick_target(self):
        fov = tcod.map.compute_fov(
            self.engine.game_map.tiles["transparent"],
            (self.entity.x, self.entity.y),
            radius=8,
        )

        # pick the first thing in fov that you can path to:
            # a decoy
            # the nearest of the player or its parts
                # if you are seeing the player after not being in attack mode, send the notice message
            # the last place you saw a player or its parts

        # set last_target to whatever you pick

        target = None
        
        for entity in self.engine.game_map.entities:
            if entity.name == "Decoy" and fov[entity.x,entity.y]:
                d = len(self.get_path_to(*entity.xy))
                if d:
                    self.last_target = target.xy
                    return (target,d,target.xy)

        d_to_t = 0
        for entity in [self.engine.player] + self.engine.player.inventory.items:
            if fov[entity.x,entity.y]:
                d = len(self.get_path_to(*entity.xy))
                if d and (not d_to_t or d_to_t > d):
                    d_to_t = d
                    target = entity
        if target:
            self.last_target = target.xy
            return (target,d_to_t,target.xy)

        if self.last_target:
            d = len(self.get_path_to(*self.last_target))
            if d:
                return (None, d, self.last_target)

        return (None, None, None)


    def decide(self) -> Optional[Action]:
        self._intent = []

        target, distance, xy = self.pick_target()
        x, y = self.entity.xy

        if not xy:
            self._intent.append(WaitAction(self.entity))
            return

        if distance == 1:
            self._intent.append(BumpAction(self.entity, xy[0]-x, xy[1]-y))
            return
        
        self.path = self.get_path_to(xy[0], xy[1])

        if self.path:
            next_move = self.path[0:self.move_speed]
            fx, fy = x, y
            for m in next_move:
                # only intend to move into non-walkables as an attack on a known target
                if not self.engine.game_map.tile_is_walkable(*m) and (not target or m != target.xy):
                    break
                dx = m[0]-fx
                dy = m[1]-fy
                self._intent.append(BumpAction(self.entity, dx, dy))
                fx += dx
                fy += dy
            if len(self._intent) > 0:
                return

        self._intent.append(WaitAction(self.entity))


class Statue(BaseAI):
    description = "docile"

    def decide(self) -> Optional[Action]:
        self._intent = [WaitAction(self.entity)]


class Constricted(BaseAI):
    description = "constricted"

    def __init__(self, entity: Actor, previous_ai: Optional[BaseAI], previous_color: Optional[Tuple[int,int,int]]):
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.previous_color = previous_color

    def decide(self) -> Optional[Action]:
        self._intent = [WaitAction(self.entity)]

    def perform(self) -> None:
        if self.entity.is_next_to_player():
            new_char = int(self.entity.base_char)-self.entity.how_next_to_player()
            if not self.entity.is_boss:
                new_char -= self.engine.player.TAIL
            if new_char < 0:
                self.entity.die()
                return
            if self.entity.is_boss and self.entity.how_next_to_player() > 7:
                self.engine.boss_killed = True
                return
            self.entity.char = str(new_char)
            super().perform()
        else:
            self.engine.message_log.add_message(f"The {self.entity.name} is no longer constricted.", color.grey)
            self.entity.char = self.entity.base_char
            self.entity.ai = self.previous_ai
            self.entity.ai._intent = None

class ConfusedEnemy(BaseAI):
    description = "confused"
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(
        self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int,
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining
        self.move_speed = entity.move_speed

    def decide(self) -> Optional[Action]:
        self._intent = []
        if self.turns_remaining <= 0:
            self._intent.append(WaitAction(self.entity))
            return

        for i in range(self.move_speed):
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )
            self._intent.append(BumpAction(self.entity, direction_x, direction_y))

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused.", color.grey
            )
            self.entity.ai = self.previous_ai
            return
        
        self.turns_remaining -= 1
        super().perform()
