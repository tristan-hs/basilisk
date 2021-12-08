"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import math
import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod

from basilisk.engine import Engine
from basilisk import color, entity_factories, exceptions, input_handlers
from basilisk.game_map import GameWorld

import utils


# Load the background image and remove the alpha channel.
background_image = tcod.image.load(utils.get_resource("menu_background.png"))[:, :, :3]

def new_game(meta) -> Engine:
    """Return a brand new game session as an Engine instance."""

    # If there's an existing save, log it as a game over
    try:
        engine = load_game(utils.get_resource("savegame.sav"))
    except FileNotFoundError:
        engine = None

    if engine:
        engine.history.append(("lose",True,engine.turn_count))
        engine.log_run()

    map_width = 76
    map_height = 40

    room_max_size = 30
    room_min_size = 7
    max_rooms = 100

    max_monsters_per_room = 5
    max_items_per_room = 1

    player = copy.deepcopy(entity_factories.player)
    player.id = 0

    engine = Engine(player=player, meta=meta)
    engine.meta = meta

    ooze_factor = 0.9

    game_mode = 'default'
    # game_mode = 'consumable testing'
    # game_mode = 'boss testing'

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
        vault_chance=0.02,
        game_mode=game_mode
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

def load_settings(filename: str) -> Meta:
    with open(filename, "rb") as f:
        meta = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(meta, Meta)
    return meta

