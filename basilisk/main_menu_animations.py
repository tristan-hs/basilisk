import basilisk.color as color
import random

y = random.choice([15,45,45,45,45,45,45,45,45,45])
if y == 15:
	x = random.choice(range(56,58))
else:
	x = random.choice(range(0,63))

class Animation():
	default_x=x
	default_y=y
	def __init__(self,x=0,y=0,frames=None):
		self.x = self.default_x+x
		self.y = self.default_y+y
		self.frames = frames

	def print(self,console,kf):
		for layer in self.frames[kf]:
			console.print(self.x,self.y,layer.content,fg=layer.color)

class Layer():
	def __init__(self,content,color):
		self.content = content
		self.color = color


# DEFAULT ANIMATION =========

default_animation = Animation(frames=[

# Frame 1
(
Layer("""
 @b
  a
 s
ilisk
""",color.player),
)

])

# STICK OUT TONGUE ==========

stick_out_tongue = Animation(frames=[
(
Layer("""
 @b
  a
 s
ilisk
""",color.player),
Layer("""
~
""",color.tongue)
),

(
Layer("""
 @b
  a
 s
ilisk
""",color.player),
),

(
Layer("""
 @b
  a
 s
ilisk
""",color.player),
Layer("""
~
""",color.tongue)
),
(
Layer("""
 @b
  a
 s
ilisk
""",color.player),
Layer("""
~
""",color.tongue)
),
])

# FLICK TAIL =================

flick_tail = Animation(frames=[
(
Layer("""
 @b
  a
 s   ,
ilisk
""",color.player),
),

(
Layer("""
 @b
  a
 s  ;
ilisk
""",color.player),
),
]*3)

# CRAWL AROUND ================

crawl_around = Animation(frames=[
(
Layer("""
 ba
 @s
 i
lisk
""",color.player),
),

(Layer("""
 as
 bi
 l@
isk
""",color.player),),

(Layer("""
 si
 al
 ib
sk @
""",color.player),),


(Layer("""
 il
 si
 sa
k @b
""",color.player),),

(Layer("""
 li
 is
 ks
 @ba
""",color.player),),

(Layer("""
 is
 lk
  i
@bas
""",color.player),),

(Layer("""
 sk
 i
 @l
basi
""",color.player),),

(Layer("""
 k
 s@
 bi
asil
""",color.player),),

(Layer("""
  @
 kb
 as
sili
""",color.player),),

(Layer("""
 @b
  a
 sk
ilis
""",color.player),),
(Layer("""
 @b
  a
 sk
ilis
""",color.player),),
(Layer("""
 @b
  a
 sk
ilis
""",color.player),),
(Layer("""
 @b
  a
 sk
ilis
""",color.player),),

(
Layer("""
 @b
  a
 sk
ilis
""",color.player),
Layer("""
~
""",color.tongue)
),

(Layer("""
 @b
  a
 sk
ilis
""",color.player),),
(Layer("""
 @b
  a
 sk
ilis
""",color.player),),
(Layer("""
 @b
  a
 sk
ilis
""",color.player),),

(Layer("""
  b
  @
 sk
ilis
""",color.player),),
(Layer("""
  b
  a@
 s k
ilis
""",color.player),),
(Layer("""
  b
  a@
 s   ,
ilisk
""",color.player),),
(Layer("""
  b
  a@
 s
ilisk
""",color.player),),

(Layer("""
  b
  @
 s
ilisk
""",color.player),),

(Layer("""
 @b
  a
 s 
ilisk
""",color.player),),

])

# SPELL IT OUT ===============

