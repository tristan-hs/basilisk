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
    description="Can't do much, but drops loot all the same.",
    drop_tier='c'
)
goblin = Actor(
    char="1",
    color=color.goblin,
    name="Goblin",
    ai_cls=ai.HostileEnemy,
    description="Will rush you on sight.",
    drop_tier='c'
)
jackelope = Actor(
    char="1",
    color=color.jackelope,
    name="Jackelope",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Moves 2 tiles per turn!",
    drop_tier='c'
)
ogre = Actor(
    char="2",
    color=color.ogre,
    name="Ogre",
    ai_cls=ai.HostileEnemy,
    description="Large and slow.",
    drop_tier='c'
)
dragon = Actor(
    char="3",
    color=color.dragon,
    name="Dragon",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Large and fast!",
    drop_tier='u'
)
titan = Actor(
    char="4",
    color=color.titan,
    name="Titan",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Durable and fast!",
    drop_tier='u'
)
lich = Actor(
    char="5",
    color=color.lich,
    name="Lich",
    ai_cls=ai.HostileEnemy,
    description="Slow, but hard to kill.",
    drop_tier='u'
)
demon = Actor(
    char="4",
    color=color.demon,
    name="Demon",
    ai_cls=ai.HostileEnemy,
    move_speed=3,
    description="A speed demon, to be precise.",
    drop_tier='u'
)
war_god = Actor(
    char="7",
    color=color.war_god,
    name="War God",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    description="Holy calamity",
    drop_tier='r'
)
elder = Actor(
    char="8",
    color=color.elder,
    name="Elder",
    ai_cls=ai.HostileEnemy,
    move_speed=1,
    description="Slow seeping madness, nigh unkillable",
    drop_tier='r'
)
decider = Actor(
    char="9",
    color=color.decider,
    name="The Decider",
    ai_cls=ai.HostileEnemy,
    move_speed=4,
    description="The fastest + most durable thing in the dungeon (so far)",
    drop_tier='r'
)

enemies = [statue,goblin,jackelope,ogre,dragon,titan,lich,demon,war_god,elder,decider]

vowel_segment = Item(
    item_type='v',
    color=color.vowel,
    name="vowel",
    edible=consumable.NothingConsumable(),
    spitable=consumable.Projectile(damage=1),
)

fireball = Item(
    item_type='c',
    color=color.fire,
    name="explosive",
    edible=consumable.ChokingConsumable(),
    spitable=consumable.FireballDamageConsumable(damage=2, radius=1),
    rarity='c'
)

confusion = Item(
    item_type='c',
    color=color.mind,
    name="confusing",
    edible=consumable.ChokingConsumable(),
    spitable=consumable.ConfusionConsumable(number_of_turns=10),
    rarity='u'
)

changeling = Item(
    item_type='c',
    color=color.mind,
    name="shifting",
    edible=consumable.ChangelingConsumable(),
    spitable=consumable.Projectile(damage=2),
    rarity='u'
)

electric = Item(
    item_type='c',
    color=color.electric,
    name="electric",
    edible=consumable.ConsumingConsumable(),
    spitable=consumable.LightningDamageConsumable(damage=4,maximum_range=8),
    rarity='u'
)

reversal = Item(
    item_type='c',
    color=color.reversal,
    name="backwards",
    edible=consumable.ReversingConsumable(),
    spitable=consumable.Projectile(damage=2),
    rarity='u'
)

familiar = Item(
    item_type='c',
    color=color.mind,
    name="familiar",
    edible=consumable.IdentifyingConsumable(),
    spitable=consumable.ThirdEyeBlindConsumable(),
    rarity='c'
)

mapping = Item(
    item_type='c',
    color=color.mind,
    name="crinkly",
    edible=consumable.MappingConsumable(),
    spitable=consumable.ThirdEyeBlindConsumable(),
    rarity='u'
)

insightful = Item(
    item_type='c',
    color=color.mind,
    name="insightful",
    edible=consumable.RearrangingConsumable(),
    spitable=consumable.ThirdEyeBlindConsumable(),
    rarity='r'
)

warped = Item(
    item_type='c',
    color=color.mind,
    name="warped",
    edible=consumable.ConsumingConsumable(),
    spitable=consumable.Projectile(damage=5),
    rarity='u'
)

forked = Item(
    item_type='c',
    color=color.tongue,
    name="forked",
    edible=consumable.ChokingConsumable(),
    spitable=consumable.Projectile(damage=3),
    rarity='c'
)

y_segment = Item(
    item_type='y',
    color=color.unidentified,
    name="mYsterious",
    edible=consumable.NothingConsumable(),
    spitable=consumable.Projectile(damage=2)
)

petrif_eyes = Item(
    item_type='c',
    color=color.cyan,
    name="eye-covered",
    edible=consumable.PetrifEyesConsumable(),
    spitable=consumable.ThirdEyeBlindConsumable(),
    rarity='r'
)

bulky = Item(
    item_type='c',
    color=color.tongue,
    name="bulky",
    edible=consumable.FreeSpitConsumable(),
    spitable=consumable.Projectile(damage=5),
    rarity='r'
)

c_segments = [
    fireball,confusion,changeling,electric,reversal,familiar,mapping,insightful,warped,forked,petrif_eyes,bulky
    #bulky
]
c_segments2 = [
    fireball, familiar, confusion, changeling, electric, reversal, insightful, petrif_eyes
]
consonants = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','z']
