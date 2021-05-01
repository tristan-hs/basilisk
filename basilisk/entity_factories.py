import random

from basilisk.components import ai, consumable
from basilisk.entity import Actor, Item
from basilisk import color
from basilisk.render_order import RenderOrder
 
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
    char="6",
    color=color.decider,
    name="The Decider",
    ai_cls=ai.HostileEnemy,
    move_speed=4,
    description="The fastest + most durable thing in the dungeon (so far)",
    drop_tier='r'
)

final_boss = Actor(
    char="9",
    color=color.purple,
    name="Voidmaw",
    ai_cls=ai.Statue,
    move_speed=0,
    description="The object of your quest",
    drop_tier='r',
    is_boss=True
)

enemies = [statue,goblin,jackelope,ogre,dragon,titan,lich,demon,war_god,elder,decider]
enemy_sets = [
[statue,    goblin,     jackelope,  goblin,     goblin],
[statue,    goblin,     jackelope,  jackelope,  ogre],
[goblin,    ogre,       jackelope,  lich,       lich, statue],

[ogre,      dragon,     titan,      lich,       lich, statue],
[lich,      dragon,     titan,      lich,       elder, statue],
[lich,      titan,      demon,      lich,       elder, statue],

[lich,      titan,      demon,      war_god,    elder, statue],
[elder,     demon,      demon,      war_god,    war_god, statue],
[elder,     elder,      elder,      war_god,    decider, statue],

[statue,goblin,jackelope,ogre,dragon,titan,lich,demon,war_god,elder,decider],
[decider,elder,war_god]
]

vowel_segment = Item(
    item_type='v',
    color=color.vowel,
    name="vowel",
    edible=consumable.StatBoostConsumable(1),
    spitable=consumable.Projectile(damage=1),
    stat=None,
    flavor="Rusted scrap and compost from the dungeon floor."
)

crown_segment = Item(
    item_type='o',
    color=color.purple,
    name='crown',
    edible=consumable.NothingConsumable(),
    spitable=consumable.NothingConsumable(),
    rarity='a',
    stat=None
)


volatile = Item(
    item_type='c',
    color=color.bile,
    name='volatile',
    edible=consumable.StatBoostConsumable(2,'BILE'),
    spitable=consumable.FireballDamageConsumable(damage=2, radius=3),
    rarity='c',
    stat='BILE',
    flavor='The metal heart of some ancient titan, leaking acrid pus.'
)

forceful = Item(
    item_type='c',
    color=color.bile,
    name='forceful',
    edible=consumable.KnockbackConsumable(),
    spitable=consumable.KnockbackProjectile(),
    rarity='u',
    stat='BILE',
    flavor='Your touch is repelled by an aura of repulsion.'
)

drilling = Item(
    item_type='c',
    color=color.bile,
    name='drilling',
    edible=consumable.ChokingConsumable(),
    spitable=consumable.DrillingProjectile(2),
    rarity='u',
    stat='BILE',
    flavor='A spiraling metal coil that glimmers with ambition.'
)

prolific = Item(
    item_type='c',
    color=color.bile,
    name='prolific',
    edible=consumable.FreeSpitConsumable(),
    spitable=consumable.LeakingProjectile(),
    rarity='u',
    stat='BILE',
    flavor='A sloshing grey ooze whose tendrils stretch for whatevery may fuel its growth.'
)

acidic = Item(
    item_type='c',
    color=color.bile,
    name='acidic',
    edible=consumable.StatBoostConsumable(1,'BILE',True),
    spitable=consumable.NothingConsumable(),
    rarity='r',
    stat='BILE'
)

petrified = Item(
    item_type='c',
    color=color.mind,
    name='petrified',
    edible=consumable.PetrifyConsumable(),
    spitable=consumable.PetrifyEnemyConsumable(),
    rarity='c',
    stat='MIND',
    flavor="A giant eye of cracked and weathered stone."
)

ghostly = Item(
    item_type='c',
    color=color.mind,
    name='ghostly',
    edible=consumable.PhasingConsumable(),
    spitable=consumable.PhasingProjectile(),
    rarity='u',
    stat='MIND',
    flavor="This cloud of ethereal resin tempts you with the comfort of the void."
)

