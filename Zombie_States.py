import pygame as pg
vec = pg.math.Vector2
from settings import *
from random import choice
from AI import State
from sprites import vec2int

class ZombieGlobalState(State):
    def __init__(self, game, mob):
        super().__init__(mob)
        self.game = game
        
    def enter(self):
        pass
    
    def execute(self):
        #Conditional things in if statements#
        #Things to happen every update
        # Put in changes that can occur from any state to avoid having to repeat it in
        # all states that need it. 
        # player detected
        if self.mob.test_for_player(self.game.player):
            self.mob.SM.change_state(Aggro(self.game, self.mob))
        else:
            if self.mob.SM.previous_state == None:
                self.mob.SM.change_state(Idle(self.mob))
            else:
                self.mob.SM.revert_to_previous_state()
                  
            
    def exit(self):
        pass


class Idle(State):
    def __init__(self, mob):
        self.mob = mob

    def enter(self):
        pass

    def execute(self):
        #Chance to play idle sound every few seconds
        # Behaviour 1 - pick random direction to walk (slow), pause, pick new direction etc
        # Behaviour 2 - walk constantly (slow) changing direction every 10 or so seconds        
        pass
    def exit(self):
        pass


class Aggro(State):
    def __init__(self, game, mob):
        self.mob = mob
        self.game = game
        
    def enter(self):
        if isinstance(self.mob.SM.previous_state, Idle) or isinstance(self.mob.SM.previous_state, Suspicious):
            choice(self.game.zombie_moan_sounds).play()
    
    def execute(self):
        self.mob.speed = choice(MOB_SPRINT_SPEEDS)
        self.mob.move(self.game.player.pos)
                
    def exit(self):
        pass


class Suspicious(State):
    def __init__(self, mob):
        self.mob = mob

    def enter(self):
        if isinstance(self.mob.SM.previous_state, Aggro):
            self.mob.last_known = vec2int(self.game.player.pos)

    def execute(self):
        last_known_dist = self.mob.pos - vec(self.mob.last_known)
        if last_known_dist.length_squared() > 1000: # while not within 1000 pixels?
            self.mob.move(self.mob.last_known)
        else:
            self.mob.speed = choice(MOB_WANDER_SPEEDS)
    def exit(self):
        pass
