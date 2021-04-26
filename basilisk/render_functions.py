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
    l6 = f"      (f)ind"
    l7 =   "    re(v)iew"
    l8 = f"      (c)haracter"

    for i,l in enumerate([l0,l1,l2,l3,l4,l5,l6,l7,l8]):
        console.print(x=x, y=y+i, string=l, fg=color.grey)

def render_status(console: Console, location: Tuple[int,int], statuses: List) -> None:
    x, y = location
    for s,status in enumerate(statuses):
        if not status.label:
            continue
        console.print(
            x=x,
            y=y+s,
            string=f"{status.label.upper()} {str(status.duration)}",
            fg=status.color
        )
    console.print(x,y+7,"      (c)ontrols",color.grey)


def render_stats_in_inspect_box(console: Console, x:int, y:int, engine: Engine):
    player = engine.player

    if engine.word_mode:
        colors = [
            color.tongue,
            color.snake_green, 
            color.green,
            color.goblin,
            color.tail,
            color.statue,
            color.player_dark,
            color.grey,
            (75,125,0),
            color.mind,
            color.bile
        ] + [color.bile] * player.BILE + [color.mind] * player.MIND + [color.tongue] * player.TONG + [color.tail] * player.TAIL 
        random.Random(engine.turn_count).shuffle(colors)
        for i,c in enumerate("WORD MODE"):
            console.print(x=x+i,y=y,string=c,fg=colors.pop())

    for i,stat in enumerate(["BILE","MIND","TONG","TAIL"]):
        for j,c in enumerate(stat):

            stat_color = color.stats[stat] if j >= player.stats[stat] or j < player.stats[stat] - player.get_status_boost(stat) else color.boosted_stats[stat]

            bg = color.black
            fg = stat_color if player.stats[stat] > j else color.grey

            console.print(x=x+j,y=y+2+i,string=c,fg=fg,bg=bg)

        k = 4
        while k < player.stats[stat] and k < 14:
            c = '+'
            if stat == 'TONG':
                if k == 4:
                    c = 'U'
                if k == 5:
                    c = 'E'
            console.print(x=x+k,y=y+2+i,string=c,fg=color.stats[stat])
            k+=1

        if player.get_status_boost(stat) > 0:
            console.print(x=x+k,y=y+2+i,string=f"({player.get_stat_boost_duration(stat)})",fg=color.boosted_stats[stat])


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

    if len(entities) < 1:
        render_stats_in_inspect_box(console, x, y, engine)
        return

    if len(entities) == 1:
        # print info panel
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
    console.print(x=x,y=y,string=entity.label,fg=entity.color)
    console.print_box(x,y+2,20,7,entity.description,color.offwhite)
    


def render_player_drawer(console: Console, location: Tuple[int,int], player, turn, word_mode) -> int:
    sx, sy = x, y = location
    items = player.inventory.items

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

    console.draw_frame(
        x=sx-2,
        y=f_start,
        width=5,
        height=f_height,
        clear=False,
        fg=c,
        bg=(0,0,0)
    )

    x, y = 75, sy - adj + r - f_height

    console.print(x=x,y=y,string="WORD║",fg=c)
    y=y+f_height
    console.print(x=x,y=y,string='╠',fg=c)
    y+=1
    console.print(x=x,y=y,string="║MODE",fg=c)
    # frame up from word to d#
    console.print_box(79,2,1,f_start-1,'╣'+'║'*(f_start-3)+'╣',fg=c)
    # frame down from mode
    y+=1
    console.print(x=x,y=y,string='╚═══╗\n    ║\n╔═══╝',fg=c)
    y+=3
    c2 = color.offwhite if word_mode else color.grey
    console.print_box(0,y,80,1,'═'*20+'╦'+'═'*40+'╦'+'═'*13+'╩════',fg=c2)
    y+=1
    console.print_box(20,y,1,9,'║'*9,fg=c2)
    console.print_box(61,y,1,9,'║'*9,fg=c2)








