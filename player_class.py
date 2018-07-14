import pygame as pg
from sprites import BaseGameEntity, collide_with_walls
from settings import *
from random import choice, uniform, random, randint
from itertools import chain

vec = pg.math.Vector2

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
                if self.fatigue > 100:
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
                #print(self.weapon.remaining_shots)

    def reload(self):
        """"""
        # Got a weapon to reload?
        if not self.weapon:
            #print("no weapon equipped")
            return
        # Got space in mag to reload?
        if not self.weapon.can_reload():
            #print("weapon full")
            return
        # Got ammo in inventory with which to reload it?
        if self.items['ammo'][self.weapon.name] <= 0:
            #print("No ammo for this")
            return
        if self.items['ammo'][self.weapon.name] >= self.weapon.space():
            self.items['ammo'][self.weapon.name] -= self.weapon.space()
            self.weapon.reload(self.weapon.space())
        elif self.items['ammo'][self.weapon.name] < self.weapon.space():
            self.weapon.reload(self.items['ammo'][self.weapon.name])
            self.items['ammo'][self.weapon.name] = 0
        self.game.effects_sounds['gun_pickup'].play()
          
        #print("Inventory ammo: {}".format(self.items['ammo'][self.weapon.name]))
        #print("Ammo in gun: {}".format(self.weapon.remaining_shots))      
            
    def pickup(self, weapon):
        #print("{} found".format(weapon))
        # Change sprite image
        if not self.current_image == 'gun':
            self.current_image = 'gun'
        self.game.effects_sounds['gun_pickup'].play()

        # New weapon in inventory?
        if weapon in self.items['weapons']: # Picked up weapon already there?
            #print("Weapon in inventory already")
            # Just take the ammo
            self.add_ammo(weapon)
        else: # New weapon not in inventory
            if self.weapon is not None: # Already holding a weapon
                # Put current weapon away
                #print("Putting current weapon away")
                self.items['weapons'][self.weapon.name] = self.weapon # Put that weapon in inv
            # Add it to inventory and equip it
            #print("Don't have that weapon")
            self.items['weapons'][weapon] = Gun(weapon)
            self.weapon = self.items['weapons'][weapon]
            self.add_ammo(weapon)
            
    def add_ammo(self, weapon):
        if weapon in self.items['ammo']: # Already have some of that ammo?
            #print("Have some of that ammo already")
            # Add more ammo
            self.items['ammo'][weapon] += WEAPONS[weapon]['capacity']
        else: # Don't already have some of that ammo
            #print("New ammo type")
            # Add a mag's worth to inventory
            self.items['ammo'][weapon] = WEAPONS[weapon]['capacity']
            
    def cycle_weapon(self):
        #print("Inventory: {}".format(self.items['weapons'].keys()))
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
            #print("Full")
            return
        elif amount > self.data['capacity'] - self.remaining_shots:
            pass
        else:
            #print("Reloading: ",amount)
            self.remaining_shots += amount

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

