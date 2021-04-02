from components import ai
from components import consumable
from entity import Actor, Item
import color
from render_order import RenderOrder
 
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
)
titan = Actor(
    char="4",
    color=color.titan,
    name="Titan",
    ai_cls=ai.HostileEnemy,
)
lich = Actor(
    char="5",
    color=color.lich,
    name="Lich",
    ai_cls=ai.HostileEnemy,
)
demon = Actor(
    char="6",
    color=color.demon,
    name="Demon",
    ai_cls=ai.HostileEnemy,
)
war_god = Actor(
    char="7",
    color=color.war_god,
    name="War God",
    ai_cls=ai.HostileEnemy,
)
elder = Actor(
    char="8",
    color=color.elder,
    name="Elder",
    ai_cls=ai.HostileEnemy,
)
decider = Actor(
    char="9",
    color=color.decider,
    name="The Decider",
    ai_cls=ai.HostileEnemy,
)

enemies = [statue,goblin,ogre,dragon,titan,lich,demon,war_god,elder,decider]

vowel = Item(
    charset=('a','e','i','o','u'),
    color=color.vowel,
    name="Vowel",
    edible=consumable.ReversingConsumable(amount=10),
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