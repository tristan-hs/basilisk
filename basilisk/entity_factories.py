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
    description="That's you!"
)

statue = Actor(
    char="0",
    color=color.statue,
    name="Statue",
    ai_cls=ai.Statue,
    move_speed=0,
    drop_tier='c',
    flavor="A former denizen of the dungeon, taken by the earth."
)
goblin = Actor(
    char="1",
    color=color.goblin,
    name="Goblin",
    ai_cls=ai.HostileEnemy,
    drop_tier='c',
    flavor="Clever enough to know the value of your loot, but not enough to see it doesn't pose a threat."
)
jackelope = Actor(
    char="1",
    color=color.jackelope,
    name="Jackelope",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    drop_tier='c',
    flavor="Natural prey to the basilisk, but quick to dispatch a careless hunter."
)
ogre = Actor(
    char="2",
    color=color.ogre,
    name="Ogre",
    ai_cls=ai.HostileEnemy,
    flavor="Oft found fumbling slow through dank dungeon corners for rats and bugs.",
    drop_tier='c'
)
mongoose = Actor(
    char="3",
    color=color.mongoose,
    name="Dire Badger",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    drop_tier='u',
    flavor="Dire badger don't care, it just takes what it wants."
)
dragon = Actor(
    char="4",
    color=color.dragon,
    name="Dragon",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    flavor='Beware its armour like tenfold shields and wings a hurricane.',
    drop_tier='u'
)
lich = Actor(
    char="5",
    color=color.lich,
    name="Lich",
    ai_cls=ai.HostileEnemy,
    drop_tier='u',
    flavor="Stalks all who disturb it with a tireless vendetta."
)
demon = Actor(
    char="4",
    color=color.demon,
    name="King Cobra",
    ai_cls=ai.HostileEnemy,
    move_speed=3,
    flavor="A predator worthy of its name.",
    drop_tier='u'
)
war_god = Actor(
    char="7",
    color=color.war_god,
    name="Titan",
    ai_cls=ai.HostileEnemy,
    move_speed=2,
    flavor="Holy calamity, wrought to destroy and caged here beneath the earth.",
    drop_tier='r'
)
elder = Actor(
    char="7",
    color=color.elder,
    name="Giant Mite",
    ai_cls=ai.HostileEnemy,
    move_speed=1,
    flavor="A slow but nigh-unkillable pest.",
    drop_tier='r'
)
decider = Actor(
    char="8",
    color=color.decider,
    name="Dire Mongoose",
    ai_cls=ai.HostileEnemy,
    move_speed=3,
    flavor="At the hole where he went in\nRed-Eye called to Wrinkle-Skin.\nHear what little Red-Eye saith:\nNag, come up and dance with death!",
    drop_tier='r'
)

final_boss = Actor(
    char="9",
    color=color.purple,
    name="One Below",
    ai_cls=ai.Statue,
    move_speed=0,
    flavor="The origin of this dungeon's evil. Only you can stop it.",
    drop_tier='r',
    is_boss=True
)

decoy = Actor(
    char="!",
    color=color.player,
    name="Decoy",
    ai_cls=ai.Statue,
    move_speed=0,
    description="Smells faintly of gingerbread",
    drop_tier='c'
)

enemies = [statue,goblin,jackelope,ogre,dragon,mongoose,lich,demon,war_god,elder,decider]
enemy_sets = [
[statue,    goblin,     jackelope,  goblin,     goblin],
[statue,    goblin,     jackelope,  jackelope,  ogre],
[goblin,    ogre,       jackelope,  lich,       lich],

[ogre,      mongoose,   dragon,      lich,       lich],
[lich,      mongoose,   dragon,      lich,       elder],
[lich,      dragon,     demon,       lich,       elder],

[lich,      dragon,     demon,      war_god,    elder],
[elder,     demon,      demon,      war_god,    war_god],
[elder,     elder,      elder,      war_god,    decider],

[statue,goblin,jackelope,ogre,dragon,mongoose,lich,demon,war_god,elder,decider],
[decider,elder,war_god]
]

vowel_segment = Item(
    item_type='v',
    color=color.vowel,
    name="vowel",
    edible=consumable.StatBoostConsumable(1),
    spitable=consumable.Projectile(damage=1),
    stat=None,
    flavor="Rusted scrap and compost given vigor by your presence."
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
    name='explosive',
    edible=consumable.StatBoostConsumable(2,'BILE'),
    spitable=consumable.FireballDamageConsumable(damage=3, radius=2),
    rarity='c',
    stat='BILE',
    flavor='The metal heart of some ancient titan, leaking acrid pus.'
)

