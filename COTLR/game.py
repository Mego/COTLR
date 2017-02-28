import maze as mazer
import random
from copy import deepcopy
import importlib
import bots
import player
def has_enemy(space, team):
    if not is_wall(space):
        index = 0 if (team == 1) else 1
        return space[index][0] > 0


def is_wall(space):
    return space in (1, 2, 3)  # walls are one of these integers


class Player_holder:
    def __init__(self, bot, x, y, team):
        self.bot = bot()
        self.team = team
        self.health =  3
        self.gun_loaded = True
        self.carrying = False
        # This variable is used to check whether the artifact is being carried by this player

        # location
        self.x = x
        self.y = y

    def play(self, scores):
        if self.team == 1:
            scores = scores[::-1]
        response = self.bot.play(scores)
        if len(response) == 2:
            if self.team == 1 and int(response[1]) in (0, 2):
                    direction = 0 if int(response[1]) == 2 else 2
            else:
                direction = int(response[1])
            return response[0],  direction
        else:
            return response[0]

    def inform(self, message):
        self.bot.inform(message)

class Playfield:
    def __init__(self, maze, artifact, bots):
        self.maze = deepcopy(maze)
        self.artifact = artifact[:]
        self.bots = bots
        self.outcomes = [0, 0]
        self.game()
        #print("poo")
        self.maze = deepcopy(maze)[::-1]
        self.artifact = artifact[:]
        self.game()

    def game(self):
        self.unit_list = []
        self.respawns = ([],[])
        self.scores = [0, 0]
        for unit_pair in range(5):
            for team in (0, 1):
                self.spawn(team)
        total_turns = 1000
        for turn in range(1,total_turns+1): #might change the winning score
            self.play(turn)
            print("\n".join(''.join("++" if i ==3 else "||" if i == 1 else "--" if i == 2 else "<>" if i[2] else str(i[0][0])+str(i[1][0]) for i in line) for line in self.maze))
            if abs(self.scores[0]-self.scores[1])>total_turns-turn:
                break  # If the condition is true, it means the one side has no chance of winning
                #        because there is not enough time for them to score enough with perfect play
        if self.scores[0] > self.scores[1]:
            self.outcomes[0] += 1
        elif self.scores[0] < self.scores[1]:
            self.outcomes[1] += 1

    def spawn(self, team):
        if team == 0: spawn_area = range(1, len(self.maze)//3+1)
        else: spawn_area = range(len(self.maze) - len(self.maze)//3 - 1, len(self.maze) - 1)
        available_spaces = []
        for row in spawn_area:
            for possible_space in range(len(self.maze[row])):
                if not is_wall(self.maze[row][possible_space]):
                    possible = True
                    directions_checking = [True for i in range(8)]
                    distance_multi = tuple((i,j) for i in (1, 0, -1) for j in (1, 0, -1) if i or j)
                    distance = 1
                    while any(directions_checking) and possible:
                        for index in range(len(directions_checking)):
                            if directions_checking[index]:
                                check_space = (self.maze[row+distance*distance_multi[index][0]]
                                                [possible_space+distance*distance_multi[index][1]])
                                if has_enemy(check_space, team):
                                        possible = False
                                elif is_wall(check_space):
                                    directions_checking[index] = False
                        distance += 1
                    if possible: available_spaces.append((row, possible_space))
        spawn_space = random.choice(available_spaces)
        self.maze[spawn_space[0]][spawn_space[1]][team][0] += 1
        self.unit_list.append(Player_holder(self.bots[team], spawn_space[1], spawn_space[0], team))

    def play(self, turn):
        actions = ([], [], [])
        attacks = {}
        for unit in self.unit_list:
            move = unit.play(self.scores)
            if move[0] == "shoot" and unit.gun_loaded and not unit.carrying:
                actions[0].append((unit, move[1]))
            elif move[0] == "stab":  # might make it illegal to stab while having flag
                if (unit.x, unit.y) in attacks:
                    attacks[(unit.x, unit.y)].append(unit)
                else:
                    attacks[(unit.x, unit.y)] = [unit]
            elif move[0] == "look":
                actions[1].append((unit, move[1]))
            elif move[0] == "take" and not unit.carrying:
                actions[2].append(unit)
            elif move[0] == "reload" and not unit.carrying:
                unit.gun_loaded = True
            elif move[0] == "drop" and unit.carrying:
                self.maze[unit.y][unit.x][unit.team][1] = False
                self.maze[unit.y][unit.x][2] = True

            elif move[0] == "move":
                self.maze[unit.y][unit.x][unit.team][0] -= 1
                step = ((move[1] == 1) - (move[1] == 3), (move[1] == 2) - (move[1] == 0))
                if not is_wall(self.maze[unit.y + step[1]][unit.x + step[0]]):
                    if unit.carrying:
                        self.maze[unit.y][unit.x][unit.team][1] = False
                    unit.x += step[0]
                    unit.y += step[1]
                    if unit.carrying:
                        self.artifact[0] += step[0]
                        self.artifact[1] += step[1]
                        self.maze[unit.y][unit.x][unit.team][1] = True
                    self.maze[unit.y][unit.x][unit.team][0] += 1
                else:
                    unit.inform("Wall")
        for unit, direction in actions[0]: # shooting
            distance = 1
            direction_multiplicands = ((0, -1), (1, 0), (0, 1), (-1, 0))
            direction = direction_multiplicands[direction]
            shot_flying = True
            while shot_flying:
                check_cell = self.maze[unit.y+distance*direction[1]][[unit.x+distance*direction[0]]]
                if has_enemy(check_cell, unit.team):
                    shot_flying = False
                    shot_cell = (unit.x+distance*direction[0],unit.y+distance*direction[1])
                    if shot_cell in attacks:
                        attacks[shot_cell].append(unit)
                    else:
                        attacks[shot_cell] = [unit]
                elif is_wall(check_cell):
                    shot_flying = False
                else: distance += 1
        killed_units = []
        for unit in self.unit_list:
            if (unit.x,unit.y) in attacks:
                cell_shots = attacks[(unit.x,unit.y)]
                for shot in cell_shots:
                    if shot.team != unit.team:
                        if not unit in attacks[(shot.x,shot.y)]:
                            if not shot.x == unit.x and shot.y == unit.y:
                                unit.health -= 1
                            else:
                                unit.health = 0
                            if unit.health == 0:
                                killed_units.append(unit)
                                self.maze[unit.x,unit.y][unit.team][0] -= 1
                                if unit.carrying:
                                    self.maze[unit.x,unit.y][unit.team][1] = False
                                    self.maze[unit.x,unit.y][2] = True
                                break
                            else:
                                unit.inform("Hit")
                        else:
                            unit.inform("Block")
        for unit in killed_units:
            actions[1].remove(unit)
            actions[2].remove(unit)
            self.respawns[unit.team].append(turn+5)
        for unit in actions[2]:
            if not self.maze[unit.y][unit.x][2]:
                actions[2].remove(unit)
        if len(actions[2]) == 1:
            flag_holder = actions[2][0]
            flag_holder.carrying = True
            flag_holder.inform("flag get")
            self.maze[flag_holder.y][flag_holder.x][2] = False
            self.maze[flag_holder.y][flag_holder.x][flag_holder.team] = True
        else:
            for bot in actions[2]:
                bot.inform("flag fight")
        for team in (0,1):
            for spawn in self.respawns[team]:
                if spawn == turn:
                    self.spawn(team)
        for unit, direction in actions[1]: # viewing
            input_info = []
            if direction in (0, 3):
                multiplier = -1
            else:
                multiplier = 1
            offsets = (1, 0, -1) if unit.team == 1 and direction in (1, 3) else (-1, 0, 1)

            for offset in offsets:
                distance = 1
                ray_casting = True
                while ray_casting:
                        if direction in (1, 3):
                            cell = self.maze[unit.y + distance * offset][unit.x + distance * multiplier]
                        else:
                            cell = self.maze[unit.y + distance * multiplier][unit.x + distance * offset]
                        if is_wall(cell):
                            ray_casting = False
                        else:
                            if cell[2]:
                                flag_status = "1"
                            elif cell[team][1]:
                                flag_status = "2"
                            elif cell[not team][1]:
                                flag_status = "3"
                            else:
                                flag_status = "0"
                            input_info.append(str(cell[team][0]))
                            input_info.append(flag_status)
                            input_info.append(str(cell[not team][0]))
                if offset != 1:
                    input_info.append("|")
            unit.inform(''.join(input_info))
        if self.artifact[1] <= len(self.maze)//3:
            self.scores[1] += 1
        elif self.artifact[1] > len(self.maze) - len(self.maze)//3:
            self.scores[0] += 1


def find_bot(module):
    for value in module.__dict__.values():
        try:
            if issubclass(value, player.Player):
                if value is not player.Player:
                    return value
        except TypeError:
            pass
    raise Exception("A class in the module that inherits from Player was not found in {}".format(module))

bots_list = open("bots.txt")
bot_names = bots_list.read().split("\n")
bot_modules = [importlib.import_module("bots."+bot_name, "bots") for bot_name in bot_names]
bots_classes = [find_bot(bot_module) for bot_module in bot_modules]

overall_scores = [0 for i in bot_names]
repeats = 40
first_bot = 0
while first_bot < len(bots_classes):
    second_bot = first_bot+1
    while second_bot < len(bots_classes):
        print("%s vs %s; Fight"%(bots_classes[first_bot].name, bots_classes[second_bot].name))
        for i in range(repeats):
            maze_stuff = mazer.gen_maze()
            playfield = Playfield(maze_stuff[0], maze_stuff[1],(bots_classes[first_bot], bots_classes[second_bot]))
            if playfield.outcomes[0] > playfield.outcomes[1]:
                overall_scores[first_bot] += 2
                print("Round %d: %s wins"%(i,bots_classes[first_bot].name))
            elif playfield.outcomes[0] < playfield.outcomes[1]:
                overall_scores[second_bot] += 2
                print("Round %d: %s wins"%(i,bots_classes[second_bot].name))
            else:
                overall_scores[first_bot] += 1
                overall_scores[second_bot] += 1
                print("Round %d: Draw"%i)
        second_bot += 1
    first_bot += 1