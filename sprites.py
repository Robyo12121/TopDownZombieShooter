import pygame as pg
from settings import *
from itertools import chain
from tilemap import collide_hit_rect, reconstruct_path #a_star_search, dijkstra_search, 
vec = pg.math.Vector2
from random  import uniform, choice, randint, random
import pytweening as tween
import Path_finding
import copy
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
    if direction == 'x': #checking for an x axis collision
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

class Gun(object):
    def __init__(self, gun_str):
        self.data = WEAPONS[gun_str]
        self.name = self.data['name']
        #self.remaining_shots = self.data['capacity']
        self.remaining_shots = 0

    def shoot(self):
        if self.remaining_shots <= 0:
            self.remaining_shots = 0
        else:
            self.remaining_shots -= 1

    def can_reload(self):
        if self.remaining_shots < self.data['capacity']:
            return True
        else:
            return False
        
    def space(self):
        return self.data['capacity']-self.remaining_shots
        
    def reload(self, amount):
        if not self.can_reload():
            print("Full")
            return
        elif amount > self.data['capacity'] - self.remaining_shots:
            print("That's too much!")
        else:
            print("Reloading: ",amount)
            self.remaining_shots += amount
        

class Player(pg.sprite.Sprite):
    #Note passing the sprite a copy of the game.
    #  This player constructor is called in game class
    def __init__(self, game, x, y): # x and y are grid coords not pixels
        self._layer = PLAYER_LAYER #Must be called before sprite.Sprite.__init__()
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.current_image = 'stand'
        self.image = game.player_imgs[self.current_image]
        #self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center # Center of hit box always same as image rect
        self.vel = vec(0,0)
        self.pos = vec(x,y)
        self.grid_pos = (self.pos.x // TILESIZE, self.pos.y // TILESIZE)      
        self.rot = 0
        self.rot_speed = 0
        # STATS
        self.damaged = False
        self.fatigue = PLAYER_FATIGUE        
        self.health = PLAYER_HEALTH
        self.infected = False
        self.last_drop = 0 #for dropping health every few seconds due to infection
        # INFO
        self.last_shot = 0
        self.facing = 0
        # INVENTORY
        #self.weapon = WEAPONS['pistol']
        self.weapon = None # MUST Be a Gun object
        self.reloading = False
        #self.items = ['pistol']
        self.items = {'weapons': {},
                      'ammo': {}}  

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        mouse_keys = pg.mouse.get_pressed()
        # MOVEMENT
        ## Turning
        if (keys[pg.K_LEFT] or keys[pg.K_a]):
            self.vel = vec(PLAYER_WALK_SPEED, 0).rotate(self.rot-90)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel = vec(PLAYER_WALK_SPEED, 0).rotate(self.rot+90)
        ## Moving
        if keys[pg.K_UP] or keys[pg.K_w]:
            # Sprinting
            if keys[pg.K_LSHIFT]:
                # Have fatigue
                if self.fatigue > 0:
                    self.vel = vec(PLAYER_SPRINT_SPEED, 0).rotate(-self.rot)
                    self.fatigue -= PLAYER_FATIGUE_RATE
                # No fatigue
                else:
                    self.vel = vec(PLAYER_NORMAL_SPEED, 0).rotate(-self.rot)
            # Walking (stealthing)
            elif keys[pg.K_LCTRL]:
                self.vel = vec(PLAYER_WALK_SPEED, 0).rotate(-self.rot)
                self.fatigue += PLAYER_FATIGUE_REGEN_WALKING
            # Jogging (normal)
            else:
                self.vel = vec(PLAYER_NORMAL_SPEED, 0).rotate(-self.rot)
                self.fatigue += PLAYER_FATIGUE_REGEN_NORMAL
        # Stationary
        if not keys[pg.K_UP] or keys[pg.K_w]:
            self.fatigue += PLAYER_FATIGUE_REGEN_STATIONARY
        # Walking backwards
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_WALK_SPEED, 0).rotate(-self.rot)

    def shoot(self):
        if not self.weapon:
            return
        else:
            now = pg.time.get_ticks()
            if now - self.last_shot > self.weapon.data['rate'] and self.weapon.remaining_shots > 0: 
                choice(self.game.weapon_sounds[self.weapon.data['name']]).play()
                self.last_shot = now
                direction = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                self.vel = vec(-self.weapon.data['recoil'], 0).rotate(-self.rot) 
                for i in range(self.weapon.data['bullet_count']): 
                    spread = uniform(-self.weapon.data['spread'], self.weapon.data['spread']) 
                    Bullet(self.game, pos, direction.rotate(spread), self.weapon.data['damage']) 
                    sound = choice(self.game.weapon_sounds[self.weapon.data['name']])
                    if sound.get_num_channels() > 2: # prevent too many overlapping sounds
                        sound.stop()
                    sound.play()
                MuzzleSmoke(self.game, pos)
                self.weapon.shoot()
                print(self.weapon.remaining_shots)

    def reload(self):
        """"""
        # Got a weapon to reload?
        if not self.weapon:
            print("no weapon equipped")
            return
        # Got space in mag to reload?
        if not self.weapon.can_reload():
            print("weapon full")
            return
        # Got ammo in inventory with which to reload it?
        if self.items['ammo'][self.weapon.name] <= 0:
            print("No ammo for this")
            return
        if self.items['ammo'][self.weapon.name] >= self.weapon.space():
            self.items['ammo'][self.weapon.name] -= self.weapon.space()
            self.weapon.reload(self.weapon.space())
        elif self.items['ammo'][self.weapon.name] < self.weapon.space():
            self.weapon.reload(self.items['ammo'][self.weapon.name])
            self.items['ammo'][self.weapon.name] = 0
        self.game.effects_sounds['gun_pickup'].play()
          
        print("Inventory ammo: {}".format(self.items['ammo'][self.weapon.name]))
        print("Ammo in gun: {}".format(self.weapon.remaining_shots))      
            
    def pickup(self, weapon):
        print("{} found".format(weapon))
        # Change sprite image
        if not self.current_image == 'gun':
            self.current_image = 'gun'
        self.game.effects_sounds['gun_pickup'].play()

        # New weapon in inventory?
        if weapon in self.items['weapons']: # Picked up weapon already there?
            print("Weapon in inventory already")
            # Just take the ammo
            self.add_ammo(weapon)
        else: # New weapon not in inventory
            if self.weapon is not None: # Already holding a weapon
                # Put current weapon away
                print("Putting current weapon away")
                self.items['weapons'][self.weapon.name] = self.weapon # Put that weapon in inv
            # Add it to inventory and equip it
            print("Don't have that weapon")
            self.items['weapons'][weapon] = Gun(weapon)
            self.weapon = self.items['weapons'][weapon]
            self.add_ammo(weapon)
            
    def add_ammo(self, weapon):
        if weapon in self.items['ammo']: # Already have some of that ammo?
            print("Have some of that ammo already")
            # Add more ammo
            self.items['ammo'][weapon] += WEAPONS[weapon]['capacity']
        else: # Don't already have some of that ammo
            print("New ammo type")
            # Add a mag's worth to inventory
            self.items['ammo'][weapon] = WEAPONS[weapon]['capacity']
            
    def cycle_weapon(self):
        print("Inventory: {}".format(self.items['weapons'].keys()))
        if self.weapon == None:
            return
        for name, obj in self.items['weapons'].items():
            if self.weapon.name != name:
                self.weapon = obj
                self.game.effects_sounds['gun_pickup'].play()
                return

    def print_inventory(self):
        print("\nInventory")
        print("\nHands: ")
        if self.weapon is None:
            pass
        else:
            print(self.weapon.name, self.weapon.remaining_shots)
        print("\nWeapons:")
        for weapon in self.items['weapons'].keys():
            print(weapon)
        print("\nAmmo:")
        for gun_type, amount in self.items['ammo'].items():
            print("{} : {}".format(gun_type, amount))

    def look_cursor(self):
        # Player face cursor pos
        cursor_pos = pg.mouse.get_pos()
        abs_cursor_pos = (cursor_pos[0] - self.game.camera.camera.x, cursor_pos[1] - self.game.camera.camera.y)
        cursor_dist = vec(abs_cursor_pos) - self.pos
        self.rot = cursor_dist.angle_to(vec(1,0))
            
    def got_hit(self):
        self.damaged = True
        self.health -= MOB_DAMAGE
        self.damage_alpha = chain(DAMAGE_ALPHA *2) #Flashing damage - happens twice
        if self.health < 0.6 * PLAYER_HEALTH and random() < PLAYER_INFECTION_CHANCE: #random() between 0.0 and 1.0
            self.infected = True            
        
    def update(self):
        self.get_keys() #uses pg.key.get_pressed()
        if self.fatigue > PLAYER_FATIGUE:
            self.fatigue = PLAYER_FATIGUE
        elif self.fatigue < 0:
            self.fatigue = 0
        self.look_cursor()
        self.image = pg.transform.rotate(self.game.player_imgs[self.current_image], self.rot)
        if self.damaged:
            try:
                self.image.fill((255,0,0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.grid_pos = (self.pos.x // TILESIZE, self.pos.y // TILESIZE)  
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls,'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls,'y')
        self.rect.center = self.hit_rect.center

        if self.infected:
            print("INFECTED. HEALTH: {}".format(self.health))
            now = pg.time.get_ticks()
            if now - self.last_drop > PLAYER_INFECTION_INTERVAL:
                self.last_drop = now
                self.health -= PLAYER_INFECTION_AMOUNT
                
        if self.health/PLAYER_HEALTH <= 0.6:
            if random() < 0.002:
                choice(self.game.player_pain_sounds).play()
        if self.health/PLAYER_HEALTH <= 0.3:
            if random() < 0.001:
                choice(self.game.player_panic_sounds).play()
        if self.health <= 0:
            self.game.playing = False

    def add_health(self, amount):
        self.infected = False
        self.health += amount
        if self.health >= PLAYER_HEALTH:
            self.health = PLAYER_HEALTH


       
class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = MOB_HIT_RECT.copy() #more than one mob
        self.hit_rect.center = self.rect.center
        self.pos = vec(x,y)
        self.grid_pos = (self.pos.x // TILESIZE, self.pos.y // TILESIZE)
        self.vel = vec(0,0)
        self.acc = vec(0,0) #Acceleration to delay movement speed
        self.rect.center = self.pos
        self.rot = uniform(0,360)
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.health = MOB_HEALTH
        self.speed = choice(MOB_WANDER_SPEEDS)
        self.detect_radius = MOB_DETECT_BASE
        self.target = None
        self.alerted = False
        self.last_hit = 0
        self.current_target = None
        self.last_path_update = 0
        self.first = False
        self.last_known = None
        self.last_known_grid = None
        self.path = None

        self.SM = AI.State_Machine(self)

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos #away from other mob
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def seek(self, target):
        """Given a target, return a seek vector to face it
        at a given speed"""
        self.desired = (target - self.pos).normalize() * self.speed
        steer = (self.desired - self.vel)
        if steer.length() > MOB_SEEK_FORCE:
            steer.scale_to_length(MOB_SEEK_FORCE)
        return steer

##    def follow_path(self, path, current_target):
##        """Sets target to first item in path and once sprite reaches it change to the
##            next target"""
##        if path == None:
##            return self.game.player.pos
##        if self.grid_pos == current_target:
##            index = path.index(current_target)
##            try:
##                self.target = path[index + 1]
##            except IndexError:
##                return self.game.player.pos
##            print("Changing target: {}".format(self.target))
##            return self.target
##        else:
##            print("Keeping target: {}".format(current_target))
##            return current_target

##    def move_set_path(self):
##        """move along a preset series of grid squares"""
##        if self.grid_pos == self.path[
##        pass

    def move(self, target):
        """Accepts target in vector form?"""
        #target = vec2int(target)
        if target == None:
            return
        target = vec(target)
        target_dist = target - self.pos
        #Mob rotation
        self.rot = target_dist.angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # Mob movement
        #self.acc = vec(1, 0).rotate(-self.rot)
        #self.acc = self.seek(self.path_to_player(next))
        #self.acc = self.seek(self.game.player.pos)
        self.acc = self.seek(target)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        # Equation of motion Pos = Vt + 0.5*Acc + (t^2) ?
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.grid_pos = (self.pos.x // TILESIZE, self.pos.y // TILESIZE)
        # Mob collisions
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

##    def pathfind_a_star(self):
##        now = pg.time.get_ticks()
##        self.start = vec(self.grid_pos)
##        self.goal = vec(self.game.player.grid_pos)
##        print("Start: {}, Goal: {}".format(self.start, self.goal))
##        
##        if now - self.last_path_update > MOB_PATH_UPDATE:
##            print(now-self.last_path_update)
##            print("Updating search")
##            print("Z: {}, P: {}".format(self.start, self.goal))
##            path,cost = a_star_search(self.game.map, self.start, self.goal)
##            #self.draw_path(path,self.start, self.goal)
##            self.path = reconstruct_path(path, self.start, self.goal)
##            self.last_path_update = now
##            self.target = vec2int(self.path[0])
##
##        self.target = self.follow_path(self.path, self.target)
##        self.move(self.target)

####    def bfs_map_follow(self):
####        path = self.game.map.reconstruct_path(

    def update_radius(self, tgt_vel):
        """Calculate detect radius based on player speed"""
        if self.alerted == True:
            self.detect_radius = MOB_LOSE_DETECT    
        else:
            self.detect_radius = MOB_DETECT_BASE + int(tgt_vel.length() * MOB_DETECT_MOD)
       
    def update(self):
        # Things to do every frame
        self.SM.update()
        player_dist = self.game.player.pos - self.pos
        self.update_radius(self.game.player.vel)
        # Alerted
        if player_dist.length_squared() < self.detect_radius**2:
            self.alerted = True
           #choice(self.game.zombie_moan_sounds
        else:
            self.alerted = False

        if self.alerted: # Mob chasing player
            self.speed = choice(MOB_SPRINT_SPEEDS)
            self.first = True
            self.move(self.game.player.pos)
        else: # Mob lost player
            if self.first:
                self.last_known = vec2int(self.game.player.pos)
                self.first = False
            if self.last_known is not None:
                last_known_dist = self.pos - vec(self.last_known)
                if last_known_dist.length_squared() > 1000: # 1000 just a number that leaves mob close to but not exactly on last known pos of player
                    self.move(self.last_known)
                else:
                    # function or code to make mob wander around
                    self.speed = choice(MOB_WANDER_SPEEDS)
                    
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32,32))
        self.draw_health()

    def draw_health(self):
        if self.health < MOB_HEALTH:
            if self.health > 60:
                col = GREEN
            elif self.health > 30:
                col = YELLOW
            else:
                col = RED
            width = int(self.rect.width * self.health /MOB_HEALTH)
            self.health_bar = pg.Rect(0,0, width, 7)
            pg.draw.rect(self.image, col, self.health_bar)


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


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, direction, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[self.game.player.weapon.data['bullet_size']] # WEAPONS[self.game.player.weapon]--->['bullet_size']
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos) # Make new vector from passed vector
        self.rect.center = pos
        #spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = direction * self.game.player.weapon.data['bullet_speed'] * uniform(0.9, 1.1) # --->['bullet_speed']
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > self.game.player.weapon.data['bullet_lifetime']: #---->['bullet_lifetime']
            self.kill()


class MuzzleSmoke(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(5,20)
        self.image = pg.transform.scale(choice(game.gun_smoke), (size, size))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > SMOKE_DURATION:
            self.kill()


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
