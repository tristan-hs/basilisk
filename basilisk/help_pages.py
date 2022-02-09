import basilisk.color as color
import random

# let's say 66 x 35, so here's a width ruler
# trim the first \n when printing
############################################################
# rewriting with wider panels, headers, and coloring

##################################################################
moving = ("""
...................  $Movement Controls$
.                 .
.                 .   Move with the vim keys (shown here) or the
.  $YKU   \\↑/$      .   num pad.
.  $H.L = ← →$      .
.  $BJN   /↓\\$      .   Press $.$ or $5$ to wait.
.                 .
.  $YU      \\/$     .   Press $>$ to use stairs.
.   $HJKL =  ←↓↑→$  .  
.  $BN      /\\$     .   Full mouse support is planned for a future
.                 .   version.
.                 .
...................


$The Map$

 You can move over any floor tile (.), snakestone tile (^~^), or
 stair tile (^>^). Enemies will not chase or attack you through
 snakestone.


$Movement Actions$

 Move onto an item (any letter) to pick it up. This adds it to the
 end of your tail.

 Move next to an enemy to constrict that enemy.

""",[(0,100,255),(200,0,200)])
##################################################################
#d=36 (44)
#colorize: (.), (~), (>)  (remove parens?)

##################################################################
enemies = ("""
$Appearance$                                       .................
                                                 .               .
 All numbers on the map represent hostile        .  ^0^^1^^1^^2^^3^^4^^5^^4^^7^^7^^8^  .
 creatures. The number is always equal to the    .               .
 creature's current health.                      .................

 $Click$ or use the $x$ cursor to inspect an enemy.


$Behaviour$

 An enemy that can see a clear path to you will move toward the
 closest part of you it can reach, erring for your head. It will 
 not attack or move toward anything in or beyond snakestone (^~^).


$Damage$

 Any damage to your head, from an enemy or otherwise, will kill
 you. Damage to your tail will destroy the damaged segment.

 Permanently damage an enemy by using certain items; temporarily 
 damage an enemy by constricting it. Reduce an enemy's health to
 below zero by either method to kill it. These two damage types 
 are cumulative.


$Enemies and WORD MODE$  ^1^^→→^

 While you're in WORD MODE, enemies decide where they will try to
 move before your turn. Red arrows indicate their intents.

 While you're not in WORD MODE, they decide what to do after your
 turn. A yellow aura indicates all tiles they could choose to move
 to.
""",[color.statue,color.goblin,color.jackelope,color.ogre,color.mongoose,color.dragon,color.lich,color.demon,color.war_god,color.elder,color.decider,(0,100,255),color.jackelope,color.red])
##################################################################
#d=36 (87)
#colorize: snakestone, arrows


##################################################################
constriction = ("""
$What is Constriction?$

 A ^constricted^ enemy can't move or attack.


 To constrict an enemy,      .....  Only your movement      .....
 move your head to an        .....  causes constriction,    .....
 adjacent tile.              ..4..  not enemies'.           ..5..
                             .....                          .....
                             .....                          .....


 An enemy remains constricted while any part of you is adjacent
 to it.


$Health Reduction$

 Constriction reduces an     .....  Once an enemy's health  .....
 enemy's health by the       .....  is brought below zero,  .....
 number of adjacent tiles    ..1..  it dies.                ..2..
 you occupy.                 .....                          .....
                             .....                          .....


 Constrict as many enemies   .....
 as you want!                .....
                             ..3..
                             .....
                             .....
""",[
  color.black
])
##################################################################
#d=36 (131)

constriction_anim_1_frames = [
("""
.....
.....
^@^^←^^2^..
^a^....
.....
""",[color.player,color.intent_bg,color.ogre,color.player]),
("""
.....
.....
^a@^^1^..
.....
.....
""",[color.player,color.black]),
("""
.....
..^@^..
.^a^^0^..
.....
.....
""",[color.player,color.player,color.black]),
("""
.....
..^a^..
..^0^^@^.
.....
.....
""",[color.player,color.black,color.player]),
("""
.....
.....
..^0^^a^.
..^@^..
.....
""",[color.black,color.player,color.player]),
("""
.....
.....
..^0^..
.^@a^..
.....
""",[color.black,color.player]),
("""
.....
.....
..^1^..
^@a^...
.....
""",[color.black,color.player])
]

