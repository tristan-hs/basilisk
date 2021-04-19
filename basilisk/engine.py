from __future__ import annotations

import lzma
import pickle

from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

from basilisk import exceptions, render_functions
from basilisk.message_log import MessageLog
from basilisk.components.status_effect import PetrifEyes

if TYPE_CHECKING:
    from basilisk.entity import Actor
    from basilisk.game_map import GameMap, GameWorld

import utils


class Engine:
    game_map: GameMap
    game_world: GameWorld
 
    def __init__(self, player: Actor):
        self.message_log = MessageLog(self)
        self.mouse_location = (0, 0)
        self.player = player
        self.word_mode = False
        self.turn_count = 0
        self.show_instructions = False
        self.boss_killed = False

    def check_word_mode(self):
        if len(self.player.inventory.items) < 1:
            self.word_mode = False
            return
        p_word = ''.join([i.char for i in self.player.inventory.items])
        self.word_mode = p_word in open(utils.get_resource("words.txt")).read().splitlines()

    def handle_enemy_turns(self) -> None:
        self.player.on_turn()
        if not any(isinstance(s,PetrifEyes) for s in self.player.statuses):
            for entity in set(self.game_map.actors) - {self.player}:
                if entity.ai:
                    try:
                        entity.ai.perform()
                    except exceptions.Impossible:
                        pass  # Ignore impossible action exceptions from AI.
        self.turn_count += 1

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=41, width=40, height=9)

        # maybe put drawer contents here instead?

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(76,0),
            word_mode = self.word_mode
        )

        render_functions.render_names_at_mouse_location(
            console=console, x=0, y=41, engine=self
        )

        if self.show_instructions:
            render_functions.render_instructions(
                console=console,
                location=(63,41)
            )
        else:
            render_functions.render_status(console=console,location=(63,42),statuses=self.player.statuses)

        render_functions.render_player_drawer(
            console=console,
            location=(77,9),
            player=self.player,
            turn=self.turn_count,
            word_mode=self.word_mode
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)