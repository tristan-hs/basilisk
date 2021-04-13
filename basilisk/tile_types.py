from typing import Tuple

import numpy as np  # type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)
# MAPPED representes unexplored, mapped tiles
MAPPED = np.array((ord("░"), (0,0,0), (82,62,30)), dtype=graphic_dt)


floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (5,5,5)),
    light=(ord(" "), (255, 255, 255), (10,10,10)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (25,0,25)),
    light=(ord(" "), (255, 255, 255), (50,0,50)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 100, 0), (0,5,0)),
    light=(ord(">"), (0, 255, 0), (0,10,0)),
)
door = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("+"), (100,50,50), (5,5,5)),
    light=(ord("+"), (150,75,75), (10,10,10))
)

vault_floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255,255,255), (0,0,10)),
    light=(ord(" "), (255,255,255), (0,0,20)),
)

tunnel_floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255,255,255,), (0,50,0)),
    light=(ord(" "), (255,255,255), (0,100,0))
)