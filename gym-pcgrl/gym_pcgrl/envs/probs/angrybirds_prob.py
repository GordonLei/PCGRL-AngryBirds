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
        # the ceiling is y = 9.0 but you will probably only need around y = 5.0
        
        # the leftmost wall is x = -7.00
        # the rightmost wall is x = 14.00

        #a platform is around .5 radius so it's a 1x1 block

        # x is 21 wide so you probably want around 42 for width
        self._width = 42
        # y is around 12.25 tall so 24.50 for height. round it to 25
        self._height = 25

        # a dictionary that contains all of the possible tile types
        tiles = self.get_tile_types()

        # probably table of how likely a certain tile would be generated for initial state
        self._prob = {

            "empty":0.69,
            "solid":0.00,
            "squareHole":0.04,
            "rectFat":0.04,
            "squareSmall":0.02,
            "squareTiny":0.02,
            "rectTiny":0.02, 
            "rectSmall":0.02,
            "rectMedium":0.02, 
            "rectBig":0.06,
            "triangleHole":0.01,
            "triangle":0.01,
            "circle":0.01,
            "circleSmall":0.01,
            "TNT":0.01,
            "pig":0.01,
            # "redBird":0.002,
            # "blueBird":0.002,
            # "yellowBird":0.002,
            # "whiteBird":0.002,
            # "blackBird":0.002,
        }

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
            "empty",
            "solid",
            "squareHole", 
            "rectFat", 
            "squareSmall", 
            "squareTiny",
            "rectTiny", 
            "rectSmall", 
            "rectMedium", 
            "rectBig",
            "triangleHole", 
            "triangle", 
            "circle", 
            "circleSmall",
            "TNT", 
            "pig",
            # "redBird",
            # "blueBird",
            # "yellowBird",
            # "whiteBird",
            # "blackBird"
        ]
            #{
            # '0': "Empty",
            #  '1': "SquareHole", '2': "RectFat", '3': "RectFat", '4': "SquareSmall",
            # '5': "SquareTiny", '6': "RectTiny", '7': "RectTiny", '8': "RectSmall",
            # '9': "RectSmall", '10': "RectMedium", '11': "RectMedium",
            # '12': "RectBig", '13': "RectBig", '14': "pig", '15': "TNT"

            # '1': "SquareHole" , '2': "RectFat", '3': "SquareSmall", '4':"SquareTiny",
            # '5': "RectTiny", '6': "RectSmall", '7': "RectMedium", '8': "RectBig",
            # '9': "TriangleHole", '10': "Triangle" , '11': "Circle", '12': "CircleSmall",
            # '13': "TNT", '14': "Pig"

            #}
        
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
        
        parser = ET.XMLParser(encoding="utf-8")
        input_XML = ET.parse(input_path, parser= parser)

        #run the Unity .exe
        script = "C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds\\EXE\\DUMMY.exe"

        #os.system(script)
        #sts = subprocess.call(script, shell=True)
        sb = subprocess.Popen(script)


        time.sleep(10)

        sb.terminate()
        #os.system("TASKKILL /F /IM C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds\\EXE\\DUMMY.exe")



        parser = ET.XMLParser(encoding="utf-8")
        output_XML = ET.parse(output_path, parser= parser)

        input_root = input_XML.getroot()
        output_root = output_XML.getroot()
        # [1] is <Birds> tag 
        # [5] is <GameObjects depending on number of birds>. so use .tag to find GameObjects Tag 
        # input and output file look the same 

        GO_input_index = 0 
        GO_output_index = 0

        while(input_root[1][GO_input_index].tag != "GameObjects"):
            GO_input_index += 1
            #print("INC 1")
        while(output_root[1][GO_output_index].tag != "GameObjects"):
            GO_output_index += 1
            #print("INC 2")

        #print(len(input_root[1][GO_input_index]))

        #this means that something changed before reaching GameObjects
        if(GO_input_index != GO_output_index):
            return 0 
        for i in range(len (input_root[1][GO_input_index] )):
            input_obj = input_root[1][GO_input_index][i].attrib
            output_obj = output_root[1][GO_input_index][i].attrib
            #print(input_obj)
            if(input_obj['x'] != output_obj['x'] or input_obj['y'] != output_obj['y']):
                return 0 
            else:
                print("COMPARED")
        #print(input_root[1][5][0].attrib)

        # 1 means this is stable? 
        return 1

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
            "TNT": calc_certain_tile(map_locations, ["TNT"]),
            # "birds": calc_certain_tile(map_locations, ["redBird", "blueBird", "yellowBird", "whiteBird", "blackBird"]),
            "blocks": calc_certain_tile(map_locations, ["squareHole", "rectFat", "squareSmall", "squareTiny","rectTiny", "rectSmall", "rectMedium", "rectBig","triangleHole", "triangle", "circle", "circleSmall"]),
            "regions": calc_num_regions(map, map_locations, ["empty", "pig", "squareHole", "rectFat", "squareSmall", "squareTiny","rectTiny", "rectSmall", "rectMedium", "rectBig","triangleHole", "triangle", "circle", "circleSmall"]),
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

            '''
            '1': "SquareHole" , '2': "RectFat", '3': "SquareSmall", '4':"SquareTiny",
                '5': "RectTiny", '6': "RectSmall", '7': "RectMedium", '8': "RectBig",
                '9': "TriangleHole", '10': "Triangle" , '11': "Circle", '12': "CircleSmall",
                '13': "TNT", '14': "Pig"
            '''

            self._graphics = {
                "empty": Image.open(os.path.dirname(__file__) + "/angrybirds/empty.png").convert('RGBA'),
                "solid": Image.open(os.path.dirname(__file__) + "/angrybirds/solid.png").convert('RGBA'),
                "squareHole": Image.open(os.path.dirname(__file__) + "/angrybirds/square_hole.png").convert('RGBA'),
                "rectFat": Image.open(os.path.dirname(__file__) + "/angrybirds/rect_fat.png").convert('RGBA'),
                "squareSmall": Image.open(os.path.dirname(__file__) + "/angrybirds/square_small.png").convert('RGBA'),
                "squareTiny": Image.open(os.path.dirname(__file__) + "/angrybirds/square_tiny.png").convert('RGBA'),
                "rectTiny": Image.open(os.path.dirname(__file__) + "/angrybirds/rect_tiny.png").convert('RGBA'),
                "rectSmall": Image.open(os.path.dirname(__file__) + "/angrybirds/rect_small.png").convert('RGBA'),
                "rectMedium": Image.open(os.path.dirname(__file__) + "/angrybirds/rect_medium.png").convert('RGBA'),
                "rectBig": Image.open(os.path.dirname(__file__) + "/angrybirds/rect_big.png").convert('RGBA'),
                "triangleHole": Image.open(os.path.dirname(__file__) + "/angrybirds/triangle_hole.png").convert('RGBA'),
                "triangle": Image.open(os.path.dirname(__file__) + "/angrybirds/triangle.png").convert('RGBA'),
                "circle": Image.open(os.path.dirname(__file__) + "/angrybirds/circle.png").convert('RGBA'),
                "circleSmall": Image.open(os.path.dirname(__file__) + "/angrybirds/circle_small.png").convert('RGBA'),
                "TNT": Image.open(os.path.dirname(__file__) + "/angrybirds/tnt.png").convert('RGBA'),
                "pig": Image.open(os.path.dirname(__file__) + "/angrybirds/pig.png").convert('RGBA'),
                # "redBird": Image.open(os.path.dirname(__file__) + "/angrybirds/redBird.png").convert('RGBA'),
                # "blueBird": Image.open(os.path.dirname(__file__) + "/angrybirds/blueBird.png").convert('RGBA'),
                # "yellowBird": Image.open(os.path.dirname(__file__) + "/angrybirds/yellowBird.png").convert('RGBA'),
                # "whiteBird": Image.open(os.path.dirname(__file__) + "/angrybirds/whiteBird.png").convert('RGBA'),
                # "blackBird": Image.open(os.path.dirname(__file__) + "/angrybirds/blackBird.png").convert('RGBA'),
            
            }


            '''
            print(self._graphics["empty"].size)
            print(self._graphics["solid"].size)
            print(self._graphics["squareHole"].size) 
            print(self._graphics["rectFat"].size)
            print(self._graphics["squareSmall"].size) 
            print(self._graphics["squareTiny"].size)
            print(self._graphics["rectTiny"].size)
            print(self._graphics["rectSmall"].size) 
            print(self._graphics["rectMedium"].size) 
            print(self._graphics["rectBig"].size)
            print(self._graphics["triangleHole"].size) 
            print(self._graphics["triangle"].size)
            print(self._graphics["circle"].size)
            print(self._graphics["circleSmall"].size)
            print(self._graphics["TNT"].size)
            print(self._graphics["pig"].size)
            print(self._graphics["redBird"].size)
            print(self._graphics["blueBird"].size)
            print(self._graphics["yellowBird"].size)
            print(self._graphics["whiteBird"].size)
            print(self._graphics["blackBird"].size)
            '''
        return super().render(map)
