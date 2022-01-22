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

 Move next to an enemy (any number) to constrict that enemy.


$Suffocation$

 Beware of becoming completely surrounded! Even if the
 surrounding tiles comprise your own tail, this will kill you
 instantly.
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

 Move your head into a tile adjacent to an enemy to ^constrict^ it.
 Only your movement causes constriction, not enemies'.

 A constricted enemy can't move or act, and its health is reduced
 for the duration of the constriction.

 An enemy remains constricted while any part of you remains
 adjacent to that enemy.


$Health Reduction$

 Constriction reduces enemy  .....  Once an enemy's health  .....
 health by the number of     .....  is brought below zero,  .....
 tiles you occupy adjacent   .....  it dies.                .....
 to the enemy.               .....                          .....    
                             .....                          .....
""",[
  color.black
])
##################################################################
#d=36 (131)

constriction_anim_1_frames = [
("""
.....
.....
^@^.^2^..
^b^....
^at^...
""",[color.player,color.ogre,color.player,color.player]),
("""
.....
.....
^b@^^1^..
^a^....
^t^....
""",[color.player,color.black,color.player,color.player]),
("""
.....
.^@^...
^ab^^0^..
^t^....
.....
""",[color.player,color.player,color.black,color.player]),
("""
.^@^...
.^b^...
^ta^^0^..
.....
.....
""",[color.player,color.player,color.player,color.black]),
("""
.^b@^..
.^a^...
.^t^^0^..
.....
.....
""",[color.player,color.player,color.player,color.black]),
("""
.^ab@^.
.^t^...
..^1^..
.....
.....
""",[color.player,color.player,color.black]),
("""
.^tab@^
.....
..^2^..
.....
.....
""",[color.player,color.ogre]),
("""
.^tab@^
.....
..^2^..
.....
.....
""",[color.player,color.ogre])
]

constriction_anim_2_frames = [
("""
.....
.....
^@^.^7^.^k^
^b^...^s^
^asili^
""",[color.player,color.elder,color.player,color.player,color.player,color.player]),
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
""",[color.player,color.player,color.dark_red,color.player,color.player]),
("""
.....
.^ili^.
^ks^^.^^s^.
.^@ba^.
.....
""",[color.player,color.player,color.dark_red,color.player,color.player])
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
 in WORD MODE. While you're in WORD MODE, your identified non-
 vowel items boost your stats.

 Press $o$ then type a word to see if it's in our dictionary.
""",[color.vowel] + random_item_colors)
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
