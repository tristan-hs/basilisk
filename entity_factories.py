from components import ai
from components import consumable
from entity import Actor, Item
import color
from render_order import RenderOrder
import random
 
player = Actor(
    char="@",
    color=color.player,
    name="Player",
    ai_cls=ai.HostileEnemy,
    render_order=RenderOrder.PLAYER
)

statue = Actor(
    char="0",
    color=color.statue,
    name="Statue",
    ai_cls=ai.Statue,
)
goblin = Actor(
    char="1",
    color=color.goblin,
    name="Goblin",
    ai_cls=ai.HostileEnemy,
)
jackelope = Actor(
    char="2",
    color=color.jackelope,
    name="Jackelope",
    ai_cls=ai.HostileEnemy,
    move_speed=2
)
ogre = Actor(
    char="2",
    color=color.ogre,
    name="Ogre",
    ai_cls=ai.HostileEnemy,
)
dragon = Actor(
    char="3",
    color=color.dragon,
    name="Dragon",
    ai_cls=ai.HostileEnemy,
    move_speed=2
)
titan = Actor(
    char="4",
    color=color.titan,
    name="Titan",
    ai_cls=ai.HostileEnemy,
    move_speed=2
)
lich = Actor(
    char="5",
    color=color.lich,
    name="Lich",
    ai_cls=ai.HostileEnemy,
    move_speed=2
)
demon = Actor(
    char="6",
    color=color.demon,
    name="Demon",
    ai_cls=ai.HostileEnemy,
    move_speed=3
)
war_god = Actor(
    char="7",
    color=color.war_god,
    name="War God",
    ai_cls=ai.HostileEnemy,
    move_speed=2
)
elder = Actor(
    char="8",
    color=color.elder,
    name="Elder",
    ai_cls=ai.HostileEnemy,
    move_speed=3
)
decider = Actor(
    char="9",
    color=color.decider,
    name="The Decider",
    ai_cls=ai.HostileEnemy,
    move_speed=4
)

enemies = [statue,goblin,jackelope,ogre,dragon,titan,lich,demon,war_god,elder,decider]

vowel_segment = Item(
    item_type='v',
    color=color.vowel,
    name="Vowel",
    edible=consumable.ChangelingConsumable(),
    spitable=consumable.Projectile(damage=1),
    description="A plain segment."
)

fire_segment = Item(
    item_type='c',
    color=color.fire,
    name="Fire",
    edible=consumable.ReversingConsumable(),
    spitable=consumable.FireballDamageConsumable(damage=1, radius=1),
    description="A smoldering segment."
)

mind_segment = Item(
    item_type='c',
    color=color.mind,
    name="Mind",
    edible=consumable.ReversingConsumable(),
    spitable=consumable.ConfusionConsumable(number_of_turns=10),
    description="A pink, wrinkled segment."
)

electric_segment = Item(
    item_type='c',
    color=color.electric,
    name="Electric",
    edible=consumable.ReversingConsumable(),
    spitable=consumable.LightningDamageConsumable(damage=4,maximum_range=5),
    description="A shocking segment."
)

c_segments = [fire_segment,mind_segment,electric_segment]
consonants = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z']
