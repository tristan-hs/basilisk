from __future__ import annotations

import os

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

import tcod.event
import math

from basilisk import actions, color, exceptions
from basilisk.actions import (
    Action,
    BumpAction,
    WaitAction,
    PickupAction,
)

if TYPE_CHECKING:
    from basilisk.engine import Engine
    from basilisk.entity import Item

import utils

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}


CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

CURSOR_X_KEYS = {
    tcod.event.K_LEFT: -1,
    tcod.event.K_RIGHT: 1,
    tcod.event.K_h: -1,
    tcod.event.K_l: 1
}


ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.grey)
            return False  # Skip enemy turn on exceptions.

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym

        modifier = event.mod
 
        player = self.engine.player
 
        if key == tcod.event.K_PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            return HistoryViewer(self.engine)

        elif key == tcod.event.K_i:
            return InventorySelectHandler(self.engine)
        elif key == tcod.event.K_s:
            return InventorySpitHandler(self.engine)
        elif key == tcod.event.K_d:
            return InventoryDigestHandler(self.engine)

        elif key == tcod.event.K_SLASH:
            return LookHandler(self.engine)

        elif key == tcod.event.K_c:
            self.engine.show_instructions = not self.engine.show_instructions

        # No valid key was pressed
        return action

class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)

class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists(utils.get_resource("savegame.sav")):
            os.remove(utils.get_resource("savegame.sav"))  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()
        
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()


