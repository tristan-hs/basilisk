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
                pass
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
        self.has_seen_player = False

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

        target = self.engine.player if fov[self.engine.player.x,self.engine.player.y] else None
        d_to_t = self.distance_to(*target.xy) if target else 999

        if target == None and self.has_seen_player == False:
            return (None, None)

        if target != None and self.has_seen_player == False:
            self.has_seen_player = True
            self.engine.message_log.add_message(f"The ? notices you!", color.offwhite, self.entity.name, self.entity.color)

        for i in self.engine.player.inventory.items:
            d_to_i = self.distance_to(*i.xy)
            if d_to_i < d_to_t and fov[i.x,i.y]:
                d_to_t = d_to_i
                target = i

        for entity in self.engine.game_map.entities:
            if entity.name == "Decoy" and fov[entity.x,entity.y]:
                target = entity
                d_to_t = self.distance_to(*entity.xy)


        return (target, d_to_t)


    def decide(self) -> Optional[Action]:
        self._intent = []

        target, distance = self.pick_target()
        x, y = self.entity.xy

        if target == None:
            self._intent.append(WaitAction(self.entity))
            return

        if distance <= 1:
            self._intent.append(BumpAction(self.entity, target.x-x, target.y-y))
            return
        
        self.path = self.get_path_to(target.x, target.y)

        if self.path:
            next_move = self.path[0:self.move_speed]
            fx, fy = x, y
            for m in next_move:
                dx = m[0]-fx
                dy = m[1]-fy
                self._intent.append(BumpAction(self.entity, dx, dy))
                fx += dx
                fy += dy
            return

        self._intent.append(WaitAction(self.entity))


class Statue(BaseAI):
    def decide(self) -> Optional[Action]:
        self._intent = [WaitAction(self.entity)]


class Constricted(BaseAI):
    def __init__(self, entity: Actor, previous_ai: Optional[BaseAI], previous_color: Optional[Tuple[int,int,int]]):
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.previous_color = previous_color

    def decide(self) -> Optional[Action]:
        self._intent = [WaitAction(self.entity)]

    def perform(self) -> None:
        if self.entity.is_next_to_player():
            new_char = int(self.entity.base_char)-self.entity.how_next_to_player()-self.engine.player.TAIL
            if new_char < 0:
                self.entity.die()
                return
            self.entity.char = str(new_char)
            super().perform()
        else:
            self.engine.message_log.add_message(f"The {self.entity.name} is no longer constricted.", color.grey)
            self.entity.color = self.previous_color
            self.entity.char = self.entity.base_char
            self.entity.ai = self.previous_ai
            self.entity.ai._intent = None

class ConfusedEnemy(BaseAI):
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
