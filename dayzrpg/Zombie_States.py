import pygame as pg
from settings import *
from random import choice
from AI import State
from sprites import vec2int
import logging
vec = pg.math.Vector2
logger = logging.getLogger(__name__)


class ZombieGlobalState(State):
    def __init__(self, game, mob):
        super().__init__(mob)
        self.game = game

    def enter(self):
        pass

    def execute(self):
        # Conditional things in if statements#
        # Things to happen every update
        # Put in changes that can occur from any state to avoid having to repeat it in
        # all states that need it.
        pass
#        if self.mob.test_for_player(self.game.player): #Alerted
#            self.mob.alerted = True
#            if isinstance(self.mob.SM.current_state, Aggro):
#                pass
#            else:
#                self.mob.SM.change_state(Aggro(self.game, self.mob))
#        else: #
#            self.mob.alerted = False
#            if self.mob.SM.previous_state == None:
#                self.mob.SM.change_state(Idle(self.game, self.mob))
#            elif isinstance(self.mob.SM.previous_state, Aggro):
#                self.mob.SM.change_state(Suspicious(self.game, self.mob))
#            else:
#                self.mob.SM.revert_to_previous_state()

    def exit(self):
        pass


class Idle(State):
    def __init__(self, game, mob):
        self.mob = mob
        self.game = game
        self.logger = logging.getLogger('game.Game.Idle')

    def enter(self):
        self.mob.speed = choice(MOB_IDLE_SPEEDS)
        self.mob.detect_radius = MOB_DETECT_BASE + int(self.game.player.vel.length() * MOB_DETECT_MOD)
        self.logger.info(f"ETR IDLE: Idle detect radius: {self.mob.detect_radius}, speed: {self.mob.speed}")

    def execute(self):
        # Chance to play idle sound every few seconds
        # Behaviour 1 - pick random direction to walk (slow), pause, pick new direction etc
        # Behaviour 2 - walk constantly (slow) changing direction every 10 or so seconds        
        self.mob.detect_radius = MOB_DETECT_BASE + int(self.game.player.vel.length() * MOB_DETECT_MOD)
        if self.mob.test_for_player(self.game.player):
            self.mob.SM.change_state(Aggro(self.game, self.mob))
        else:
<<<<<<< HEAD
            self.mob.wander()
=======
            self.mob.wander(wander_speed=1, target_change_time=MOB_WANDER_TIME * 3)
>>>>>>> zombies now don't rapidly change directions when approaching target

    def exit(self):
        pass


class Aggro(State):
    def __init__(self, game, mob):
        self.mob = mob
        self.game = game
        self.logger = logging.getLogger('game.Game.Aggro')

    def enter(self):
        self.mob.speed = choice(MOB_SPRINT_SPEEDS)
        self.mob.alerted = True
        self.mob.detect_radius = MOB_LOSE_DETECT
        self.logger.info("Aggro detect radius: {}".format(self.mob.detect_radius))

        if isinstance(self.mob.SM.previous_state, Idle) or isinstance(self.mob.SM.previous_state, Suspicious):
            choice(self.game.zombie_moan_sounds).play()

    def execute(self):
        if self.mob.test_for_player(self.game.player):
            self.mob.first = True
            self.mob.speed = choice(MOB_SPRINT_SPEEDS)
            self.mob.move_to_target(self.game.player.pos)
        else:
            self.mob.SM.change_state(Suspicious(self.game, self.mob))

    def exit(self):
        self.mob.alerted = False


class Suspicious(State):
    def __init__(self, game, mob):
        self.mob = mob
        self.game = game
        self.logger = logging.getLogger('game.Game.Suspicious')

    def enter(self):
        self.mob.speed = choice(MOB_SPRINT_SPEEDS)
        self.detect_radius = MOB_DETECT_BASE + int(self.game.player.vel.length() * MOB_DETECT_MOD)
        self.logger.info("Suspicious detect radius: {}".format(self.mob.detect_radius))
        self.mob.last_known = vec2int(self.game.player.pos)
        self.mob.first = False
        # Assuming always coming from Aggro state.
        self.time_since_aggro = pg.time.get_ticks()

    def execute(self):
        # Check that timer hasn't expired
        now = pg.time.get_ticks()
        if now - self.time_since_aggro > MOB_SUSP_TIME:
            self.mob.SM.change_state(Idle(self.game, self.mob))

        if self.mob.test_for_player(self.game.player):
            self.mob.SM.change_state(Aggro(self.game, self.mob))

        last_known_dist = self.mob.pos - vec(self.mob.last_known)                                 
        if last_known_dist.length_squared() > 5000:  # while not within 1000 pixels?

            self.mob.move_to_target(self.mob.last_known)
        else:
            self.mob.speed = choice(MOB_WANDER_SPEEDS)
            self.mob.wander()

    def exit(self):
        pass