constriction_anim_2_frames = [
("""
.....
.....
^@^^←^^7^.^k^
^b^...^s^
^asili^
""",[color.player,color.intent_bg,color.elder,color.player,color.player,color.player,color.player]),
("""
.....
.....
^b@^^6^..
^a^...^k^
^silis^
""",[color.player,color.black,color.player,color.player,color.player]),
("""
.....
.^@^..
^ab^^5^..
^s^....
^ilisk^
""",[color.player,color.player,color.black,color.player,color.player]),
("""
.....
.^b@^..
^sa^^4^..
^i^....
^lisk^.
""",[color.player,color.player,color.black,color.player,color.player]),
("""
.....
.^ab@^.
^is^^3^..
^l^....
^isk^..
""",[color.player,color.player,color.black,color.player,color.player]),
("""
.....
.^sab^.
^li^^2^^@^.
^i^....
^sk^...
""",[color.player,color.player,color.black,color.player,color.player,color.player]),
("""
.....
.^isa^.
^il^^1^^b^.
^s^..^@^.
^k^....
""",[color.player,color.player,color.black,color.player,color.player,color.player,color.player]),
("""
.....
.^lis^.
^si^^0^^a^.
^k^.^@b^.
.....
""",[color.player,color.player,color.black,color.player,color.player,color.player]),
("""
.....
.^ili^.
^ks^^.^^s^.
.^@ba^.
.....
""",[color.player,color.player,color.dark_red,color.player,color.player])
]

constriction_anim_3_frames = [
("""
^1^....
.^\\^^2^^←^^2^
^@^....
^b^.^7^^←^^7^
^at^...
""",[color.goblin,color.intent_bg,color.ogre,color.intent_bg,color.ogre,color.player,color.player,color.elder,color.intent_bg,color.elder,color.player]),
("""
^1^....
.^\\^^1^^←^^2^
^b@^...
^a^.^6^^←^^7^
^t^....
""",[color.goblin,color.intent_bg,color.black,color.intent_bg,color.ogre,color.player,color.player,color.black,color.intent_bg,color.elder,color.player]),
("""
.....
.^1^^1^^←^^2^
^b@^...
^a^.^6^^←^^7^
^t^....
""",[color.goblin,color.black,color.intent_bg,color.ogre,color.player,color.player,color.black,color.intent_bg,color.elder,color.player]),
("""
.....
.^1^^1^^2^.
^b@^^/^..
^a^.^6^^←^^7^
^t^....
""",[color.goblin,color.black,color.ogre,color.player,color.intent_bg,color.player,color.black,color.intent_bg,color.elder,color.player]),
("""
.....
.^1^^1^^2^.
^b@^^/^..
^a^.^6^^7^.
^t^....
""",[color.goblin,color.black,color.ogre,color.player,color.intent_bg,color.player,color.black,color.elder,color.player]),
("""
.....
.^.^^01^.
^ab@^..
^t^.^56^.
.....
""",[color.dark_red,color.black,color.player,color.player,color.black]),
("""
.....
.^..^^0^.
^tab@^.
..^45^.
.....
""",[color.dark_red,color.black,color.player,color.black]),
("""
.....
.^...^^@^
.^tab^.
..^45^.
.....
""",[color.dark_red,color.player,color.player,color.black]),
("""
...^@^.
.^...^^b^
..^ta^.
..^55^.
.....
""",[color.player,color.dark_red,color.player,color.player,color.black]),
("""
..^@b^.
.^...^^a^
...^t^.
..^66^.
.....
""",[color.player,color.dark_red,color.player,color.player,color.black]),
("""
..^ba^.
.^.^^@^^.^^t^
..^↑↑^.
..^77^.
.....
""",[color.player,color.dark_red,color.player,color.dark_red,color.player,color.intent_bg,color.elder]),
]