class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    TITLE = "<missing title>"
    tooltip = "(d)igest/(s)pit"

    def __init__(self, engine: Engine, i_filter=lambda x: True):
        super().__init__(engine)
        self.items = [i for i in engine.player.inventory.items if i_filter(i)]
        self.inventory_length = len(self.items)
        self.cursor = 0
        self.frame_width = max(len(i) for i in (self.TITLE, range(31), self.tooltip) if i is not None)+4
        if engine.player.x <= 30:
            self.frame_x = 80-self.frame_width-1
        else:
            self.frame_x = 1
        self.frame_y = 1

    @property
    def highlighted_item(self) -> Optional[Item]:
        if self.inventory_length > max(self.cursor,0):
            return self.items[self.cursor]
        return None

    def get_frame_height(self, console: tcod.Console) -> int:
        if self.highlighted_item:
            inner = console.get_height_rect(
                self.frame_x+1,self.frame_y+1,self.frame_width-2,47,self.highlighted_item.description
            )+2
        else:
            inner = 1

        return inner+2

    def highlight_item(self, console: tcod.Console):
        x, y = self.highlighted_item.xy
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def render_item_panel(self, console: tcod.Console):
        # print main popup
        console.draw_frame(
            x=self.frame_x,
            y=self.frame_y,
            width=self.frame_width,
            height=self.frame_height,
            title=self.TITLE,
            clear=True,
            fg=(50, 150, 50),
            bg=(0, 0, 0),
        )

        if self.highlighted_item:
            console.print(self.frame_x+1, self.frame_y+1, self.highlighted_item.label, self.highlighted_item.color)
            console.print_box(self.frame_x+1,self.frame_y+3,self.frame_width-2,self.frame_height-4,self.highlighted_item.description,color.offwhite)
        else:
            console.print(self.frame_x+1,self.frame_y+1,"(None)", color.grey)

    def render_items_drawer(self, console: tcod.Console):
        console.draw_frame(
            x=self.frame_x+1,
            y=self.frame_y+self.frame_height-1,
            width=self.frame_width-2 if self.frame_width % 2 != 0 else self.frame_width - 3,
            height=3,
            clear=True,
            fg=(100,100,100),
            bg=(0,0,0)
        )

        space = self.frame_width-6 if self.frame_width % 2 == 0 else self.frame_width-5
        start_at = min(self.cursor - (space/2), len(self.items)-space-1)
        end_at = max(start_at,0) + space
        i = 0
        for k, v in enumerate(self.items):
            if k < start_at:
                continue
            if k > end_at:
                break
            fg = color.black if v is self.highlighted_item else v.color
            bg = color.white if v is self.highlighted_item else color.black
            console.print(self.frame_x+2+i, self.frame_y+self.frame_height, v.char, fg=fg, bg=bg)
            i += 1

    def render_tooltip(self, console: tcod.Console):
        w = self.frame_width if self.frame_width % 2 == 0 else self.frame_width - 1
        ttw = len(self.tooltip) if len(self.tooltip) % 2 == 0 else len(self.tooltip) - 1
        ttx = int(self.frame_x + (w/2) - (ttw/2))
        console.print(ttx, self.frame_y+self.frame_height-1, self.tooltip)

    def render_menu(self, console: tcod.Console):
        self.frame_height = self.get_frame_height(console)

        if self.highlighted_item:
            self.render_items_drawer(console)

        if self.highlighted_item:
            self.highlight_item(console)

        self.render_item_panel(console)

        if self.tooltip:
            self.render_tooltip(console)


    def on_render(self, console: tcod.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        self.render_menu(console)


    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        if len(self.items) < 1:
            return super().ev_keydown(event)

        # Scroll through inventory
        if event.sym in CURSOR_X_KEYS:
            adjust = CURSOR_X_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = max(self.inventory_length - 1, 0)
            elif adjust > 0 and self.cursor == self.inventory_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.inventory_length - 1))

            return None

        # Select item
        elif event.sym in CONFIRM_KEYS and self.highlighted_item:
            return self.on_item_selected(self.highlighted_item)

        elif event.sym in (tcod.event.K_d, tcod.event.K_s):
            return self.on_item_used(self.highlighted_item, event)

        return super().ev_keydown(event)


    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        return None

    def on_item_used(self, item: Item, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        return None

    def spit_item(self, item):
        return item.spitable.get_throw_action(self.engine.player)

    def eat_item(self, item):
        return item.edible.get_eat_action(self.engine.player)

class InventorySelectHandler(InventoryEventHandler):
    TITLE = "Select a segment"

    def on_item_used(self, item: Item, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        if event.sym == tcod.event.K_s:
            return self.spit_item(item)

        elif event.sym == tcod.event.K_d:
            return self.eat_item(item)


class InventorySpitHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select a segment to spit"
    tooltip = None

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Return the action for the selected item."""
        return self.spit_item(item)


class InventoryDigestHandler(InventoryEventHandler):
    TITLE = "Select a segment to digest"
    tooltip = None

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        return self.eat_item(item)


class InventoryIdentifyHandler(InventoryEventHandler):
    TITLE = "Select a segment to identify"
    tooltip = None

    def __init__(self,engine: Engine, identifier: Item):
        super().__init__(engine, lambda x:x.identified == False and x.char != identifier.char)
        self.identifier = identifier

    def on_item_selected(self, item: Optional[Item]) -> Optional[ActionOrHandler]:
        return actions.ItemAction(self.engine.player, self.identifier, target_item=item)

    def on_exit(self):
        if self.identifier.identified:
            return super().on_exit()

class InventoryRearrangeHandler(InventoryEventHandler):
    TITLE = "Type yourself out"
    tooltip = None

    def __init__(self, engine: Engine, rearranger: Item):
        super().__init__(engine, lambda x:x is not rearranger)
        self.rearranger = rearranger
        self.selected_items = []
        self.all_items = self.engine.player.inventory.items[:]

    def on_exit(self):
        if self.rearranger.identified:
            return super().on_exit()

    def render_menu(self, console: tcod.Console):
        self.frame_height = 3

        self.render_items_drawer(console)
        self.render_input_panel(console)

    def render_input_panel(self, console: tcod.Console):
        console.draw_frame(
            x=self.frame_x,
            y=self.frame_y,
            width=self.frame_width,
            height=self.frame_height,
            clear=True,
            fg=(50,150,50),
            bg=(0,0,0)
        )

        chars = ''.join([i.char for i in self.selected_items])+'_'*len(self.items)
        console.print(self.frame_x+1,self.frame_y+1,chars,fg=color.grey)

    def on_item_selected(self, item: Optional[Item]):
        self.items.remove(item)
        self.selected_items.append(item)
        if self.cursor > len(self.items)-1:
            self.cursor = len(self.items)-1

        if len(self.items) == 0:
            new_order = self.selected_items + [self.rearranger]

            poses = [i.xy for i in self.all_items]
            for s, segment in enumerate(new_order):
                new_order[s].place(*poses[s])

            self.engine.player.inventory.items = new_order

            return actions.ItemAction(self.engine.player, self.rearranger)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))

class SingleProjectileAttackHandler(SelectIndexHandler):
    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int,int]], Optional[Action]]
    ):
        super().__init__(engine)
        self.callback = callback

    @property
    def path_to_target(self):
        x,y = self.engine.mouse_location
        if not self.engine.game_map.visible[x,y]:
            return None
        return self.engine.player.ai.get_path_to(x,y,0)

    def on_render(self, console: tcod.Console)->None:
        # render the line
        super().on_render(console)
        
        if not self.path_to_target:
            return

        for px,py in self.path_to_target:
            console.tiles_rgb["bg"][px, py] = color.white
            console.tiles_rgb["fg"][px, py] = color.black

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        # select based on the line
        if not self.path_to_target:
            return None
        for px,py in self.path_to_target:
            if self.engine.game_map.get_actor_at_location(px,py):
                return self.callback((px,py))

class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location
        radius = self.radius

        i = x - radius
        while i <= x+radius:
            j=y-radius
            while j <= y+radius:
                if math.sqrt((x-i)**2 + (y-j)**2) <= radius:
                    console.tiles_rgb["bg"][i, j] = color.white
                    console.tiles_rgb["fg"][i, j] = color.black
                j+=1
            i+=1

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))

class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent