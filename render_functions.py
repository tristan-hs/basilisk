from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap

DIRECTIONS = [(0,-1),(0,1),(-1,-1),(-1,0),(-1,1),(1,-1),(1,0),(1,1)]
D_ARROWS = ['↑', '↓', '\\', '←', '/', '/','→','\\']
D_KEYS = ['J','K','Y','H','B','U','L','N']

def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()

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
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.draw_frame(
        x=x,
        y=y,
        width=4,
        height=3,
        clear=True,
        fg=color.offwhite,
        bg=(0,0,0)
    )
    console.print(x=x+1, y=y+1, string=f"D{dungeon_level}")

def render_instructions(console: Console, location: Tuple[int,int]) -> None:
    x, y = location
    l1 = f"{D_KEYS[2]} {D_KEYS[0]} {D_KEYS[5]} (i)nventory"
    l2 = f" {D_ARROWS[2]}{D_ARROWS[0]}{D_ARROWS[5]}  (s)pit"
    l3 = f"{D_KEYS[3]}{D_ARROWS[3]}.{D_ARROWS[6]}{D_KEYS[6]} (d)igest"
    l4 = f" {D_ARROWS[4]}{D_ARROWS[1]}{D_ARROWS[7]}  (>)descend"
    l5 = f"{D_KEYS[4]} {D_KEYS[1]} {D_KEYS[7]} (/)look"
    l6 = f"      (.)wait"
    l7 = f"    re(v)iew"

    for i,l in enumerate([l1,l2,l3,l4,l5,l6,l7]):
        console.print(x=x, y=y+i, string=l, fg=(150,150,150))

def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)

def render_word_mode(console: Console, location: Tuple[int,int], active: bool) -> None:
    x, y = location

    c = color.white if active else color.grey

    console.draw_frame(
        x=x,
        y=y,
        width=4,
        height=6,
        clear=True,
        fg=c,
        bg=(0,0,0)
    )

    console.print(x=x+1,y=y+1,string="WM\nOO\nRD\nDE", fg=c)

def render_player_drawer(console: Console, location: Tuple[int,int], player, turn) -> None:
    sx, sy = x, y = location
    items = player.inventory.items

    adj = turn % 4

    sy += adj
    x += adj

    r = 26

    for i in range(r):
        if r-i == len(items)+1:
            console.print(x=x,y=y,string=player.char,fg=player.color)
        if r-i < len(items)+1:
            item = items[len(items)-r+i]
            console.print(x=x,y=y,string=item.char,fg=item.color)

        if (x == sx and y % 4 == sy % 4) or x < sx:
            x += 1
        else:
            x -= 1
        y += 1