constriction_anim_4_frames = [
("""
.^a^...
^@^....
.^←^^1^..
.....
.....
""",[color.player,color.player,color.intent_bg,color.goblin]),
("""
.....
^a@^...
..^0^..
.....
.....
""",[color.player,color.black]),
("""
.^@^...
.^a^...
..^0^..
.....
.....
""",[color.player,color.player,color.black])
]

constriction_anim_5_frames = [
("""
.....
^@^....
^↑←^^1^..
^1^....
.....
""",[color.player,color.intent_bg,color.goblin,color.goblin]),
("""
.....
.^@^...
^↑^.^0^..
^1^....
.....
""",[color.player,color.intent_bg,color.black,color.goblin]),
("""
.....
.^@^...
^1^.^0^..
.....
.....
""",[color.player,color.goblin,color.black]),
("""
.....
.^/^^@^..
^1^.^0^..
.....
.....
""",[color.intent_bg,color.player,color.goblin,color.black]),
("""
.....
.^1^^@^..
..^0^..
.....
.....
""",[color.goblin,color.player,color.black]),
("""
.....
.^0^...
.^@^^0^..
.....
.....
""",[color.black,color.player,color.black])
]


##################################################################
random_item_colors = [random.choice([color.bile,color.mind,color.tongue,color.tail,color.offwhite]) for i in range(21)]
items = ("""
............  $Appearance$
.          .
.          .   Any letter on the map is an item.
.  ^aeiouy^  .
.  ^b^^c^^d^^f^^g^^h^  .
.  ^j^^k^^l^^m^^n^^p^  .  $Item Actions$
.  ^q^^r^^s^^t^^v^^w^  .
.  ^x^^y^^z^     .   Move over an item to pick it up and add it to the
.          .   end of your tail. Press $s$ to choose an item to spit
............   or $d$ to choose an item to digest. This will usually
               consume the selected item.

 Press $i$ to open the inventory. Highlight an item to see a
 description of what it does when spit, digested, or equipped as
 part of a word. Press $s$ or $d$ to spit or digest the selected item.

 If an item on your tail breaks, subsequent items are dropped.


$Identification$

 Identify a letter by spitting, digesting, or destroying it. Press
 $p$ to review which letter holds which item this run and which 
 items you have yet to identify.


$Items and WORD MODE$

 If your tail in order spells out a word in our dictionary, you're
 in ^WORD MODE^. While you're in ^WORD MODE^, your identified non-
 vowel items boost your stats.

 Press $o$ then type a word to see if it's in our dictionary.
""",[color.vowel] + random_item_colors + [color.snake_green,color.snake_green])
##################################################################
#d=36 (173)

##################################################################
stats = ("""
$Stats$

 Some items boost your stats when digested. If the boost is 
 temporary, its duration will be shown next to the affected stat. 


^BILE^  Each point adds +1 to damage done by items.

^MIND^  Each point increases the duration or potency of non-damaging
      item effects.

^TONG^  Each point adds +1 to your vision radius and +2 to your
      smell radius.

      Smell radius determines your ability to detect and identify 
      enemies through walls. Default smell radius is 0.

^TAIL^  Each point adds +1 to the total constriction damage you deal
      to each enemy.


$Status Effects$

 ^SALIVA^.n  The next n times you spit an item, it won't be consumed

^PETRIFY^.n  All enemies you see turn to stone for n turns

  ^PHASE^.n  You can move through n wall tiles

 SHIELD.n  The next n times you take damage it has no effect

  ^CHOKE^.n  You can't spit for n turns

  ^DAZE^..n  You can't see enemy intents for n turns
""",[color.bile,color.mind,color.tongue,color.tail,color.snake_green,color.cyan,color.purple,color.tongue,color.red])
##################################################################
#d=36 (214)
#colorize: stats, statuses, n?

