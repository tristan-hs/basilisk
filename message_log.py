from typing import Iterable, List, Reversible, Tuple
import textwrap

import tcod

import color


class Message:
    def __init__(self, text: str, fg: Tuple[int, int, int], message_log, arg: str = None, arg_color: str = None):
        if arg:
            self.plain_text = arg.join(text.split('?'))
        else:
            self.plain_text = text
        self.text = text
        self.fg = fg
        self.count = 1
        self.parent = message_log
        self.turn_count = self.parent.engine.turn_count
        self.arg = arg
        self.arg_color = arg_color

    @property
    def full_text(self) -> str:
        """The full text of this message, including the count if necessary."""
        return self.plain_text


class MessageLog:
    def __init__(self, engine) -> None:
        self.messages: List[Message] = []
        self.engine = engine

    def add_message(
        self, text: str, fg: Tuple[int, int, int] = color.grey, arg: str = None, arg_color: str = None
    ) -> None:
        """Add a message to this log.
        `text` is the message text, `fg` is the text color.
        If `stack` is True then the message can stack with a previous message
        of the same text.
        """
        if arg:
            ftext = arg.join(text.split('?'))
        else:
            ftext = text

        last_msg = self.messages[-1] if self.messages else None
        if self.messages and self.engine.turn_count != last_msg.turn_count and last_msg.text[0] != '_':
                last_msg.text = '_'+last_msg.text
                last_msg.plain_text = '_'+last_msg.plain_text

        self.messages.append(Message(text, fg, self, arg, arg_color))

    def render(
        self, console: tcod.Console, x: int, y: int, width: int, height: int,
    ) -> None:
        """Render this log over the given area.
        `x`, `y`, `width`, `height` is the rectangular region to render onto
        the `console`.
        """
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """Return a wrapped text message."""
        for line in string.splitlines():  # Handle newlines in messages.
            yield from textwrap.wrap(
                line, width, expand_tabs=True,
            )

    @classmethod
    def render_messages(
        cls,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        """Render the messages provided.
        The `messages` are rendered starting at the last message and working
        backwards.
        """
        y_offset = height - 1

        for message in reversed(messages):
            i = 0
            arg_printed = False
            for line in reversed(list(cls.wrap(message.full_text, width))):
                if message.arg and i + len(line) > len(message.text.split('?')[1]) and arg_printed == False:
                    # we've printed backwards up to a line w/ an argument
                    pos = len(message.text.split('?')[1])-i
                    pos2 = pos + len(message.arg)

                    console.print(x=x, y=y+y_offset,string=line[:-pos2], fg=message.fg)
                    console.print(x=x+len(line)-pos2, y=y+y_offset, string=line[-pos2:-pos],fg=message.arg_color)
                    arg_printed = True
                    console.print(x=x+len(line)-pos, y=y+y_offset, string=line[-pos:], fg=message.fg)
                else:
                    console.print(x=x, y=y + y_offset, string=line, fg=message.fg)
                y_offset -= 1                
                if y_offset < 0:
                    return  # No more space to print messages.
                i += len(line)+1
