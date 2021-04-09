import random
import entity_factories
from entity import Item
import numpy

letters = {
	'b':2,
	'c':2,
	'd':4,
	'f':2,
	'g':3,
	'h':2,
	'j':1,
	'k':1,
	'l':4,
	'm':2,
	'n':6,
	'p':2,
	'q':1,
	'r':6,
	's':4,
	't':6,
	'v':2,
	'w':2,
	'x':1,
	'z':1
}

letters_weighted = []
for k,v in letters.items():
	letters_weighted += [k]*v

letters_weighted.sort(key=lambda l: letters[l])
mean = sum([v for v in letters.values()])/len(letters)
median = int(round(len(letters_weighted)/2))

"""print(f"med: {letters_weighted[median]}")
print(mean)
print(letters_weighted)"""

c_segments22 = []

for c in entity_factories.c_segments2:
	c_segments22.append(Item(
		item_type='c',
		color=c._color,
		name=c.name+'2',
		edible=c.edible,
		spitable=c.spitable,
		rarity=c.rarity
	))

item_fs = entity_factories.c_segments[:] + c_segments22
item_fs.sort(key=lambda i:{'c':0,'u':1,'r':2}[i.rarity])

"""for item in item_fs:
	print(f"{item.name} ({item.rarity})")"""
letters_weighted_ = letters_weighted

def assign_items():
	all_items = []
	letters_weighted = letters_weighted_[:]
	letters_weighted.sort(key=lambda l:letters[l]+random.random())

	# assign letters to items + print list
	while len(letters_weighted) > 0:
		item_fs = entity_factories.c_segments[:] + c_segments22
		random.shuffle(item_fs)
		for i in item_fs:
			letters_weighted_thirds = numpy.array_split(letters_weighted,3)
			third = letters_weighted_thirds[{'r':0,'u':1,'c':2}[i.rarity]]
			
			char = random.choice(third) if len(third) > 0 else random.choice(letters_weighted)

			item = Item(
			    item_type='c',
			    color=i._color,
			    name=i.name,
			    edible=i.edible,
			    spitable=i.spitable,
			    rarity=i.rarity
			)
			item.char = char
			all_items.append(item)
			letters_weighted = [l for l in letters_weighted if l != item.char]

			if len(letters_weighted) == 0:
				break

	all_items.sort(key=lambda i: letters[i.char])
	return all_items

"""for i in all_items:
	print(f"{i.char} - {i.name} ({i.rarity})")"""

letter_cols = [l for l in letters]
letter_cols.sort(key=lambda l:letters[l])


tallies = {i.name:{'rarity':i.rarity,'chars':{c:0 for c in letter_cols}} for i in item_fs}
space_1 = max([len(t) for t in tallies])
space_2 = 3


"""
for i in range(1000):
	items = assign_items()
	for item in items:
		tallies[item.name]['chars'][item.char] += 1



print(' '*space_1 + ' '*space_2 + '   '.join(l for l in letter_cols))

for name,tally in tallies.items():
	space_a = space_1 - len(name)
	char_counts = []
	for c in tally['chars'].values():
		space = 3 - len(str(c))
		char_counts.append(str(c)+' '*space)

	print(name + ' '*space_a + ' ' + tally['rarity'] + ' ' + ' '.join(char_counts))
"""

enemies = {'c':{'drops':[]},'u':{'drops':[]},'r':{'drops':[]}}

drops = assign_items()
drops.sort(key=lambda x: letters[x.char])

for i,e in enemies.items():
	for d in drops:
		fact = letters[d.char]
		additions = [d] * fact if d.rarity != i else [d] * (fact+2) * (fact+2)
		e['drops'] += additions


floors = [
	['c','c','c','c','u']*1,
	['c','c','c','u','u']*2,
	['c','c','c','u','u']*3,

	['c','c','u','u','r']*2,
	['c','c','u','u','r']*3,
	['c','u','u','u','r']*4,
	
	['c','u','u','u','r']*5,
	['u','u','u','r','r']*5,
	['u','u','r','r','r']*5
]

my_drops = []

for floor in floors:
	floor_drops = []
	for enemy in floor:
		floor_drops.append(random.choice(enemies[enemy]['drops']))
	my_drops.append(floor_drops)


space_2 = 6
print (' '*space_1 + ' '*space_2 + '   '.join(str(i) for i in range(9)))
for drop in drops:
	space_a = space_1 - len(drop.name)
	counts = []

	for floor in my_drops:
		count = str(len([d for d in floor if d == drop]))
		count += ' '*(3-len(count))
		counts.append(count)

	total = '= '+str(sum([int(c) for c in counts]))
	counts.append(total)

	print(drop.name + ' '*space_a + ' ' + drop.rarity + ' ' + drop.char + '  ' + ' '.join(counts))





