#!/usr/bin/env python3
import player
class Bam(player.Player):
    name = "SigKill"
    def __init__(self):
        self.health =  3
        self.gun_loaded = True
        self.carrying = False
        self.turn = 0

    def play(self, scores):
        return "derp"
    def inform(self, message):
        pass

