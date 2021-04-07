from __future__ import annotations
from components.base_component import BaseComponent

import color

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
	from entity import Actor

class StatusEffect(BaseComponent):
	parent: Actor
	label = "<status>"
	description = "(no description)"
	color = color.grey

	def __init__(self, duration: int, target):
		self.duration = duration
		self.parent = target
		self.apply()

	def decrement(self):
		self.duration -= 1
		if self.duration == 0:
			self.remove()

	def apply(self):
		self.parent.statuses.append(self)

	def remove(self):
		self.parent.statuses.remove(self)
		self.engine.message_log.add_message(f"You are no longer {self.label}.", color.yellow)

	def strengthen(self, strength: int=10):
		self.duration += strength


class ThirdEyeBlind(StatusEffect):
	label ="TE Blind"
	description = "can't see intents"
	color = color.red
	
	def apply(self):
		super().apply()
		self.engine.message_log.add_message("You are blind to enemy intents!", color.red)

	def strengthen(self):
		super().strengthen()
		self.engine.message_log.add_message("Your foresight is weakened further!", color.red)
