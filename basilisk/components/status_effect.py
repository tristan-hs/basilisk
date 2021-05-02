from __future__ import annotations

from basilisk.components.base_component import BaseComponent
from basilisk import color

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
	from basilisk.entity import Actor

class StatusEffect(BaseComponent):
	parent: Actor
	label = "<status>"
	description = "(no description)"
	color = color.grey

	def __init__(self, duration: int, target):
		self.parent = target
		self.duration = duration+self.duration_mod
		self.apply()

	@property
	def duration_mod(self):
		return self.engine.player.MIND

	def decrement(self):
		self.duration -= 1
		if self.duration < 1:
			self.remove()

	def apply(self):
		self.parent.statuses.append(self)

	def remove(self):
		self.parent.statuses.remove(self)
		if self.label and self.parent is self.engine.player:
			self.engine.message_log.add_message(f"You are no longer {self.label}.", color.yellow)
		elif self.label:
			self.engine.message_log.add_message(f"{self.parent.name} is no longer {self.label}.", color.yellow)

	def strengthen(self, strength: int=10):
		self.duration += strength


class BadStatusEffect(StatusEffect):
	@property
	def duration_mod(self):
		return 0 - self.engine.player.MIND


class EnemyStatusEffect(StatusEffect):
	pass


class _StatBoost(StatusEffect):
	label = None
	description = None
	color = None

class StatBoost(_StatBoost):
	def __init__(self, duration: int, target, stat, amount):
		self.amount = amount
		self.stat = stat
		super().__init__(duration, target)

		for status in self.parent.statuses:
			if isinstance(status, _StatBoost) and status.stat == stat:
				status.duration = self.duration = max(status.duration, self.duration)


class Phasing(StatusEffect):
	label="phasing"
	description="can go through walls"
	color=color.purple

	def apply(self):
		super().apply()
		msg = "Your vibrations attune to the stone."
		self.engine.message_log.add_message(msg, color.offwhite)

	def strengthen(self):
		super().strengthen(3)
		msg = "Your particles continue to whir." if self.parent is self.engine.player else f"The {self.parent.name}'s particles continue to whir."
		self.engine.message_log.add_message(msg, color.offwhite)


class PhasedOut(StatusEffect):
	label="phased out"
	description="gone for now"
	color=color.purple

	def apply(self):
		super().apply()
		self.parent.ai.clear_intent()
		msg = f"The {self.parent.name} phases out of existence -- for now."
		self.engine.message_log.add_message(msg, color.offwhite)
		self.parent.blocks_movement = False

	def remove(self):
		super().remove()
		conflict = self.engine.game_map.get_blocking_entity_at_location(*self.parent.xy)

		if conflict:
			msg = f"The {self.parent.label} and {conflict.label} merge into one grotesque but inviable specimen."
			self.engine.message_log.add_message(msg, color.grey)
			self.parent.die()
			conflict.die()
		self.parent.blocks_movement = True



class Leaking(EnemyStatusEffect):
	label="crumbling"
	description="bits are falling off"
	color=color.bile

	def decrement(self):
		self.parent.take_damage(1)
		v = self.engine.game_map.vowel.spawn(self.engine.game_map,*self.parent.xy)
		n = 'n' if v.char not in ['y','u'] else ''
		self.engine.message_log.add_message(f"The {self.parent.name} sheds a{n} ?!", color.grey, v.char, v.color)
		super().decrement()

	def apply(self):
		super().apply()
		self.engine.message_log.add_message(f"The {self.parent.name} starts shedding pieces!", color.offwhite)

	def strengthen(self):
		super().strengthen(3)
		self.engine.message_log.add_message(f"The {self.parent.name} will crumble for even longer.", color.offwhite)



class Shielded(StatusEffect):
	label="shielded"
	description="invulnerable"
	color=color.grey

	def decrement(self, on_turn=True):
		if on_turn:
			return
		self.duration -= 1
		if self.duration < 1:
			self.engine.message_log.add_message("Your stone coating crumbles.", color.yellow)
			self.remove()
		else:
			self.engine.message_log.add_message("Your stone coating deflects the attack.", color.grey)

	def strengthen(self):
		super().strengthen(1)
		self.engine.message_log.add_message("Your stone coating hardens.", color.offwhite)

	def apply(self):
		super().apply()
		self.engine.message_log.add_message("Your scales form a protective stone coating.", color.offwhite)


class Petrified(EnemyStatusEffect):
	label="petrified"
	description="can't move"
	color=color.grey

	def apply(self):
		super().apply()
		self.parent.ai.clear_intent()
		self.engine.message_log.add_message(f"The {self.parent.name} turns to stone!", color.offwhite)

	def strengthen(self):
		super().strengthen(3)
		self.engine.message_log.add_message(f"The {self.parent.name} hardens!", color.offwhite)


class PetrifiedSnake(EnemyStatusEffect):
	label="petrified"
	description="can't move"
	color=color.grey

	def apply(self):
		super().apply()
		self.engine.message_log.add_message("You turn to stone!", color.red)

	def strengthen(self):
		super().strengthen(3)
		self.engine.message_log.add_message("You harden!", color.red)


class FreeSpit(StatusEffect):
	label="salivating"
	description="spit segments without consuming them"
	color=color.snake_green

	def apply(self):
		super().apply()
		self.engine.message_log.add_message("All your spit replenishes.", color.snake_green)

	def strengthen(self):
		super().strengthen(3)
		self.engine.message_log.add_message("Your bile wells up within you.", color.snake_green)


class PetrifEyes(StatusEffect):
	label = "petrifying"
	description = "gaze of stone"
	color = color.cyan

	def apply(self):
		super().apply()
		self.engine.message_log.add_message("All you see turns grey and stoney.", color.yellow)

	def strengthen(self):
		super().strengthen(3)
		self.engine.message_log.add_message("You feel your gaze grow stronger.", color.yellow)


class Choking(BadStatusEffect):
	label = "choking"
	description = "can't spit"
	color = color.tongue

	def apply(self):
		super().apply()
		self.engine.message_log.add_message("You can't spit!", color.red)

	def strengthen(self):
		super().strengthen()
		self.engine.message_log.add_message("Your throat is feeling even worse!", color.red)


class ThirdEyeBlind(BadStatusEffect):
	label ="future blind"
	description = "can't see intents"
	color = color.red
	
	def apply(self):
		super().apply()
		self.engine.message_log.add_message("You are blind to enemy intents!", color.red)

	def strengthen(self):
		super().strengthen()
		self.engine.message_log.add_message("Your foresight is weakened further!", color.red)
