from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import random

from basilisk import color
from basilisk.message_log import MessageLog
from basilisk.render_order import RenderOrder

if TYPE_CHECKING:
    from tcod import Console
    from basilisk.engine import Engine
    from basilisk.game_map import GameMap

DIRECTIONS = [(0,-1),(0,1),(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)]
D_ARROWS = ['↑', '↓', '\\', '←', '/', '/','→','\\']
D_KEYS = ['J','K','Y','H','B','U','L','N']

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
    console: Console, dungeon_level: int, location: Tuple[int, int], word_mode: bool
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location
    c = color.offwhite if word_mode else color.grey

    console.draw_frame(
        x=x,
        y=y,
        width=4,
        height=3,
        clear=True,
        fg=c,
        bg=(0,0,0)
    )

    console.print(x=x-1,y=y,string='╚╦',fg=color.snake_green if word_mode else color.grey)

    console.print(x=x+1, y=y+1, string=f"D{dungeon_level}", fg=c)

def render_instructions(console: Console, location: Tuple[int,int]) -> None:
    x, y = location
    l0 = f"      (i)nventory"
    l1 = f"{D_KEYS[2]} {D_KEYS[0]} {D_KEYS[5]} (s)pit"
    l2 = f" {D_ARROWS[2]}{D_ARROWS[0]}{D_ARROWS[5]}  (d)igest"
    l3 = f"{D_KEYS[3]}{D_ARROWS[3]}.{D_ARROWS[6]}{D_KEYS[6]} (>)descend"
    l4 = f" {D_ARROWS[4]}{D_ARROWS[1]}{D_ARROWS[7]}  (/)look"
    l5 = f"{D_KEYS[4]} {D_KEYS[1]} {D_KEYS[7]} (.)wait"
    l6 = "    re(v)iew"
    l7 = ""
    l8 = f"   per(c)eive"

    for i,l in enumerate([l0,l1,l2,l3,l4,l5,l6,l7,l8]):
        console.print(x=x, y=y+i, string=l, fg=color.grey)

def render_status(console: Console, location: Tuple[int,int], statuses: List, engine: Engine) -> None:
    render_stats(console, *location, engine)

    g_statuses = ["SALIVA","PETRIFY","PHASE","SHIELD"] + ["CHOKE","DAZE"]

    for i,s in enumerate(g_statuses):
        status = [status for status in statuses if status.label and status.label.upper() == s]
        fg = status[0].color if status else color.dark_grey
        y = 41 + i if i < 4 else 42 + i
        x = 71-len(s)-2 if i < 4 else 72
        string = s+'.0' if i < 4 else s + '.'*(6-len(s)) + '0'
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
        console.print(x=x+6,y=y+i,string='0',fg=fg)

        if player.get_status_boost(stat) > 0:
            console.print(x=x+6,y=y+i,string=str(player.get_stat_boost_duration(stat)),fg=color.boosted_stats[stat])


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    if not engine.game_map.in_bounds(mouse_x, mouse_y):
        return

    entities = [
        e for e in engine.game_map.entities if 
            e.x == mouse_x and 
            e.y == mouse_y and 
            (
                engine.game_map.visible[mouse_x, mouse_y] or 
                (engine.game_map.explored[mouse_x, mouse_y] and e.render_order == RenderOrder.ITEM) or
                engine.game_map.smellable(e, True)
            )
        ]

    if len(entities) == 1:
        entity = entities[0]
    elif len(entities) > 1:
        actors = [e for e in entities if e.render_order == RenderOrder.ACTOR]
        if len(actors) == 1:
            entity = actors[0]
        else:
            for e,entity in enumerate(entities):
                console.print(x,y+e,entity.label,fg=entity.color)
                if e > 8:
                    break
            return
    else:
        return
    console.print(x=x,y=y,string=entity.label,fg=entity.color)
    console.print_box(x,y+2,20,6,entity.description,color.offwhite)

    console.print(x=x,y=y+y,string=f"id:{entity.id}",fg=color.offwhite)
    

class ColorScheme:
    def __init__(self, player, base_colors=[color.dark_grey,color.grey]):
        colors = [color.bile] * player.BILE + [color.mind] * player.MIND + [color.tongue] * player.TONG + [color.tail] * player.TAIL 
        if len(colors) < 28:
            colors += [base_colors[0]] * (28 - len(colors) - 1)
            colors += [base_colors[1]]
        # fixed shuffle per length of list
        random.Random(92).shuffle(colors)
        
        # cycle through that shuffle turn by turn
        for i in range(player.engine.turn_count % 28):
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
    cs = ColorScheme(player, [color.offwhite,color.grey]) if word_mode else ColorScheme(player)

    sy -= 4
    y -= 4

    adj = turn % 4
    sy += adj
    x += adj
    r = 30

    c = color.snake_green if word_mode else color.grey

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

    c2 = color.offwhite if word_mode else color.grey
    console.draw_frame(
        x=sx-2,
        y=f_start,
        width=5,
        height=f_height,
        clear=False,
        fg=c2,
        bg=(0,0,0)
    )

    x, y = 75, sy - adj + r - f_height

    for i,char in enumerate("WORD"):
        console.print(x=x+i,y=y,string=char,fg=cs.next_color)

    console.print(x=x+4,y=y,string="║",fg=c)
    y=y+f_height
    console.print(x=x,y=y,string='╠',fg=c)
    y+=1
    console.print(x=x,y=y,string="║",fg=c)

    for i,char in enumerate("MODE"):
        console.print(x=x+i+1,y=y,string=char,fg=cs.next_color)

    # frame up from word to d#
    console.print_box(79,2,1,f_start-1,'╣'+'║'*(f_start-3)+'╣',fg=c)
    # frame down from mode
    y+=1
    console.print(x=x,y=y,string='╚═══╗\n    ║',fg=c)
    console.draw_frame(x=71,y=y+3,width=9,height=6,clear=False,fg=c2,bg=(0,0,0))
    console.print(x=x+4,y=y+2,string='║\n╣',fg=c)
    #y+=3
    #console.print_box(0,y,80,1,'═'*20+'╦'+'═'*40+'╦'+'═'*13+'╩════',fg=c2)
    #y+=1
    #console.print_box(20,y,1,9,'║'*9,fg=c2)
    #console.print_box(61,y,1,9,'║'*9,fg=c2)








