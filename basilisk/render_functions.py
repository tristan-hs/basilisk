from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import random

from basilisk import color
from basilisk.message_log import MessageLog
from basilisk.render_order import RenderOrder
from basilisk.tile_types import NAMES, FLAVORS

if TYPE_CHECKING:
    from tcod import Console
    from basilisk.engine import Engine
    from basilisk.game_map import GameMap

DIRECTIONS = [(0,-1),(0,1),(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)]
D_ARROWS = ['↑', '↓', '\\', '←', '/', '/','→','\\']
D_KEYS = ['K','J','Y','H','B','U','L','N']
ALPHA_CHARS = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=45, width=20, height=1, ch=1, bg=color.dark_red)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=color.snake_green
        )

    console.print(
        x=1, y=45, string=f"HP: {current_value}/{maximum_value}", fg=color.white
    )

def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int], word_mode: bool, turn_count: int, do_turn_count: bool
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location
    x -= 1
    c = color.offwhite if word_mode else color.grey
    dungeon_level = dungeon_level if len(str(dungeon_level)) > 1 else f"0{dungeon_level}"

    if do_turn_count:
        turn_count = str(turn_count)
        for i in [9,99,999]:
            if int(turn_count) <= i:
                turn_count = '0' + turn_count
        if int(turn_count) > 9999:
            turn_count = turn_count[0]+turn_count[1]+'.'+turn_count[2]+'k'
        if int(turn_count) > 99999:
            turn_count = ' bruh'

        console.draw_frame(
            x=x-2,
            y=+2,
            width=8,
            height=3,
            clear=True,
            fg=color.grey,
            bg=(0,0,0)
        )
        console.print(x=x-1,y=y+3,string=f"T{turn_count}", fg=color.grey)

    console.draw_frame(
        x=x,
        y=y,
        width=5,
        height=3,
        clear=True,
        fg=c,
        bg=(0,0,0)
    )
    console.print(x=x-1,y=y,string='╚╦',fg=color.snake_green if word_mode else color.grey)
    console.print(x=x+1, y=y+1, string=f"D{dungeon_level}", fg=c)

def render_instructions(console: Console, location: Tuple[int,int]) -> None:
    x, y = location
    l0 = f"{D_KEYS[2]} {D_KEYS[0]} {D_KEYS[5]} (?)info"
    l1 = f" {D_ARROWS[2]}{D_ARROWS[0]}{D_ARROWS[5]}  (.)wait"
    l2 = f"{D_KEYS[3]}{D_ARROWS[3]}.{D_ARROWS[6]}{D_KEYS[6]} (>)descend"
    l3 = f" {D_ARROWS[4]}{D_ARROWS[1]}{D_ARROWS[7]}  (i)nventory"
    l4 = f"{D_KEYS[4]} {D_KEYS[1]} {D_KEYS[7]} (s)pit"
    l5 = "      (d)igest"
    l7 = "     e(x)amine"
    l6 = "    re(v)iew"
    l8 = f"   per(c)eive"

    for i,l in enumerate([l0,l1,l2,l3,l4,l5,l6,l7,l8]):
        console.print(x=x, y=y+i, string=l, fg=color.dark_grey)

def render_status(console: Console, location: Tuple[int,int], statuses: List, engine: Engine) -> None:
    render_stats(console, *location, engine)

    g_statuses = ["SALIVA","PETRIFY","PHASE","SHIELD"] + ["CHOKE","DAZE"]

    for i,s in enumerate(g_statuses):
        status = [status for status in statuses if status.label and status.label.upper() == s]
        fg = status[0].color if status else color.dark_grey
        y = 41 + i if i < 4 else 42 + i
        x = 71-len(s)-2 if i < 4 else 72
        d = str(status[0].duration) if status else '0'
        d = d if len(d) < 2 else '!'
        string = s+'.'+d if i < 4 else s + '.'*(6-len(s)) + d
        console.print(x=x,y=y,string=string,fg=fg)


def render_stats(console: Console, x:int, y:int, engine: Engine):
    player = engine.player

    for i,stat in enumerate(["BILE","MIND","TONG","TAIL"]):
        base_amt = player.stats[stat] - player.get_status_boost(stat)
        temp_amt = player.stats[stat]

        for j,c in enumerate(stat):
            if j < base_amt:
                fg = color.stats[stat]
            elif j < temp_amt:
                fg = color.boosted_stats[stat]
            else:
                fg = color.dark_grey
            console.print(x=x+j,y=y+i,string=c,fg=fg)

        k = 4
        while  k < 6:
            c = '+'
            if k < base_amt:
                fg = color.stats[stat]
            elif k < temp_amt:
                fg = color.boosted_stats[stat]
            else:
                c = '.'
                fg = color.dark_grey
            if stat == 'TONG' and k < temp_amt:
                if k == 4:
                    c = 'U'
                if k == 5:
                    c = 'E'
            console.print(x=x+k,y=y+i,string=c,fg=fg)
            k+=1
    
        console.print(x=x+6,y=y+i,string='0',fg=color.dark_grey)

        if player.get_status_boost(stat) > 0:
            string = str(player.get_stat_boost_duration(stat))
            if len(string) > 1:
                string = '!'
            console.print(x=x+6,y=y+i,string=string,fg=color.boosted_stats[stat])


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    if not engine.game_map.in_bounds(mouse_x, mouse_y):
        return

    entities = engine.mouse_things

    chars = ALPHA_CHARS[:]
    for e,entity in enumerate(entities):
        if e == len(entities)-1 and (engine.game_map.visible[mouse_x,mouse_y] or engine.game_map.explored[mouse_x,mouse_y] or engine.game_map.mapped[mouse_x,mouse_y]):
            tile = engine.game_map.tiles['light'][mouse_x,mouse_y]
            name = NAMES[entity[5]]
            fg = color.grey
            console.print(x+3,y+e,chr(tile[0]),tuple(tile[1]),tuple(tile[2]))
        else:
            engine.game_map.print_tile(entity,(x+3,y+e),console)
            name = entity.label if len(entity.label) > 1 else '???'
            fg = entity.color
        
        name = name if len(name) < 13 else name[:10]+'..'
        console.print(x,y+e,chars.pop(0)+')',fg=fg)
        console.print(x+5,y+e,name,fg=fg)
        if e > 6:
            console.print(x+1,y+e+1,'...',fg=color.offwhite)
            break
    