##################################################################
other = ("""
$Miscellaneous Tips$

- Beware when the floor is ^blue^ and the walls are narrow. Yes,
  treasures beyond your wildest dreams await, but at what cost?

- Digesting-to-identify is often worth the risk. You didn't get
  where you are by being a choosy eater.

- $Click$ a tile or press $x$ to learn more about your surroundings.


$Why Am I Here?$

 Have you forgotten already, brave ^serpent^?

 The world is solidifying. You can see it in the segments of your
 own tail -- give any a-one too much attention and it will
 manifest permanence, granting new definition to the world.
 Disgusting.

 You've come to put an end to all that inane stratification.

 Again you've found its source here where the flux is weakest; 
 where rules reign, though the floor still shifts and squirms as 
 it ought. In your belly you can feel the awful eminations of 
 stifling reality welling up from the earth. The will of the ^One 
 Below^.

 And you've accepted, though it pains you, that you must use the
 tools of your enemy to succeed. No random assemblage will find
 purchase on this purveyor of perpetuity. Proceed with purpose and
 become the word that will bring chaos everlasting!

 May that word be ^Basilisk^!
""",[(0,0,150),color.player,color.purple,color.player])
##################################################################
#d=36 (256)
#colorize: serpent, One Below, blue, Basilisk

tutorial_messages = {

  'new game':
################################################
("""
$Welcome to Basilisk!$

That ^@^ is you. Move with the num pad or the 
vim keys (shown in the bottom left).

Hit $?$ for more information.

You can disable these tips from the in-game menu
($ESC$).
""",[color.player]),

  'pick up': 
################################################
("""
$You've picked up an item!$

It's been added to the end of your tail. See how
it follows you around the dungeon.

Your tail is shown in order in the panel on the
right.

Press $i$ and scroll up and down for more infor-
mation on the items in your tail.

From inside or outside that menu, press $d$ or $s$ 
to digest or spit an item.
""",[]),

  'word mode 2':
################################################
("""
^You're back in WORD MODE!^

This happens when your tail spells out a word. 

Press $o$ at any time to look up a word.

While in ^WORD MODE^, you can see where your
enemies intend to move (^→^) and your identified
consonants boost your stats.

Press $?$ for more information on word mode,
stats, and enemy behavior.
""",[color.snake_green,color.snake_green,color.red]),
  
  'enemy':
################################################
("""
$You spotted an enemy!$

Once it can see a clear path to you, it will
chase you down.

Fortunately, you can constrict and paralyze it
by moving your head into an adjacent tile.
""",[]),
    
  'constrict':
################################################
("""
$You're constricting an enemy!$

While constricted, it can't move or act.

The more completely you encircle it, the lower
its health will go. But if you release it before
killing it, it will recover.

It will only die if its health is brought $below$
zero.

Press $?$ for more information on constriction.
""",[]),

  'consonant': 
################################################
("""
$You've picked up a consonant!$

You can $d$igest it or $s$pit it to find out what
this letter does. Do so at your own risk.

Your com$p$endium will track which items you've
identified this run and which items you've en-
countered across all your runs.

Press $?$ for more information on items.
""",[]),
  
  'stairs': 
################################################
("""
$You've found stairs!$

With your head on that tile, press $>$ to descend
to the next level.
""",[]),

  'snakestone':
################################################
("""
$You've just entered snakestone!$

Enemies can't attack you while you're in it or
follow you through it. Use it wisely.
""",[]),

  'new game 2':
################################################
("""
$Welcome back to the dungeon!$

Yes, back to the very beginning.

You'll notice that your com$p$endium still knows
about the consonants you found in your past
lives. It just doesn't know what they look like
in this one yet.
""",[]),

    'stat boost':
################################################
("""
$One of your stats is buffed!$

In the bottom right panel, each colored-in 
letter represents 1 point in its stat.

If the buff is temporary, you'll see the number 
of turns remaining to the right of the stat.

Press $?$ for more info on stats and status
effects.
""",[]),
    
  '100 turns':
################################################
("""
Have you tried using your $mouse$ or the
e$x$amination cursor to look around?

You can $click$ or press an index key (shown in 
the bottom left) for more information on what-
ever's in the highlighted tile.
""",[])
}