spell_it_out = Animation(y=-1,frames=[

(Layer("""

 ba
 @s
 i
lisk
""",color.player),),

(Layer("""

 as
 bi
 l@
isk
""",color.player),),

(Layer("""

 si
 al
 ib
sk @
""",color.player),),

(Layer("""

 il
 si
 sa
k  b@
""",color.player),),

(Layer("""

 li
 is
 ks
   ab@
""",color.player),),

(Layer("""

 is
 lk
  i
   sab@
""",color.player),),

(Layer("""

 sk
 i
  l
   isab@
""",color.player),),
(Layer("""

 sk
 i
  l
   isab@
""",color.player),),
(Layer("""

 sk
 i
  l
   isab@
""",color.player),),

(Layer("""

 
 sk
 i
  lisab@
""",color.player),),

(Layer("""

 
 
 sk
 ilisab@
""",color.player),),
(Layer("""

 
 
 sk
 ilisab@
""",color.player),),
(Layer("""

 
 
 sk
 ilisab@
""",color.player),),

(Layer("""

 
 
 k
 silisab@
""",color.player),),
(Layer("""

 
 
 
 ksilis@b
""",color.player),),

(Layer("""

 
 
  
  ksil@ba
""",color.player),),


(Layer("""

 
 
  
   ks@bas
""",color.player),),


(Layer("""

 
 
  
    @basi
""",color.player),),


(Layer("""

 
 
  
   @basil
""",color.player),),

(Layer("""

 
 
  
  @basili
""",color.player),),

(Layer("""

 
 
  
 @basilis
""",color.player),),

(Layer("""
   
    
     
       
@basilisk
""",color.player),),
(Layer("""
   
    
     
       
@basilisk
""",color.player),),
(Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),
(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
 @     
basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
  @   
 b     
asilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
  @ 
  b   
 a     
silisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),
(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),
(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),

])

intro_animation = Animation(y=-1,frames=[
(Layer("""
 
 
 
  
        
""",color.player),),
(Layer("""
 
 
 
  
                
""",color.player),),
(Layer("""
 
 
 
  
               
""",color.player),),

(Layer("""
 
 
 
  
        @        
""",color.player),),
(Layer("""
 
 
 
  
        @        
""",color.player),),
(Layer("""
 
 
 
  
        @        
""",color.player),),
(Layer("""
 
 
 
  
        
""",color.player),),
(Layer("""
 
 
 
  
        
""",color.player),),
(Layer("""
 
 
 
  
        @        
""",color.player),),
(Layer("""
 
 
 
        @
        b        
""",color.player),),
(Layer("""
 
 
 
        b@
        a        
""",color.player),),
(Layer("""
 
 
 
        b@
        a        
""",color.player),),
(Layer("""
 
          
         @
        b
        a        
""",color.player),),
(Layer("""
 
          
         @
        b
        a        
""",color.player),),
(Layer("""
 
          
         
        b@
        a        
""",color.player),),
(Layer("""
 
          
         
        b@
        a        
""",color.player),),
(Layer("""
 
          
         
        b@
        a        
""",color.player),),
(Layer("""
 
          
         
        b@
        a        
""",color.player),),
(Layer("""
 
          
         
        @
        a        
""",color.player),),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(
Layer("""
 
          
         
       @b
        a        
""",color.player),
Layer("""



      ~
""",color.tongue)
),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(Layer("""
 
          
         
       @b
        a        
""",color.player),),
(Layer("""
 
          
         
        @
        b        
""",color.player),),
(Layer("""
 
          
         
       
        @        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),
(Layer("""
 
          
         
       
        
""",color.player),),


(Layer("""
 
 
 
  
        @        
""",color.player),),

(Layer("""
 
 
 
  
       @b        
""",color.player),),

(Layer("""
 
 
   
  
      @ba        
""",color.player),),

(Layer("""
 
 
   
   
     @bas        
""",color.player),),

(Layer("""
 
 
     
    
    @basi        
""",color.player),),

(Layer("""
 
 
     
      
   @basil        
""",color.player),),

(Layer("""
 
 
     
      
  @basili        
""",color.player),),

(Layer("""
 
 
     
       
 @basilis        
""",color.player),),

(Layer("""
   
    
     
       
@basilisk
""",color.player),),
(Layer("""
   
    
     
       
@basilisk
""",color.player),),
(Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),
(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
       
@basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
     
 @     
basilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
    
  @   
 b     
asilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
  @ 
  b   
 a     
silisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),

(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),
(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),
(Layer("""




          by -taq
""",color.purple),
Layer("""
   
 @b 
  a   
 s     
ilisk
""",color.player),),

])

animations = [
	stick_out_tongue,stick_out_tongue,stick_out_tongue,
	flick_tail,flick_tail,flick_tail,
	crawl_around,
	spell_it_out
]