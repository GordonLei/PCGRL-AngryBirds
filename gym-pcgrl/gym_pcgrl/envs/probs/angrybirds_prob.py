import os
import subprocess
import time
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image
from gym_pcgrl.envs.probs.problem import Problem
from gym_pcgrl.envs.helper import *

"""

"""

class AngryBirdsProblem(Problem):
    """
    The constructor is responsible of initializing all the game parameters
    """
    def __init__(self):
        super().__init__()


        # the floor is y = -3.25
        # the ceiling is y = 2.0 
        
        # the leftmost wall is x = -4
        # the rightmost wall is x = 11.00

        #a platform is around .5 radius so it's a 1x1 block
        #FAT blocks are .5; regular are .25 radius

        # x is 15 wide so you probably want around 18*2 for width
        self._width = 30 #amount of .5 segments
        
        # y is around 5.25 tall so 5.25*4 for height
        self._height = 21 #amount of .25 segments

        # a dictionary that contains all of the possible tile types
        self._tiles = self.get_tile_types()

        # probably table of how likely a certain tile would be generated for initial state
        self._prob = {
            "empty":0.80,
            "solid":0.00,

            "rt_corner":0.04,

            "rh_corner":0.04,
            "rh_l":0.00,
            "rh_r":0.00,
            "rh_lr":0.00,
            "rh_ul":0.00,
            "rh_ur":0.00,

            "rs_corner":0.02,
            "rs_o1":0.00,

            "rm_corner":0.06,
            "rm_o1":0.00,
            "rm_o2":0.00,
            "rm_o3":0.00,

            "rl_corner":0.01,
            "rl_o1":0.00,
            "rl_o2":0.00,
            "rl_o3":0.00,
            "rl_o4":0.00,

            "rf_corner":0.01,
            "rf_lr":0.00,
            "rf_ul":0.00,
            "rf_ur":0.00,

            "tnt_corner":0.01,
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
        self._max_pigs = 10
        self._max_birds = 5
        self._max_blocks = 30
        self._max_tnt = 5

        self._rewards = {
            # "player": 3,
            # "bird": 3,
            "pig": 1,
            "blocks": 1,
        }


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
            "empty", #0
            "solid", #1

            "rt_corner",#2
            "rh_corner",#3
            "rh_l",#4
            "rh_r",#5
            "rh_lr",#6
            "rh_ul",#7
            "rh_ur",#8

            "rs_corner",#9
            "rs_o1",#10

            "rm_corner",#11
            "rm_o1",#12
            "rm_o2",#13
            "rm_o3",#14

            "rl_corner",#15
            "rl_o1",#16
            "rl_o2",#17
            "rl_o3",#18
            "rl_o4",#19

            "rf_corner",#20
            "rf_lr",#21
            "rf_ul",#22
            "rf_ur",#23

            "tnt_corner",#24
            "tnt_lr",#25
            "tnt_ul",#26
            "tnt_ur",#27

            "pig",#28

            # "redBird",
            # "blueBird",
            # "yellowBird",
            # "whiteBird",
            # "blackBird"
        ]
        
    def adjust_param(self, **kwargs):
        super().adjust_param(**kwargs)

        self._max_pigs = kwargs.get('max_pigs', self._max_pigs)
        self._max_birds = kwargs.get('max_birds', self._max_birds)
        self._max_blocks = kwargs.get('max_blocks', self._max_blocks)
        self._max_tnt = kwargs.get('max_tnt', self._max_tnt)


        self._solver_power = kwargs.get('solver_power', self._solver_power)

        # self._max_enemies = kwargs.get('max_enemies', self._max_enemies)
        # self._max_potions = kwargs.get('max_potions', self._max_potions)
        # self._max_treasures = kwargs.get('max_treasures', self._max_treasures)
        #
        # self._target_col_enemies = kwargs.get('target_col_enemies', self._target_col_enemies)
        self._target_solution = kwargs.get('target_solution', self._target_solution)

        rewards = kwargs.get('rewards')
        if rewards is not None:
            for t in rewards:
                if t in self._rewards:
                    self._rewards[t] = rewards[t]

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

            #run the Unity .exe
            script1 = "D:\\Unity\\2017.3.1f1\\Editor\\Unity.exe -quit -batchmode -buildTarget win64 -projectPath C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds -executeMethod MyEditorScript.PerformBuild"
            script2 = "C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds\\EXE\\DUMMY.exe"

            sb = subprocess.Popen(script1)
            time.sleep(20)

            sb.terminate()
            sb = subprocess.Popen(script2)
            
            time.sleep(7)
            sb.terminate()

            parser = ET.XMLParser(encoding="utf-8")
            output_XML = ET.parse(output_path, parser= parser)

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
            print("PROBABLY FAILED COMPILING .EXE")
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
        map_stats = {
            "empty": calc_certain_tile(map_locations, ["empty"]),
            "pig": calc_certain_tile(map_locations, ["pig"]),
            "TNT": calc_certain_tile(map_locations, ["tnt_corner"]),
            # "birds": calc_certain_tile(map_locations, ["redBird", "blueBird", "yellowBird", "whiteBird", "blackBird"]),

            #REMOVED squareTiny and circles and trianglesfrom the 2 below
            "blocks": calc_certain_tile(
                map_locations, ["rt_corner", "rh_corner", "rs_corner", "rm_corner", "rl_corner", "rf_corner", "tnt_corner"]),
            "regions": calc_num_regions(
                map, map_locations, ["empty", "pig", "rt_corner", "rh_corner", "rs_corner", "rm_corner", "rl_corner", "rf_corner", "tnt_corner"]),
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
        # 3rd value is min; 4th value is the max 
        rewards = {
            "empty": get_range_reward(new_stats["empty"], old_stats["empty"], 1, 1),
            "pig": get_range_reward(new_stats["pig"], old_stats["pig"], 1, self._max_pigs),
            "TNT": get_range_reward(new_stats["TNT"], old_stats["TNT"], 0, self._max_tnt),
            #"birds": get_range_reward(new_stats["birds"], old_stats["birds"], 1, self._max_birds),
            "blocks": get_range_reward(new_stats["blocks"], old_stats["blocks"], 1, self._max_blocks),
            "regions": get_range_reward(new_stats["regions"], old_stats["regions"], 1, 1)
        }

        return rewards["empty"] +\
            rewards["pig"] * self._rewards["pig"]  +\
            rewards["TNT"] +\
            rewards["blocks"] * self._rewards["blocks"]+\
            rewards["regions"]
        # rewards["birds"] * self._rewards["birds"] +\
        return self._get_variety_value(map, 1) + self._test_stability(map) + self._get_pig_potential(map, 1)

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
        percentage = 10
        # return self._test_stability(map) == 1 and len(new_stats["empty"]) * 100 / self._height*self._width*100 < percentage
        return self._test_stability(map) == 1 and new_stats["empty"] * 100 / self._height*self._width*100 < percentage

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
            "TNT": new_stats["TNT"], 
            #"birds": new_stats["birds"],
            "blocks": new_stats["blocks"], 
            "regions": new_stats["regions"] 
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

        return super().render(map)