class ColorScheme:
    def __init__(self, player, base_colors=[color.dark_grey,color.grey], scheme_length=28):
        colors = [color.bile] * player.BILE + [color.mind] * player.MIND + [color.tongue] * player.TONG + [color.tail] * player.TAIL 
        if len(colors) < 28:
            colors += [base_colors[0]] * (scheme_length - len(colors) - 1)
            colors += [base_colors[1]]
        # fixed shuffle per length of list
        random.Random(round(player.engine.turn_count/500)).shuffle(colors)
        
        # cycle through that shuffle turn by turn
        for i in range(player.engine.turn_count % scheme_length):
            c = colors.pop(0)
            colors.append(c)

        self.colors = colors
        self._index = -1

    @property
    def next_color(self):
        self._index += 1
        if self._index >= len(self.colors):
            self._index = 0

        return self.colors[self._index]



def render_player_drawer(console: Console, location: Tuple[int,int], player, turn, word_mode) -> int:
    sx, sy = x, y = location
    items = player.inventory.items
    cs = ColorScheme(player, [color.snake_green,color.offwhite]) if word_mode else ColorScheme(player)
    wcs = ColorScheme(player, [color.dark_grey,color.snake_green],30) if word_mode else ColorScheme(player,scheme_length=30)

    sy -= 4
    y -= 4

    adj = turn % 4
    sy += adj
    x += adj
    r = 30

    for i in range(r):
        if r-i == len(items)+1:
            f_start = y-1
            f_height = r-i+2
            console.print(x=x,y=y,string=player.char,fg=player.color)
        if r-i < len(items)+1:
            item = items[len(items)-r+i]
            console.print(x=x,y=y,string=item.char,fg=item.color)

        if (x == sx and y % 4 == sy % 4) or x < sx:
            x += 1
        else:
            x -= 1
        y += 1

    # word mode letters n junk
    for i,char in enumerate("WORD"):
        console.print(x=75+i,y=sy-adj+r-f_height,string=char,fg=cs.next_color)
    # word mode frame
    console.draw_frame(
        x=sx-2,
        y=f_start,
        width=5,
        height=f_height,
        clear=False,
        fg=color.offwhite if word_mode else color.dark_grey,
        bg=None
    )
    for i,char in enumerate("MODE"):
        console.print(x=75+i+1,y=sy-adj+r+1,string=char,fg=cs.next_color)

    # stats frame
    console.draw_frame(x=71,y=40,width=9,height=6,clear=False,fg=color.grey if word_mode else color.dark_grey,bg=(0,0,0))

    # wires top to bottom
    for i,c in enumerate('╣'+'║'*(f_start-3)+'╣'):
        console.print(79,2+i,c,fg=wcs.next_color)

    x,y = 75,sy-adj+r
    console.print(x=x,y=y,string='╠',fg=wcs.next_color)
    y+=1
    console.print(x=x,y=y,string="║",fg=wcs.next_color)
    y+=1
    for i,c in enumerate('╚═══╗'):
        console.print(x=x+i,y=y,string=c,fg=wcs.next_color)
    y += 1
    for i,c in enumerate('║║╣'):
        console.print(x=x+4,y=y+i,string=c,fg=wcs.next_color)


def print_fov_actors(console,player,xy):
    x,y = xy
    chars = ALPHA_CHARS[:]
    for actor in sorted(list(player.gamemap.actors),key=lambda a:a.id):
        if actor is player:
            continue
        if not (player.gamemap.visible[actor.x,actor.y] or player.gamemap.smellable(actor,True)):
            continue
        if player.gamemap.print_actor_tile(actor,(x+3,y),console):
            name = actor.name
            if len(name) > 12:
                name = name[:10]+'..'
            fg = actor.color
            console.print(x,y,f"{chars.pop(0)})",fg=fg)
            console.print(x+5,y,name,fg=fg)
            if actor.ai.description == "asleep":
                console.print(x+18,y,"z²",fg=color.grey)
            y += 1
            if y > 48:
                console.print(x+1,y,'...',fg=color.offwhite)
                break

    xs,ys = player.gamemap.downstairs_location
    if player.gamemap.visible[xs,ys]:
        tile = player.gamemap.tiles['light'][xs,ys]
        name = NAMES[player.gamemap.tiles[xs,ys][5]]
        fg = color.grey
        console.print(x+3,y,chr(tile[0]),tuple(tile[1]),tuple(tile[2]))

        if len(name) > 12:
            name = name[:10]+'..'
        console.print(x,y,f"{chars.pop(0)})",fg=fg)
        console.print(x+5,y,name,fg=fg)

    console.print(6,49,"(c)ontrols",color.dark_grey)