cursed = Item(
    item_type='c',
    color=color.mind,
    name='cursed',
    edible=consumable.NotConsumable(),
    spitable=consumable.NotConsumable(),
    rarity='u',
    stat='MIND',
    flavor="lol get rekt"
)

calcified = Item(
    item_type='c',
    color=color.mind,
    name='calcified',
    edible=consumable.ShieldingConsumable(),
    spitable=consumable.PetrifEyesConsumable(),
    rarity='r',
    stat='MIND',
    flavor="As you move you hear it chewing bone and gravel."
)

wrinkled = Item(
    item_type='c',
    color=color.mind,
    name='wrinkled',
    edible=consumable.NothingConsumable(),
    spitable=consumable.NothingConsumable(),
    rarity='r',
    stat='MIND'
)

musclebound = Item(
    item_type='c',
    color=color.tail,
    name='musclebound',
    edible=consumable.StatBoostConsumable(2,'TAIL'),
    spitable=consumable.Projectile(damage=3),
    rarity='c',
    stat='TAIL',
    flavor="Dense, rippling cords of flesh, wound together like a ball of yarn."
)

annoying = Item(
    item_type='c',
    color=color.tail,
    name='annoying',
    edible=consumable.ConsumingConsumable(),
    spitable=consumable.NothingConsumable(),
    rarity='u',
    stat='TAIL'
)

backward = Item(
    item_type='c',
    color=color.tail,
    name='backward',
    edible=consumable.ReversingConsumable(),
    spitable=consumable.SpittingConsumable(),
    rarity='u',
    stat='TAIL',
    flavor=random.choice([
        "O, stone, be not so.",
        "At evil's eyes walks I, Lisa. By Basilisk Laws, eyes live. Ta!",
        "*Nod*, I did loot a ogre, ergo a tool did I don."
    ])
)

pure = Item(
    item_type='c',
    color=color.tail,
    name='pure',
    edible=consumable.RearrangingConsumable(),
    spitable=consumable.DroppingConsumable(),
    rarity='u',
    stat='TAIL',
    flavor="Each perfect facet grants a new dimension of clarity."
)

growing = Item(
    item_type='c',
    color=color.tail,
    name='growing',
    edible=consumable.StatBoostConsumable(1,'TAIL',True),
    spitable=consumable.NothingConsumable(),
    rarity='r',
    stat='TAIL'
)

learned = Item(
    item_type='c',
    color=color.tongue,
    name='learned',
    edible=consumable.IdentifyingConsumable(),
    spitable=consumable.ThirdEyeBlindConsumable(),
    rarity='c',
    stat='TONG',
    flavor="A heap of brains twitching in unity; it whispers secrets as you travel"
)

longue = Item(
    item_type='c',
    color=color.tongue,
    name='long',
    edible=consumable.StatBoostConsumable(3,'TONG'),
    spitable=consumable.HookshotProjectile(),
    rarity='c',
    stat='TONG',
    flavor="A coil of wet pink flesh branching off into prehensile tendrils."
)

inquisitive = Item(
    item_type='c',
    color=color.tongue,
    name='inquisitive',
    edible=consumable.MappingConsumable(),
    spitable=consumable.IdentifyingProjectile(),
    rarity='u',
    stat='TONG',
    flavor="As close as you'll' come to looking in a mirror; when you see it, you see it knows you"
)

hungry = Item(
    item_type='c',
    color=color.tongue,
    name='hungry',
    edible=consumable.VacuumConsumable(),
    spitable=consumable.NothingConsumable(),
    rarity='u',
    stat='TONG'
)

sensitive = Item(
    item_type='c',
    color=color.tongue,
    name='sensitive',
    edible=consumable.StatBoostConsumable(1,'TONG',True),
    spitable=consumable.ClingyConsumable(),
    rarity='r',
    stat='TONG',
    flavor="This soft orb oozes appreciation at the slightest acknowledgement."
)


c_segments = [
    volatile, forceful, drilling, prolific, acidic, petrified, ghostly, cursed, calcified, wrinkled, musclebound, annoying, backward, pure, growing, learned, longue, inquisitive, hungry, sensitive
    #hungry
]
consonants = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','z']