forceful = Item(
    item_type='c',
    color=color.bile,
    name='force',
    edible=consumable.KnockbackConsumable(),
    spitable=consumable.KnockbackProjectile(),
    rarity='u',
    stat='BILE',
    flavor='Your touch is stayed by an aura of repulsion.'
)

drilling = Item(
    item_type='c',
    color=color.bile,
    name='drill',
    edible=consumable.ChokingConsumable(),
    spitable=consumable.DrillingProjectile(3),
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
    flavor='A sloshing grey ooze whose tendrils stretch for whatever may fuel its growth.'
)

acidic = Item(
    item_type='c',
    color=color.bile,
    name='acid',
    edible=consumable.StatBoostConsumable(1,'BILE',True),
    spitable=consumable.DamageAllConsumable(damage=3),
    rarity='r',
    stat='BILE',
    flavor='Carved from the fangs of your predecessor, this segment still drips with their legendary venom.'
)

petrified = Item(
    item_type='c',
    color=color.mind,
    name='petrify',
    edible=consumable.PetrifyConsumable(),
    spitable=consumable.PetrifyEnemyConsumable(),
    rarity='c',
    stat='MIND',
    flavor="A giant eye of cracked and weathered stone."
)

ghostly = Item(
    item_type='c',
    color=color.mind,
    name='phase',
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
    name='hardened',
    edible=consumable.ShieldingConsumable(),
    spitable=consumable.PetrifEyesConsumable(),
    rarity='r',
    stat='MIND',
    flavor="As you move it chews the bone and gravel beneath you."
)

wrinkled = Item(
    item_type='c',
    color=color.mind,
    name='wrinkled',
    edible=consumable.TimeReverseConsumable(),
    spitable=consumable.WormholeConsumable(),
    rarity='r',
    stat='MIND',
    flavor="\"A straight line is not the shortest distance between two points,\" it assures you."
)

musclebound = Item(
    item_type='c',
    color=color.tail,
    name='ripped',
    edible=consumable.StatBoostConsumable(2,'TAIL'),
    spitable=consumable.Projectile(damage=4),
    rarity='c',
    stat='TAIL',
    flavor="Dense, rippling cords of flesh, wound together like a ball of yarn."
)

annoying = Item(
    item_type='c',
    color=color.tail,
    name='decoy',
    edible=consumable.ConsumingConsumable(),
    spitable=consumable.DecoyConsumable(),
    rarity='u',
    stat='TAIL',
    flavor=">:P"
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
    name='insightful',
    edible=consumable.RearrangingConsumable(),
    spitable=consumable.DroppingConsumable(),
    rarity='u',
    stat='TAIL',
    flavor="Each perfect side grants a new dimension of clarity."
)

growing = Item(
    item_type='c',
    color=color.tail,
    name='evolving',
    edible=consumable.StatBoostConsumable(1,'TAIL',True),
    spitable=consumable.EntanglingConsumable(),
    rarity='r',
    stat='TAIL',
    flavor="Creeping vines emerge where it passes."
)

learned = Item(
    item_type='c',
    color=color.tongue,
    name='identify',
    edible=consumable.IdentifyingConsumable(),
    spitable=consumable.ThirdEyeBlindConsumable(),
    rarity='c',
    stat='TONG',
    flavor="A cohesion of twitching cortical matter; it whispers secrets as you travel."
)

longue = Item(
    item_type='c',
    color=color.tongue,
    name='hooked',
    edible=consumable.StatBoostConsumable(3,'TONG'),
    spitable=consumable.HookshotProjectile(),
    rarity='c',
    stat='TONG',
    flavor="A coil of prehensile and toothed tendrils."
)

inquisitive = Item(
    item_type='c',
    color=color.tongue,
    name='reference',
    edible=consumable.MappingConsumable(),
    spitable=consumable.IdentifyingProjectile(),
    rarity='u',
    stat='TONG',
    flavor="It offers no warranty for the truths within."
)

hungry = Item(
    item_type='c',
    color=color.tongue,
    name='hungry',
    edible=consumable.VacuumConsumable(),
    spitable=consumable.VacuumProjectile(),
    rarity='u',
    stat='TONG',
    flavor="Slathering maws adorn its every side. They cry to be fed."
)

sensitive = Item(
    item_type='c',
    color=color.tongue,
    name='sense',
    edible=consumable.StatBoostConsumable(1,'TONG',True),
    spitable=consumable.ClingyConsumable(),
    rarity='r',
    stat='TONG',
    flavor="This orb of fluff coos appreciation at the slightest acknowledgement."
)


c_segments = [
    #volatile, forceful, drilling, prolific, acidic, petrified, ghostly, cursed, calcified, wrinkled, musclebound, annoying, backward, pure, growing, learned, longue, inquisitive, hungry, sensitive
    wrinkled
]
consonants = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','z']
