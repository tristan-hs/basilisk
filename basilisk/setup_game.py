"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod

from basilisk import input_handlers
from basilisk.engine import Engine
from basilisk import color, entity_factories
from basilisk.game_map import GameWorld

import utils


# Load the background image and remove the alpha channel.
background_image = tcod.image.load(utils.get_resource("menu_background.png"))[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 76
    map_height = 40

    room_max_size = 30
    room_min_size = 7
    max_rooms = 100

    max_monsters_per_room = 5
    max_items_per_room = 1

    player = copy.deepcopy(entity_factories.player)
    player.id = 0

    engine = Engine(player=player)

    ooze_factor = 0.9

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        ooze_factor=ooze_factor,
        vault_chance=0.02
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Salutations, ?. The dungeon awaits!", color.purple, "Basilisk", color.snake_green
    )
    return engine

def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine

class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def __init__(self):
        try:
            self.engine = load_game(utils.get_resource("savegame.sav"))
        except FileNotFoundError:
            self.engine = None
        except Exception as exc:
            traceback.print_exc()  # Print to stderr.
            return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")

    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width - 16,
            console.height - 3,
            "by -taq",
            fg=color.purple,
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["(c)ontinue", "(n)ew game", "(q)uit"]
        ):
            if i == 0 and not self.engine:
                continue
            console.print(
                72,
                21 + (2*i),
                text.ljust(menu_width),
                fg=color.white,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

        if self.engine:
            history = self.engine.history
            words = [i[1] for i in history if i[0] == 'form word']
            uses = [i for i in history if i[0] in ['spit item','digest item']]
            kills = [i for i in history if i[0] == 'kill enemy']
            pname = words[-1] if words else ''

            x = 22
            y = 21

            if len(words) + y + 3 > console.height:
                y -= len(words) + y + 3 - console.height
                if y < 3:
                    y = 3

            pname = '@' + pname
            console.print(x,y,pname,color.player)
            console.print(x+len(pname),y," the Basilisk",color.offwhite)

            console.print(x,y+2,f"Floor: D{self.engine.game_map.floor_number}",color.offwhite)
            console.print(x,y+3,f"Turn:  {self.engine.turn_count}",color.offwhite)

            lword = sorted(words,key=lambda x:len(x))[-1] if words else "n/a"
            console.print(x,y+5,f"History:",color.offwhite)

            for w in reversed(words):
                console.print(x+3,y+7,f"@{w}",tuple(c//2 for c in color.player))
                y += 1
                if y + 10 > console.height:
                    break

            if not len(words):
                console.print(x+3,y+7,"n/a",color.grey)


    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            if self.engine:
                return input_handlers.MainGameEventHandler(self.engine)
            else:
                return input_handlers.PopupMessage(self, "No saved game to load.")
        elif event.sym == tcod.event.K_n:
            return input_handlers.MainGameEventHandler(new_game())

        return None