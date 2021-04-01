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
    color=(127,127,127),
    name="Statue",
    ai_cls=ai.Statue,
    fighter=Fighter(hp=1, defense=0, power=0),
)

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