class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def __init__(self):
        try:
            self.engine = load_game(utils.get_resource("savegame.sav"))
        except FileNotFoundError:
            self.engine = None

        try:
            self.meta = load_settings(utils.get_resource("savemeta.sav"))
        except FileNotFoundError:
            self.meta = Meta()

        if self.engine:
            self.engine.meta = self.meta

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
            ["(c)ontinue", "(n)ew game", "(h)istory", "(o)ptions", "(q)uit"]
        ):
            if i == 0 and not self.engine:
                continue
            if i == 2 and not len(self.meta.old_runs):
                continue
            console.print(
                72,
                19 + (2*i),
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

            if len(words) + y + 10 > console.height:
                y -= len(words) + y + 10 - console.height
                if y < 3:
                    y = 3

            pname = '@' + pname
            console.print(x,y,pname,color.player)
            console.print(x+len(pname),y," the Basilisk",color.offwhite)

            console.print(x,y+2,f"Floor: D{self.engine.game_map.floor_number}",color.offwhite)
            console.print(x,y+3,f"Turn:  {self.engine.turn_count}",color.offwhite)

            lword = sorted(words,key=lambda x:len(x))[-1] if words else "n/a"
            console.print(x,y+5,f"History:",color.offwhite)

            seen = set()
            for w in [i for i in reversed(words) if not (i in seen or seen.add(i))]:
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
            if self.engine:
                return input_handlers.Confirm(parent=self,callback=self.start_new_game,prompt="Start a new game? Your existing save will be overwritten and marked as a loss.")
            else: return self.start_new_game()
        elif event.sym == tcod.event.K_h and len(self.meta.old_runs):
            return HistoryMenu(self)
        elif event.sym == tcod.event.K_o:
            return OptionsMenu(self, self.engine)

        return None

    def start_new_game(self):
        return input_handlers.MainGameEventHandler(new_game(self.meta))


class SubMenu(input_handlers.BaseEventHandler):
    def __init__(self, parent):
        self.parent = parent

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym == tcod.event.K_ESCAPE:
            return self.parent
        return None

    def on_render(self, console:tcod.Console) -> None:
        console.draw_semigraphics(background_image, 0, 0)
        console.print(7,47,"(ESC) to go back")

class HistoryMenu(SubMenu):
    # (type of record, record, turn count)
            # types of record:
                # pickup item
                # spit item
                # digest item
                # break segment
                # identify item

                # kill enemy
                # descend stairs
                # form word
                # win
                # lose
    def __init__(self, parent):
        super().__init__(parent)

        history = self.parent.meta.old_runs
        shistory = [event for run in history for event in run]
        last_run = history[-1]

        stats = {}

        # LAST RUN STATS
        last_run = history[-1]
        words = [i for i in last_run if i[0] == "form word"]

        stats['Last run'] = [
            ('name', words[-1][1] if len(words) else ""),
            ('won', last_run[-1][0] == "win"),
            ('level', len([i for i in last_run if i[0] == "descend stairs"])+1),
            ('turns', last_run[-1][2]),
            ('unique kills', len(set([i[1] for i in last_run if i[0] == "kill enemy"]))),
            ('items identified', len([i for i in last_run if i[0] == "identify item"])),
            ('longest word', max([i[1] for i in words], key=len) if len(words) > 0 else "n/a"),
            ('unique words', len(set([i[1] for i in words])))
        ]

        # ALL TIME STATS
        unique_words = set([event[1] for event in shistory if event[0] == "form word"])

        stats['All time'] = [
            ('turns', sum([i[-1][2] for i in history])),
            ('unique kills', len(set([event[1] for event in shistory if event[0] == "kill enemy"]))), 
            ('items identified', len(set([event[1] for event in shistory if event[0] == "identify item"]))),
            ('longest word', max(unique_words, key=len) if len(unique_words) > 0 else ""),
            ('unique words', len(unique_words))
        ]

        # RECORDS
        floors = set([event[1] for event in shistory if event[0] == "descend stairs"])
        highest_floor = max(floors) if len(floors) > 0 else 1
        wins = [i for i in history if i[-1][0] == "win"]

        stats['Records'] = [
            ('lowest floor', max(floors) if len(floors) > 0 else 1),
            ('wins', len(wins)),
            ('win %', math.floor((len([i for i in shistory if i[0] == "win"])/len([i for i in shistory if i[0] in ["win","lose"]]))*100)/100),
            ('fastest win', min([i[-1][2] for i in wins]) if wins else "n/a")
        ]

        # WINNING WORDS
        last_words = []
        for w in wins:
            last_words.append([i[1] for i in w if i[0] == "form word"][-1])

        stats['Winning words'] = last_words

        self.stats = stats


    def on_render(self, console:tcod.Console) -> None:
        super().on_render(console)
        c2 = color.grey
        c3 = color.offwhite

        console.print(7,7,"HISTORY")

        console.print(8,10,"Last run")
        s = self.stats['Last run']
        console.print(9,12,f"@{s[0][1]}",color.player)
        console.print(10+len(s[0][1]),12," the Basilisk",c2)
        if s[1][1]:
            console.print(9,13,"CONSTRICTED THE ONE BELOW",color.purple)
        else:
            console.print(9,13,f"defeated on floor",c2)
            console.print(27,13,str(s[2][1]),c3)
        y = self.print_subsection(console,s[3:],15,c2,c3)
        
        console.print(8,y+2,"All time")
        y = self.print_subsection(console,self.stats['All time'],y+4,c2,c3)

        y = self.print_subsection(console,self.stats['Records'],y+1,c2,c3)
        
        console.print(8,y+2,f"Winning words")
        wins = self.stats['Records'][1][1] | 0
        if wins > 0:
            y += 4
            for w in self.stats['Winning words']:
                console.print(9,y,f"@{w}",color.player)
                y += 1
                if y > 47:
                    break
        else:
            console.print(9,y+4,"n/a",c2)

    def print_subsection(self,console,s,y,c2,c3):
        indent = max([len(i[0]) for i in s])+11
        for k,v in enumerate(s):
            console.print(9,y,f"{v[0]}",c2)
            i = str(v[1])
            c = c3 if i in ['0','n/a','0.0'] else c3
            if v[0] == 'unique kills':
                i += '/12'
                if v[0] == 12:
                    c = color.purple
            if v[0] == 'items identified':
                i += '/21'
                if v[0] == 21:
                    c = color.purple
            console.print(indent,y,i,c)
            y += 1
        return y

    
class OptionsMenu(SubMenu):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine

    def on_render(self, console:tcod.Console) -> None:
        super().on_render(console)
        console.print(7,7,"OPTIONS")
        console.print(8,10,"(f)ullscreen")
        ccstatus = "ON" if self.engine.meta.do_combat_confirm else "OFF"
        console.print(8,11,"(c)onfirm combat start - "+ccstatus)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym == tcod.event.K_f:
            raise exceptions.ToggleFullscreen()
        if event.sym == tcod.event.K_c:
            self.engine.meta.do_combat_confirm = not self.engine.meta.do_combat_confirm
        return super().ev_keydown(event)


class Meta():
    def __init__(self):
        self._fullscreen = True
        self.do_combat_confirm = True
        self.old_runs = []

    @property
    def fullscreen(self):
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, new_val):
        self._fullscreen = new_val
        self.save()

    def log_run(self, history):
        self.old_runs.append(history)
        self.save()

    def save(self):
        save_data = lzma.compress(pickle.dumps(self))
        with open(utils.get_resource("savemeta.sav"), "wb") as f:
            f.write(save_data)
