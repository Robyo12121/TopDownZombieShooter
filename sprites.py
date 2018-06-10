import pygame as pg
from settings import *
from tilemap import collide_hit_rect, reconstruct_path #a_star_search, dijkstra_search, 
vec = pg.math.Vector2
from random  import uniform, choice
import pytweening as tween
import Path_finding
import AI


class BaseGameEntity():
    _nextID = 0
    def __init__(self):
        self.id = BaseGameEntity._nextID
        BaseGameEntity._nextID += 1
    def update(self):
        raise NotImplementedError

def vec2int(v):
    """Convert vector to tuple of ints as vectors not hashable"""
    return (int(v.x), int(v.y))

def collide_with_walls(sprite, group, direction):
    """for each axis detect collisions between player and walls"""
    if direction == 'x': #checking for an x is collision
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)#False as don't delete walls
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:         
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2 # move my x tile pos 1 tile to the left of the left edge of object we've hit
            if hits[0].rect.centerx < sprite.hit_rect.centerx:           
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2 #so move my x side up against the objects right side
            sprite.vel.x = 0                                               # and then stop moving in that direction
            sprite.hit_rect.centerx = sprite.pos.x                           #put my rectangle surface where my pos is
            
    if direction == 'y': # checking for y axis collision
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits: #if we collide with something
            if hits[0].rect.centery > sprite.hit_rect.centery: 
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2 # so move my y tile pos to 1 tile above it's top edge
            if hits[0].rect.centery < sprite.hit_rect.centery: 
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2# move my y tile pos to its bottom edge  
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Obstacle(pg.sprite.Sprite):
    """Invisble collidable object that sits on top of """
    def __init__(self, game, x, y, w, h):
        self._layer = WALL_LAYER
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x,y,w,h)
        self.x = x
        self.y = y
        self.rect.x = x 
        self.rect.y = y

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, item_type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[item_type]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hit_rect = self.rect
        self.type = item_type
        self.pos = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        #bobbing motion
        # Every frame calc how far along in tween func
        offset = BOB_RANGE * (self.tween(self.step/BOB_RANGE) - 0.5) #subtract half as we start in center
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1
