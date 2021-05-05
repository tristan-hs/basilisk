from __future__ import annotations

import lzma
import pickle
import glob
import os

from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

from basilisk import exceptions, render_functions
from basilisk.message_log import MessageLog
from basilisk.components.status_effect import PetrifEyes, Petrified, PhasedOut
import basilisk.color as color
from basilisk.components.ai import Constricted

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

    # field of view
    @property
    def fov_radius(self):
        return 8 + self.player.TONG

    # field of smell: detect presence of enemies
    @property
    def fos_radius(self):
        return 0 + self.player.TONG * 2

    # field of identity: detect enemy identity
    @property
    def foi_radius(self):
        return 0 + self.player.TONG

    def turn_back_time(self, turns, turner):
        turn = self.turn_count - turns
        with open(f"snapshot_{turn}.sav", "rb") as f:
            engine = pickle.loads(lzma.decompress(f.read()))
        assert isinstance(engine, Engine)
        self.game_map = engine.game_map
        self.game_map.engine = self
        self.player = engine.player

        for i in self.game_map.entities:
            if i.id == turner.id:
                if i in self.player.inventory.items:
                    i.edible.consume()
                else:
                    i.consume()
                return

    def save_turn_snapshot(self):
        self.save_as(f"snapshot_{self.turn_count}.sav")
        snapshots = glob.glob("snapshot_*.sav")
        for s in snapshots:
            turn = s[9:s.index('.')]
            if int(turn) < self.turn_count-10:
                os.remove(s)

    def check_word_mode(self):
        if len(self.player.inventory.items) < 1:
            self.word_mode = False
            return
        p_word = ''.join([i.char for i in self.player.inventory.items])
        self.word_mode = p_word in open(utils.get_resource("words.txt")).read().splitlines()

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                if (
                    any(isinstance(s,PetrifEyes) for s in self.player.statuses) and 
                    self.game_map.visible[entity.x,entity.y] and 
                    not isinstance(entity.ai, Constricted)
                ):
                    entity.ai.clear_intent()
                    continue
                if (
                    (
                        any(isinstance(s,Petrified) for s in entity.statuses) or
                        any(isinstance(s,PhasedOut) for s in entity.statuses)
                    ) and
                    not isinstance(entity.ai, Constricted)
                ):
                    entity.ai.clear_intent()
                    entity.on_turn()
                    continue
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

            if not self.player.is_alive:
                break

        self.player.on_turn()

        if not self.player.can_move():
            self.message_log.add_message(f"Oof! You're trapped!", color.red)
            self.player.die()
        
        self.turn_count += 1
        self.save_turn_snapshot()   

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=self.fov_radius,
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

        actor = self.game_map.get_actor_at_location(*self.mouse_location)
        self.game_map.print_enemy_fov(console, actor)
        self.game_map.print_intent(console, actor)

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