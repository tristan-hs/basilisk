from components import ai
from components import consumable
from entity import Actor, Item
import color
from render_order import RenderOrder
import random
 
player = Actor(
    char="@",
    color=color.player,
    name="Basilisk",
    ai_cls=ai.HostileEnemy,
    render_order=RenderOrder.PLAYER,
    description="Of course I know him. He's me!"
)

statue = Actor(
    char="0",
    color=color.statue,
    name="Statue",
    ai_cls=ai.Statue,
    description="Can't do much, but drops loot all the same."
)
goblin = Actor(
    char="1",
    color=color.goblin,
    name="Goblin",
    ai_cls=ai.HostileEnemy,
    description="Will rush you on sight."
)
jackelope = Actor(
    char="1",
    color=color.jackelope,
    name="Jackelope",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Moves 2 tiles per turn!"
)
ogre = Actor(
    char="2",
    color=color.ogre,
    name="Ogre",
    ai_cls=ai.HostileEnemy,
    description="Large and slow."
)
dragon = Actor(
    char="3",
    color=color.dragon,
    name="Dragon",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Large and fast!"
)
titan = Actor(
    char="4",
    color=color.titan,
    name="Titan",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Durable and fast!"
)
lich = Actor(
    char="5",
    color=color.lich,
    name="Lich",
    ai_cls=ai.HostileEnemy,
    description="Slow, but hard to kill."
)
demon = Actor(
    char="4",
    color=color.demon,
    name="Demon",
    ai_cls=ai.HostileEnemy,
    move_speed=3,
    description="A speed demon, to be precise."
)
war_god = Actor(
    char="7",
    color=color.war_god,
    name="War God",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Holy calamity"
)
elder = Actor(
    char="8",
    color=color.elder,
    name="Elder",
    ai_cls=ai.HostileEnemy,
    move_speed=1,
    description="Slow seeping madness, nigh unkillable"
)
decider = Actor(
    char="9",
    color=color.decider,
    name="The Decider",
    ai_cls=ai.HostileEnemy,
    move_speed=4,
    description="The fastest + most durable thing in the dungeon (so far)"
)

enemies = [statue,goblin,jackelope,ogre,dragon,titan,lich,demon,war_god,elder,decider]

vowel_segment = Item(
    item_type='v',
    color=color.vowel,
    name="vowel",
    edible=consumable.NothingConsumable(),
    spitable=consumable.Projectile(damage=1),
)

fire_segment = Item(
    item_type='c',
    color=color.fire,
    name="explosive",
    edible=consumable.NothingConsumable(),
    spitable=consumable.FireballDamageConsumable(damage=1, radius=1),
)

mind_segment = Item(
    item_type='c',
    color=color.mind,
    name="shifting",
    edible=consumable.ChangelingConsumable(),
    spitable=consumable.ConfusionConsumable(number_of_turns=10),
)

electric_segment = Item(
    item_type='c',
    color=color.electric,
    name="electric",
    edible=consumable.NothingConsumable(),
    spitable=consumable.LightningDamageConsumable(damage=4,maximum_range=5),
)

reversal_segment = Item(
    item_type='c',
    color=color.reversal,
    name="backwards",
    edible=consumable.ReversingConsumable(),
    spitable=consumable.Projectile(damage=1),
)

familiar_segment = Item(
    item_type='c',
    color=color.mind,
    name="familiar",
    edible=consumable.IdentifyingConsumable(),
    spitable=consumable.ThirdEyeBlindConsumable()
)

insightful_segment = Item(
    item_type='c',
    color=color.mind,
    name="insightful",
    edible=consumable.RearrangingConsumable(),
    spitable=consumable.MappingConsumable()
)

warped_segment = Item(
    item_type='c',
    color=color.mind,
    name="warped",
    edible=consumable.ConsumingConsumable(),
    spitable=consumable.Projectile(damage=3)
)

forked_segment = Item(
    item_type='c',
    color=color.tongue,
    name="forked",
    edible=consumable.ChokingConsumable(),
    spitable=consumable.Projectile(damage=3)
)

c_segments = [
    fire_segment,
    mind_segment,
    electric_segment, 
    reversal_segment, 
    familiar_segment, 
    insightful_segment,
    warped_segment,
    forked_segment
]
#c_segments = [forked_segment, familiar_segment]
consonants = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z']
