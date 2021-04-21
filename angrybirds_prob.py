import os
import numpy as np
from PIL import Image
from problem import Problem
from helper import *


class AngryBirdsProblem(Problem):
    def __init__(self):
        super().__init__()

        # self._width = 16
        # self._height = 10

        # a dictionary that contains all of the possible tile types
        tiles = self.get_tile_types()

        # probably table of how likely a certain tile would be generated for initial state
        self._prob = []

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
        return {
                 '0': "Empty",
               #  '1': "SquareHole", '2': "RectFat", '3': "RectFat", '4': "SquareSmall",
               # '5': "SquareTiny", '6': "RectTiny", '7': "RectTiny", '8': "RectSmall",
               # '9': "RectSmall", '10': "RectMedium", '11': "RectMedium",
               # '12': "RectBig", '13': "RectBig", '14': "pig", '15': "TNT"

                '1': "SquareHole" , '2': "RectFat", '3': "SquareSmall", '4':"SquareTiny",
                '5': "RectTiny", '6': "RectSmall", '7': "RectMedium", '8': "RectBig",
                '9': "TriangleHole", '10': "Triangle" , '11': "Circle", '12': "CircleSmall",
                '13': "TNT", '14': "Pig"

                }

    """
        Private function that test if current map is stable.
        Simulates the level to test for stability. 
        Parameters:
            map (string[][]): the input level to run the game on
        Returns:
            int: 0 if not stable, 1 if stable
    """

    def _test_stability(self, map):
        return 0

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
            "Empty": calc_certain_tile(map_locations, ["Empty"]),
            "Pig": calc_certain_tile(map_locations, ["Pig"]),
            "TNT": calc_certain_tile(map_locations, ["TNT"]),

        }

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
    def get_reward(self, map, new_stats, old_stats):
        return _get_variety_value(map, 1) + _test_stability(map) + _get_pig_potential(map, 1)

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
        return _test_stability(map) == 1 and len(new_stats["empty"]) * 100 / height*width*100 < percentage

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
        Get an image on how the map will look like for a specific map

        Parameters:
            map (string[][]): the current game map

        Returns:
            Image: a pillow image on how the map will look like using the binary graphics
        """

    def render(self, map):
        if self._graphics == None:
            self._graphics = {

            }
        return super().render(map)
