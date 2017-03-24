#!/usr/bin/env python3
import player
from textwrap import wrap
class Bam(player.Player):
    name = "HecksomeOverlord" #TY Matthew Roh for the help with the name
    def __init__(self):
        self.health = 3
        self.gun_loaded = True
        self.carrying = False
        self.turn = 0
        self.map = [[None for i in range(21*2+1)] for i in range(25*2+1)]
        self.pos = [0,0]  # all coords originate from the starting point
        self.scores = (0,0)
        self.flag_pos=1
        self.turn = 0
        self.enemies_time = None  # Turn an enemy was last encountered
        self.enemies = []  # enemies the bot is interacting with i.e. having a fight to the death with
        self.looked = None
        self.row=None #this CAN be figured out, though only under certain circumstances#
        self.look_dir = None # what direction were we looking

    def iswall(self,cell):
        pass # figure this out later #

    def play(self, scores):
        if self.scores[0] < scores[0]:
            self.flag_pos = 0
            self.scores = scores
        elif self.scores[1] < scores[1]:
            self.flag_pos = 2  # PANIC!!!!!11!
            self.scores = scores
        else:
            self.flag_pos = 1
        if self.carrying: ## FLAG TRANSPORT ##
            if self.looked != None and self.looked<(self.turn-3):
                if self.map[self.pos[1]-1][self.pos[0]] != None:
                    if not self.iswall(self.map[self.pos[1]-1][self.pos[0]]):
                        return "move 0" # 0 is up? #
                else: pass # todo: add looking here


        # Actual plays go here #

        self.turn += 1

    def inform(self, message):
        if message == "Hit":
            self.health -= 1
            self.enemies = self.turn
            self.hit = self.turn
        elif message == "Block":
            self.enemies = self.turn
            self.hit = self.turn
        elif message == "Flag get":
            self.carrying = True
        elif message == "Flag fight":
            pass
            # TODO: put thing here when I get around to adding the enemy recording thing
        elif all(i in "012345|" for i in message): # just looked
            lines=[wrap(i) for i in message.split()]
            lines[0]
