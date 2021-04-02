from components import ai
from components import consumable
from components.fighter import Fighter
from entity import Actor, Item
import color
from render_order import RenderOrder
 
player = Actor(
    char="@",
    color=color.player,
    name="Player",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    render_order=RenderOrder.PLAYER
)

statue = Actor(
    char="0",
    color=color.statue,
    name="Statue",
    ai_cls=ai.Statue,
    fighter=Fighter(hp=1, defense=0, power=0),
)
goblin = Actor(
    char="1",
    color=color.goblin,
    name="Goblin",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
ogre = Actor(
    char="2",
    color=color.ogre,
    name="Ogre",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
dragon = Actor(
    char="3",
    color=color.dragon,
    name="Dragon",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
titan = Actor(
    char="4",
    color=color.titan,
    name="Titan",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
lich = Actor(
    char="5",
    color=color.lich,
    name="Lich",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
demon = Actor(
    char="6",
    color=color.demon,
    name="Demon",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
war_god = Actor(
    char="7",
    color=color.war_god,
    name="War God",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
elder = Actor(
    char="8",
    color=color.elder,
    name="Elder",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)
decider = Actor(
    char="9",
    color=color.decider,
    name="The Decider",
    ai_cls=ai.HostileEnemy,
    fighter=Fighter(hp=1, defense=0, power=1)
)

enemies = [statue,goblin,ogre,dragon,titan,lich,demon,war_god,elder,decider]

vowel = Item(
    charset=('a','e','i','o','u'),
    color=(0,0,255),
    name="Vowel",
    edible=consumable.HealingConsumable(amount=10),
    spitable=consumable.Projectile(damage=1)
)


"""confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)
health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)"""