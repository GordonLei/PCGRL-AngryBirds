import os
import subprocess
import time
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image
from gym_pcgrl.envs.probs.problem import Problem
from gym_pcgrl.envs.helper import get_range_reward, get_tile_locations, calc_certain_tile, calc_num_regions
from gym_pcgrl.envs.probs.mdungeon.engine import State,BFSAgent,AStarAgent

rt_corner=0
rh_corner=1
rs_corner=2
rm_corner=3
rl_corner=4
rf_corner=5
tnt_corner=6
pig=7
empty=8 #8
solid=9 #9
rh_l=10
rh_r=11
rh_lr=12
rh_ul=13
rh_ur=14
rs_o1=15
rm_o1=16
rm_o2=17
rm_o3=18
rl_o1=19
rl_o2=20
rl_o3=21
rl_o4=22
rf_lr=23
rf_ul=24
rf_ur=25
tnt_lr=26
tnt_ul=27
tnt_ur=28


"""

"""

class AngryBirdsProblem(Problem):
    """
    The constructor is responsible of initializing all the game parameters
    """
    def __init__(self):
        super().__init__()

        # solver_power
        self._solver_power = 5000

        # the floor is y = -3.25
        # the ceiling is y = 2.0 
        
        # the leftmost wall is x = -4
        # the rightmost wall is x = 11.00

        #a platform is around .5 radius so it's a 1x1 block
        #FAT blocks are .5; regular are .25 radius

        # x is 15 wide so you probably want around 15*2 for width
        self._width = 30 #11#30 #amount of .5 segments

        # x is 15 wide so you probably want around 15/(.215*2) for width
        # times 2 since it is .215 from center of object to the origin so double to get full max height 
        #self._width = 35 #amount of .5 segments

        # y is around 5.25 tall so 5.25*4 for height
        self._height = 21 #7#21 #amount of .25 segments

        # y is around 5.25 tall so 5.25/(.110*2) for height
        # times 2 since it is .215 from center of object to the origin so double to get full max height 
        #self._height = 24 #amount of .25 segments

        # a dictionary that contains all of the possible tile types
        self._tiles = self.get_tile_types()

        # probably table of how likely a certain tile would be generated for initial state
        self._prob = {
            "rt_corner":0.01,
            "rh_corner":0.02,
            "rs_corner":0.01,
            "rm_corner":0.02,
            "rl_corner":0.01,
            "rf_corner":0.01,
            "tnt_corner":0.01,

            "empty":0.45,
            "solid":0.00,

            
            "rh_l":0.00,
            "rh_r":0.00,
            "rh_lr":0.00,
            "rh_ul":0.00,
            "rh_ur":0.00,

            
            "rs_o1":0.00,

            
            "rm_o1":0.00,
            "rm_o2":0.00,
            "rm_o3":0.00,

            
            "rl_o1":0.00,
            "rl_o2":0.00,
            "rl_o3":0.00,
            "rl_o4":0.00,

            
            "rf_lr":0.00,
            "rf_ul":0.00,
            "rf_ur":0.00,

            
            "tnt_lr":0.00,
            "tnt_ul":0.00,
            "tnt_ur":0.00,

            "pig":0.01,
            # "redBird":0.002,
            # "blueBird":0.002,
            # "yellowBird":0.002,
            # "whiteBird":0.002,
            # "blackBird":0.002,
        }

        i = 0.00
        
        self._border_tile = "solid"
        # max_enemies would be number of pigs
        self._max_pigs = 5
        #self._max_birds = 5
        self._max_blocks = 100
        self._max_tnt = 3

        self._rewards = {
            "pig": 3,
            "blocks": 2,
            "tnt": 4,
            "stability": 5
        }
        self._map = [[]]


        #self._border_size = (1, 1)
        #self._border_tile = tiles[0]
        #self._tile_size = 16

    """
        Get a dictionary of all the different tile names
        (blocks 3, 7, 9, 11 and 13) are their respective block names rotated 90 degrees clockwise
        Returns:
            dictionary: key = tile number, value = name of tile
    """
    def get_tile_types(self):
        return [
            "rt_corner",#0
            "rh_corner",#1
            "rs_corner",#2
            "rm_corner",#3
            "rl_corner",#4
            "rf_corner",#5
            "tnt_corner",#6
            "pig",#7

            
            "empty", #8
            "solid", #9


            "rh_l",#10
            "rh_r",#11
            "rh_lr",#12
            "rh_ul",#13
            "rh_ur",#14


            "rs_o1",#15


            "rm_o1",#16
            "rm_o2",#17
            "rm_o3",#18


            "rl_o1",#19
            "rl_o2",#20
            "rl_o3",#21
            "rl_o4",#22


            "rf_lr",#23
            "rf_ul",#24
            "rf_ur",#25

            "tnt_lr",#26
            "tnt_ul",#27
            "tnt_ur",#28
            
        ]
        
    def adjust_param(self, **kwargs):
        super().adjust_param(**kwargs)

        self._max_pigs = kwargs.get('max_pigs', self._max_pigs)
        #self._max_birds = kwargs.get('max_birds', self._max_birds)
        self._max_blocks = kwargs.get('max_blocks', self._max_blocks)
        self._max_tnt = kwargs.get('max_tnt', self._max_tnt)


        self._solver_power = kwargs.get('solver_power', self._solver_power)

        # self._max_enemies = kwargs.get('max_enemies', self._max_enemies)
        # self._max_potions = kwargs.get('max_potions', self._max_potions)
        # self._max_treasures = kwargs.get('max_treasures', self._max_treasures)
        #
        # self._target_col_enemies = kwargs.get('target_col_enemies', self._target_col_enemies)
        #self._target_solution = kwargs.get('target_solution', self._target_solution)

        rewards = kwargs.get('rewards')
        if rewards is not None:
            for t in rewards:
                if t in self._rewards:
                    self._rewards[t] = rewards[t]

    '''
    check stability based on blocks underneath

    If level is stable, then it should return an int = number of blocks in the level
    '''

    def _blocks_stability(self, map):
        #print(map)
        coords = []
        # map looks like this 
        # top-most row is the top most level
        # bottom-most row is the bottom most level
        # 0,0 is upper left corner 
        x_length = len(map[0])
        y_length = len(map)
        #each row is a y value
        #each col is a x value

        corners = ["rt_corner","rh_corner","rs_corner","rm_corner","rl_corner","rf_corner","tnt_corner","pig"]
        
        stability_counter = 0

        for y in range(y_length):
            for x in range(x_length):
                #print("COORDS: ",x,y, "max:", x_length, y_length)
                #to iterate the map, the x value is the first index. the y value is the second index 
                if( map[y][x] in corners):
                    block_value = corners.index(map[y][x])
                    coords.append([block_value,y,x])

        block_counter = len(coords)

        #print(len(coords))
        #print(coords)
        #check each coord and see if there is a block underneath it 
        for each in coords:
            #print(each[0], each[1], each[2])
            y = each[1]
            x = each[2]
            #if y-value is the max, it is on the floor therefore the block is stable 
            if each[1] == y_length - 1:
                #print("on the floor increase", stability_counter)
                stability_counter += 1
            else:
                if each[0] == rt_corner or each[0] == pig:
                    if(map[y+1][x] == "empty"):
                        stability_counter -= 1
                    else:
                        #print("rt bottom not empty", stability_counter, map[y+1][x])
                        stability_counter += 1
                #rh
                elif each[0] == rh_corner:
                    if(map[y+1][x] == "empty" or map[y+1][x+1] == "empty"):
                        #print("rh empty", stability_counter, map[y+1][x],map[y+1][x+1])
                        stability_counter -= 1
                    else:
                        #print("rh bottom not empty", stability_counter, map[y+1][x],map[y+1][x+1])
                        stability_counter += 1
                #rs
                elif each[0] == rs_corner:
                    if(map[y+1][x] == "empty" and map[y+1][x+1] == "empty"):
                        #print("rs bottom empty", stability_counter, map[y+1][x],map[y+1][x+1])
                        stability_counter -= 1
                    else:
                        #print("rs bottom not empty", stability_counter, map[y+1][x],map[y+1][x+1])
                        stability_counter += 1
                #rm
                elif each[0] == rm_corner:
                    empty_counter = 0
                    for i in range(0,4):
                        if map[y+1][x+i] == "empty":
                            empty_counter += 1
                    if(empty_counter >= 3):
                        #print("rm bottom empty", stability_counter, map[y+1][x],map[y+1][x+1],map[y+1][x+2],map[y+1][x+3])
                        stability_counter -= 1
                    else:
                        #print("rm bottom not empty", stability_counter, map[y+1][x],map[y+1][x+1],map[y+1][x+2],map[y+1][x+3])
                        stability_counter += 1
                #rl
                elif each[0] == rl_corner:
                    #if( map[y+1][x+1] == "empty" and (map[y+1][x+2] == "empty" and map[y+1][x+3] == "empty" and map[y+1][x+4] == "empty") ):
                        #stability_counter -= 1
                    empty_counter = 0
                    for i in range(0,5):
                        if map[y+1][x+i] == "empty":
                            empty_counter += 1
                    if(empty_counter >= 3):
                        #print("rl bottom empty", stability_counter, map[y+1][x],map[y+1][x+1],map[y+1][x+2],map[y+1][x+3],map[y+1][x+4])
                        stability_counter -= 1
                    else:
                        #print("rl bottom not empty", stability_counter, map[y+1][x],map[y+1][x+1],map[y+1][x+2],map[y+1][x+3],map[y+1][x+4])
                        stability_counter += 1
                #rf
                elif each[0] == rf_corner:
                    if(map[y+1][x] == "empty" or map[y+1][x+1] == "empty"):
                        stability_counter -= 1
                    else:
                        stability_counter += 1
                #tnt
                elif each[0] == tnt_corner:
                    if(map[y-1][x] == "empty" and map[y-1][x+1] == "empty"):
                        stability_counter -= 1
                    else:
                        stability_counter += 1
                #error
                else:
                    print("ERROR in stability check", each[0])
        #print(stability_counter, block_counter)
        if(stability_counter >= block_counter):
            print("STABLE LEVEL")
            #time.sleep(500)
        #return 1 if every block is stable; return varying degree of negative depending on how many blocks are unstable
        return ( stability_counter -  (block_counter - 1))
    """
        Private function that test if current map is stable.
        Simulates the level to test for stability. 
        Parameters:
            map (string[][]): the input level to run the game on
        Returns:
            int: 0 if not stable, 1 if stable
    """

    def _test_stability(self, map):
        #print(os.path.dirname(os.path.realpath(__file__)))
        input_path = os.path.abspath(os.path.join(__file__ ,"../../../../../compare_XML/input.xml"))
        output_path = os.path.abspath(os.path.join(__file__ ,"../../../../../compare_XML/output.xml"))
        try: 
            parser = ET.XMLParser(encoding="utf-8")
            input_XML = ET.parse(input_path, parser= parser)

            #'''
            #run the Unity .exe
            script1 = "D:\\Unity\\2017.3.1f1\\Editor\\Unity.exe -quit -batchmode -buildTarget win64 -projectPath C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds -executeMethod MyEditorScript.PerformBuild"
            script2 = "C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds\\EXE\\DUMMY.exe"

            sb = subprocess.Popen(script1)
            time.sleep(20)

            sb.terminate()
            print("compiling Unity project done")
            sb = subprocess.Popen(script2)
            
            time.sleep(10)
            sb.terminate()
            #'''
            print("open and closed Unity project")

            parser = ET.XMLParser(encoding="utf-8")
            output_XML = ET.parse(output_path, parser= parser)
            print("parsed through output_XML")
            input_root = input_XML.getroot()
            output_root = output_XML.getroot()
            # [1] is <Birds> tag 
            # [5] is <GameObjects depending on number of birds>. so use .tag to find GameObjects Tag 
            # input and output file look the same 

            GO_input_index = 0 
            GO_output_index = 0

            #do this to increment to where the .tag is GameObjects
            while(input_root[1][GO_input_index].tag != "GameObjects"):
                GO_input_index += 1
                #print("INC 1")
            while(output_root[1][GO_output_index].tag != "GameObjects"):
                GO_output_index += 1
                #print("INC 2")

            #this means that something changed before reaching GameObjects
            if(GO_input_index != GO_output_index):
                return 0 

            x_threshold = .25
            y_threshold = .25

            #check if anything shifted. if something shifted, then level is unstable therefore return 0 reward
            for i in range(len (input_root[1][GO_input_index] )):
                input_obj = input_root[1][GO_input_index][i].attrib
                output_obj = output_root[1][GO_input_index][i].attrib
                if( abs( float(input_obj['x']) - float(output_obj['x'])) >= x_threshold  
                    or abs( float(input_obj['y']) - float(output_obj['y'])) >= y_threshold):
                    return 0 
                else:
                    print("stable level")
            # 1 means this is stable? 
            return 1
        except:
            print(".EXE failed compilation OR output.xml is empty")
            pass

    """
        Get the current stats of the map
        
        Returns:
            dict(string,any): stats of the current map to be used in the reward, episode_over, debug_info calculations.
            The used status are "player": number of player tiles, "crate": number of crate tiles,
            "target": number of target tiles, "reigons": number of connected empty tiles,
            "dist-win": how close to the win state, "sol-length": length of the solution to win the level
        
        From sokoban_ban.py, need to adapt for Angry Birds
    """
    def get_stats(self, map):
        map_locations = get_tile_locations(map, self.get_tile_types())
        self._map = map
        map_stats = {
            "empty": calc_certain_tile(map_locations, ["empty"]),
            "pig": calc_certain_tile(map_locations, ["pig"]),
            "tnt": calc_certain_tile(map_locations, ["tnt_corner"]),
            # "birds": calc_certain_tile(map_locations, ["redBird", "blueBird", "yellowBird", "whiteBird", "blackBird"]),

            #REMOVED squareTiny and circles and trianglesfrom the 2 below
            "blocks": calc_certain_tile(
                map_locations, ["rt_corner", "rh_corner", "rs_corner", "rm_corner", "rl_corner", "rf_corner", "tnt_corner"]),
            "stability": self._blocks_stability(self._map)
            #"regions": calc_num_regions(
            #    map, map_locations, ["empty", "pig", "rt_corner", "rh_corner", "rs_corner", "rm_corner", "rl_corner", "rf_corner", "tnt_corner"]),
        }
        #this part is to find other keys for map_states
        '''
        if map_stats["player"] == 1 and map_stats["regions"] == 1:
            p_x,p_y = map_locations["player"][0]
            enemies = []
            enemies.extend(map_locations["spider"])
            enemies.extend(map_locations["bat"])
            enemies.extend(map_locations["scorpion"])
            if len(enemies) > 0:
                dikjstra,_ = run_dikjstra(p_x, p_y, map, ["empty", "player", "bat", "spider", "scorpion"])
                min_dist = self._width * self._height
                for e_x,e_y in enemies:
                    if dikjstra[e_y][e_x] > 0 and dikjstra[e_y][e_x] < min_dist:
                        min_dist = dikjstra[e_y][e_x]
                map_stats["nearest-enemy"] = min_dist
            if map_stats["key"] == 1 and map_stats["door"] == 1:
                k_x,k_y = map_locations["key"][0]
                d_x,d_y = map_locations["door"][0]
                dikjstra,_ = run_dikjstra(p_x, p_y, map, ["empty", "key", "player", "bat", "spider", "scorpion"])
                map_stats["path-length"] += dikjstra[k_y][k_x]
                dikjstra,_ = run_dikjstra(k_x, k_y, map, ["empty", "player", "key", "door", "bat", "spider", "scorpion"])
                map_stats["path-length"] += dikjstra[d_y][d_x]
        '''

        return map_stats


    """
        Get the current game reward between two stats
        
        A sum of variety value, pig placement potential, and stability. 
        
        Parameters:
            map: level
            new_stats (dict(string,any)): the new stats after taking an action
            old_stats (dict(string,any)): the old stats before taking an action
        Returns:
            float: the current reward due to the change between the old map stats and the new map stats
    """
    def get_reward(self, new_stats, old_stats):
        rewards = {
            #"empty": get_range_reward(new_stats["empty"], old_stats["empty"], 1, 1),
            "pig": get_range_reward(new_stats["pig"], old_stats["pig"], 1, self._max_pigs),
            "tnt": get_range_reward(new_stats["tnt"], old_stats["tnt"], 0, self._max_tnt),
            #"birds": get_range_reward(new_stats["birds"], old_stats["birds"], 1, self._max_birds),
            "blocks": get_range_reward(new_stats["blocks"], old_stats["blocks"], 1, self._max_blocks),
            #"regions": get_range_reward(new_stats["regions"], old_stats["regions"], 1, 1)

            #this part is for stability 
            "stability": get_range_reward(new_stats["stability"], old_stats["stability"], 1,1)
        }

        #print(rewards["pig"] * self._rewards["pig"],
        #    rewards["tnt"] * self._rewards["tnt"],
        #    rewards["blocks"] * self._rewards["blocks"],
        #    rewards["stability"] * self._rewards["stability"])

        return rewards["pig"] * self._rewards["pig"]  +\
            rewards["tnt"] * self._rewards["tnt"] +\
            rewards["blocks"] * self._rewards["blocks"] +\
            rewards["stability"] * self._rewards["stability"] 
        # rewards["birds"] * self._rewards["birds"] +\
        #return self._get_variety_value(map, 1) + self._test_stability(map) + self._get_pig_potential(map, 1)

    """
        Uses the stats to check if the problem ended (episode_over) which means reached
        a satisfying quality based on the stats
        
        If map is stable and there are enough blocks(less than 10 percent of empty tiles), then can end

        Parameters:
            new_stats (dict(string,any)): the new stats after taking an action
            old_stats (dict(string,any)): the old stats before taking an action

        Returns:
            boolean: True if the level reached satisfying quality based on the stats and False otherwise
    """
    def get_episode_over(self, new_stats, old_stats):
        percentage = 0.60
        #print(new_stats["empty"] / (self._height*self._width))
        # return self._test_stability(map) == 1 and len(new_stats["empty"]) * 100 / self._height*self._width*100 < percentage
        #print((new_stats["empty"] / (self._height*self._width)) < percentage)
        return (new_stats["empty"] / (self._height*self._width)) < percentage and\
            new_stats["pig"] <= self._max_pigs and new_stats["pig"] > 0 and\
            new_stats["blocks"] <= self._max_blocks and\
            new_stats["tnt"] <= self._max_tnt and\
            new_stats["stability"] >= 0
        #return self._test_stability(map) == 1 and new_stats["empty"] * 100 / self._height*self._width*100 < percentage

    """
        Uses a formula to calculate how varied the blocks are in current level

        Parameters:
            map: the level
            factor: affects how much impact would variety cause

        Returns:
            return variety value as a double
    """
    def _get_variety_value(self,map, factor):
        return

    def _get_pig_potential(self,map, factor):
        return
    
    """
    Get any debug information need to be printed

    Parameters:
        new_stats (dict(string,any)): the new stats after taking an action
        old_stats (dict(string,any)): the old stats before taking an action

    Returns:
        dict(any,any): is a debug information that can be used to debug what is
        happening in the problem
    """
    def get_debug_info(self, new_stats, old_stats):
        return {
            "empty": new_stats["empty"],
            "pig": new_stats["pig"], 
            "tnt": new_stats["tnt"], 
            #"birds": new_stats["birds"],
            "blocks": new_stats["blocks"], 
            #"regions": new_stats["regions"] 
        }

    """
        Get an image on how the map will look like for a specific map

        Parameters:
            map (string[][]): the current game map

        Returns:
            Image: a pillow image on how the map will look like using the binary graphics
        """

    def render(self, map):
        if self._graphics == None:
            self._graphics = {
                "empty": Image.open(os.path.dirname(__file__) + "/angrybirds/empty.png").convert('RGBA'),
                "solid": Image.open(os.path.dirname(__file__) + "/angrybirds/solid.png").convert('RGBA'),

                "rt_corner":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rt_corner.png").convert('RGBA'),

                "rh_corner":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rh_corner.png").convert('RGBA'),
                "rh_l":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rh_l.png").convert('RGBA'),
                "rh_r":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rh_r.png").convert('RGBA'),
                "rh_lr":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rh_lr.png").convert('RGBA'),
                "rh_ul":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rh_ul.png").convert('RGBA'),
                "rh_ur":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rh_ur.png").convert('RGBA'),

                "rs_corner":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rs_corner.png").convert('RGBA'),
                "rs_o1":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rs_o1.png").convert('RGBA'),

                "rm_corner":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rm_corner.png").convert('RGBA'),
                "rm_o1":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rm_o1.png").convert('RGBA'),
                "rm_o2":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rm_o2.png").convert('RGBA'),
                "rm_o3":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rm_o3.png").convert('RGBA'),

                "rl_corner":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rl_corner.png").convert('RGBA'),
                "rl_o1":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rl_o1.png").convert('RGBA'),
                "rl_o2":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rl_o2.png").convert('RGBA'),
                "rl_o3":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rl_o3.png").convert('RGBA'),
                "rl_o4":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rl_o4.png").convert('RGBA'),

                "rf_corner":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rf_corner.png").convert('RGBA'),
                "rf_lr":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rf_lr.png").convert('RGBA'),
                "rf_ul":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rf_ul.png").convert('RGBA'),
                "rf_ur":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/rf_ur.png").convert('RGBA'),

                "tnt_corner":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/tnt_corner.png").convert('RGBA'),
                "tnt_lr":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/tnt_lr.png").convert('RGBA'),
                "tnt_ul":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/tnt_ul.png").convert('RGBA'),
                "tnt_ur":Image.open(os.path.dirname(__file__) + "/angrybirds/new_sprites/tnt_ur.png").convert('RGBA'),

                "pig": Image.open(os.path.dirname(__file__) + "/angrybirds/pig.png").convert('RGBA'),
                
                # "redBird": Image.open(os.path.dirname(__file__) + "/angrybirds/redBird.png").convert('RGBA'),
                # "blueBird": Image.open(os.path.dirname(__file__) + "/angrybirds/blueBird.png").convert('RGBA'),
                # "yellowBird": Image.open(os.path.dirname(__file__) + "/angrybirds/yellowBird.png").convert('RGBA'),
                # "whiteBird": Image.open(os.path.dirname(__file__) + "/angrybirds/whiteBird.png").convert('RGBA'),
                # "blackBird": Image.open(os.path.dirname(__file__) + "/angrybirds/blackBird.png").convert('RGBA'),
            }
        self._map = map
        return super().render(map)
