from gym_pcgrl.envs.reps.representation import Representation
from PIL import Image
from gym import spaces
import numpy as np
import xml.etree.ElementTree as ET
import random
import time

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
The wide representation where the agent can pick the tile position and tile value at each update.
"""
class WideAngryBirdsRepresentation(Representation):
    """
    Initialize all the parameters used by that representation
    """
    def __init__(self):
        super().__init__()

    """
    Resets the current representation

    Parameters:
        width (int): the generated map width
        height (int): the generated map height
        prob (dict(int,float)): the probability distribution of each tile value
    """
    def reset(self, width, height, prob):
        if self._random_start or self._old_map is None:
            self._map = self.gen_random_map(self._random, width, height, prob)
            self._old_map = self._map.copy()
        else:
            self._map = self._old_map.copy()


    """ 
    Gets the action space used by the wide representation

    Parameters:
        width: the current map width
        height: the current map height
        num_tiles: the total number of the tile values

    Returns:
        MultiDiscrete: the action space used by that wide representation which
        consists of the x position, y position, and the tile value
    """
    def get_action_space(self, width, height, num_tiles):
        #return spaces.MultiDiscrete([width, height, num_tiles])
        return spaces.MultiDiscrete([width, height, 8])

    """
    Get the observation space used by the wide representation

    Parameters:
        width: the current map width
        height: the current map height
        num_tiles: the total number of the tile values

    Returns:
        Box: the observation space used by that representation. A 2D array of tile numbers
    """
    def get_observation_space(self, width, height, num_tiles):
        return spaces.Dict({
            "map": spaces.Box(low=0, high=num_tiles-1, dtype=np.uint8, shape=(height, width))
            #"map": spaces.Box(low=0, high=7, dtype=np.uint8, shape=(height, width))
        })

    """
    Get the current representation observation object at the current moment

    Returns:
        observation: the current observation at the current moment. A 2D array of tile numbers
    """
    def get_observation(self):
        return {
            "map": self._map.copy()
        }

    '''
    taken from https://stackoverflow.com/a/65808327
    '''
    def _pretty_print(self,current, parent=None, index=-1, depth=0):
        for i, node in enumerate(current):
            self._pretty_print(node, current, i, depth + 1)
        if parent is not None:
            if index == 0:
                parent.text = '\n' + ('\t' * depth)
            else:
                parent[index - 1].tail = '\n' + ('\t' * depth)
            if index == len(parent) - 1:
                current.tail = '\n' + ('\t' * (depth - 1))

    """ 
    Translate lowermost leftmost corner of block when placed in Python to Unity's center of the block placement
    """
    def MapToUnity(self,typeOfBlock):
        #print("TYPE: ", typeOfBlock)

        #with reference to leftmost corner and objects placed on there 
        if(typeOfBlock == "RectTiny"):
            return (0.215,0.110)
        elif(typeOfBlock == "SquareHole"): 
            return (0.420,0.420)
        elif(typeOfBlock == "RectSmall"): 
            return (0.425,0.110)
        elif(typeOfBlock == "RectMedium"):
            return (.840,0.110)
        elif(typeOfBlock == "RectBig"):
            return (1.025,0.110)
        elif(typeOfBlock == "RectFat"):
            return (0.425,0.220)
    
        elif(typeOfBlock == "TNT"):
            return (0.33,0.33)
        elif(typeOfBlock == "Pig"):
            return (0.235,0.230)
        elif(typeOfBlock == "Platform"):
            return (0.333,0.333)
        else:
            print("ERROR HAS OCCURED WHEN TRANSLATING MAP TO UNITY", typeOfBlock)
            return (0,0)



    """
    Create the XML level to be used 
    """
    def writeXML(self, map):
        blocks_array = []
        tnt_array = []
        pigs_array = []
        platform_array = []
        birds_array = ['BirdRed']
        corners = [rt_corner,rh_corner,rs_corner,rm_corner,rl_corner,rf_corner]
        block_type = ["RectTiny", "SquareHole", "RectSmall", "RectMedium", "RectBig", "RectFat"]
        pigs_num = pig
        tnt_num = tnt_corner
        platform_num = 29
        # map looks like this 
        # top-most row is the top most level
        # bottom-most row is the bottom most level
        # 0,0 is upper left corner 
        x_length = len(map[0])
        y_length = len(map)
        

        #each row is a y value
        #each col is a x value
        for y in range(y_length):
            for x in range(x_length):
                #print("COORDS: ",x,y, "max:", x_length, y_length)
                #to iterate the map, the x value is the first index. the y value is the second index 
                if(map[y][x] in corners):
                    b_type =  block_type[corners.index(map[y][x])]
                    #print("ADDED: ", b_type)
                    blocks_array.append([b_type,y,x])
                elif map[y][x] == pigs_num:
                    pigs_array.append([y,x])
                elif map[y][x] == tnt_num:
                    tnt_array.append([y,x])
                elif map[y][x] == platform_num:
                    platform_array.append([y,x])
        
        #print("BLOCK ARRAY: \n", blocks_array)
        
        
        root = ET.Element('Level')
        root.set('width','2')

        camera = ET.Element('Camera')
        #fill in camera stuff
        camera.set('x', '0')
        camera.set('y', '0')
        camera.set('minWidth', '20')
        camera.set('maxWidth', '25')
        #END
        root.append(camera)

        birds = ET.Element('Birds')
        root.append(birds)
        for each in birds_array:
            temp_bird = ET.SubElement(birds, 'Bird')
            temp_bird.set('type', str(each))
            #fill in temp_bird

            #end
        
        slingshot = ET.Element('Slingshot')
        #fill in slingshot stuff
        slingshot.set('x', '-7')
        slingshot.set('y', '-2.5')
        #END
        root.append(slingshot)

        gameObjects = ET.Element('GameObjects')
        root.append(gameObjects)

        #in the Unity:
        # the floor is y = -3.25
        # the ceiling is y = 2.0 
        # HEIGHT is 5.25
        
        # the leftmost wall is x = -4
        # the rightmost wall is x = 11
        # WIDTH is 15

        #in the map:
        # width = 36
        # height = 21

        #subtract to mirror the image as first row in the map is the top-most row in the level
        map_width = 15
        map_height = 5.25
        #this is to account that blocks can go beyond x=0 or y=0 as origin is not the corner of the level
        
        x_max_from_origin = -5
        y_max_from_origin = -3.75

        #conversions to divide by to get map to unity
        x_conv = 1/ (.25 * 2)
        y_conv = 1 / (.125 * 2)

        x_threshold = 0#.0005
        y_threshold = .0005
        for each in blocks_array:
            temp_block = ET.SubElement(gameObjects, 'Block')

            temp_block.set('type', str(each[0]))
            temp_block.set('material', 'wood')
            #HAVE TO ACCOUNT THAT YOU PLACE THE BLOCK BASED ON THE CENTER OF THE BLOCK IN UNITY
            #MapToUnity(typeOfBlock) will return how to move leftmost lowermost corner to center of the block
            
            xy_diff = self.MapToUnity(str(each[0]))
            
            x_diff = x_max_from_origin + xy_diff[0]
            y_diff = y_max_from_origin + xy_diff[1]

            temp_block.set('x', str(each[2]/x_conv + x_diff + x_threshold))
            temp_block.set('y', str(map_height - each[1]/y_conv + y_diff + y_threshold))

            #print(str(each[0]), xy_diff[0], xy_diff[1], each[2]/2 - x_diff, map_height - each[1]/4 - y_diff)
            #print(map_height, each[1]/4,y_diff, "y_diff: ",3.25+xy_diff[1])
            temp_block.set('rotation', "0")

        for each in pigs_array:
            #HAVE TO ACCOUNT THAT YOU PLACE THE BLOCK BASED ON THE CENTER OF THE BLOCK IN UNITY
            #MapToUnity(typeOfBlock) will return how to move leftmost lowermost corner to center of the block
            xy_diff = self.MapToUnity("Pig")

            x_diff = x_max_from_origin + xy_diff[0]
            y_diff = y_max_from_origin + xy_diff[1]

            temp_pig = ET.SubElement(gameObjects, 'Pig')
            temp_pig.set('type', 'BasicSmall')
            temp_pig.set('x', str(each[1]/x_conv + x_diff + x_threshold))
            temp_pig.set('y', str(map_height - each[0]/y_conv+ y_diff + y_threshold))
            temp_pig.set('rotation', '0')

        for each in tnt_array:
            #HAVE TO ACCOUNT THAT YOU PLACE THE BLOCK BASED ON THE CENTER OF THE BLOCK IN UNITY
            #MapToUnity(typeOfBlock) will return how to move leftmost lowermost corner to center of the block
            xy_diff = self.MapToUnity("TNT")
            
            x_diff = x_max_from_origin + xy_diff[0]
            y_diff = y_max_from_origin + xy_diff[1]

            temp_tnt = ET.SubElement(gameObjects, 'TNT')
            temp_tnt .set('x', str(each[1]/x_conv + x_diff + x_threshold))
            temp_tnt .set('y', str(map_height - each[0]/y_conv + y_diff + y_threshold))
            temp_tnt .set('rotation', '0')

        
        '''
        for each in platform_array:
            #<Platform type="Platform"  x="2"  y="-1" scaleX="5.5" scaleY="8"/>
            #xy_diff = self.MapToUnity("Platform")

            #x_diff = x_max_from_origin + xy_diff[0]
            #y_diff = y_max_from_origin + xy_diff[1]

            temp_platform = ET.SubElement(gameObjects, 'Platform')
            temp_platform.set('x', str(each[1]/x_conv + x_diff + x_threshold))
            temp_platform.set('y', str(map_height - each[0]/y_conv + y_diff + y_threshold))
            temp_platform.set('scaleX', '5.5')
            temp_platform.set('scaleY', '8')
        '''



        self._pretty_print(root) #make the XML prettier
        tree = ET.ElementTree(root)
        #path = "C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds\\Assets\\StreamingAssets\\Levels\\level-6.xml"
        path = "C:\\Users\\nekonek0\\Desktop\\Computer_Science\\GitHub_repos\\science-birds\\Assets\\Resources\\Levels\\level-1.xml"
        
        with open(path, 'wb') as files:
            files.write(b'<?xml version="1.0" encoding="UTF-16"?>\n')
            tree.write(files,xml_declaration=False,encoding='utf-8')

    """
    this will try to remove any "phantom" corner blocks that are not filled in for some reason 
    """

    def fix(self, map):
        x_length = len(map[0])
        y_length = len(map)
        #each row is a y value
        #each col is a x value
        for y in range(y_length):
            for x in range(x_length):
                #append the coords that are corners and have nothing near them 
                if(map[y][x] >= 0 and map[y][x] <= 6):
                    #rt
                    if map[y][x]  == rt_corner:
                        continue 
                    #rh
                    elif map[y][x]  == rh_corner:
                        #subtract to go upwards the row/height
                        if map[y-1][x] != rh_l or\
                            map[y-2][x] != rh_l or\
                            map[y-3][x] != rh_ul or\
                            map[y][x+1] != rh_lr or\
                            map[y-1][x+1] != rh_r or\
                            map[y-2][x+1] != rh_r or\
                            map[y-3][x+1] != rh_ur:
                                map[y][x] = empty
                    #rs
                    elif map[y][x]  == rs_corner:
                        if map[y][x+1] != rs_o1:
                            map[y][x] = empty
                        #map[x+1][y] = 8
                    #rm
                    elif map[y][x]  == rm_corner:
                        if map[y][x+1] != rm_o1 or\
                            map[y][x+2] != rm_o2 or\
                            map[y][x+3] != rm_o3:
                                map[y][x] = empty
                    #rl
                    elif map[y][x]  == rl_corner:
                        if map[y][x+1] != rl_o1 or\
                            map[y][x+2] != rl_o2 or\
                            map[y][x+3] != rl_o3 or\
                            map[y][x+4] != rl_o4:
                                map[y][x] = empty
                    #rf
                    elif map[y][x]  == rf_corner:
                        if map[y-1][x] != rf_ul or\
                            map[y][x+1] != rf_lr or\
                            map[y-1][x+1] != rf_ur:
                                map[y][x] = empty
                    #tnt
                    elif map[y][x]  == tnt_corner:
                        if map[y-1][x] != tnt_ul or\
                            map[y][x+1] != tnt_lr or\
                            map[y-1][x+1] != tnt_ur:
                                map[y][x] = empty
                    #error
                    else:
                        print("ERROR in FIX", map[y][x] )

    """
    Update the wide representation with the input action

    Parameters:
        action: an action that is used to advance the environment (same as action space)

    Returns:
        boolean: True if the action change the map, False if nothing changed
    """
    def update(self, action):
        change = [0,1][self._map[action[1]][action[0]] != action[2]]
        #only update on an empty.pig, or corner of a block/tnt

        #initial clean out the block or set it to something if it is empty 
        if(self._map[action[1]][action[0]] == empty):
            self._map[action[1]][action[0]] = action[2]
        #start with pig or tnt_corner for now
        #elif (self._map[action[1]][action[0]] == pig or self._map[action[1]][action[0]] == tnt_corner):
        elif (self._map[action[1]][action[0]] < empty):
            #keep track of the block that is to be changed
            curr_block_num = self._map[action[1]][action[0]]
            #erase pig 
            if(self._map[action[1]][action[0]] == pig):
                pass
            #erase tnt_corner
            elif(self._map[action[1]][action[0]] == tnt_corner):
                #print(self._map)
                #print("attempt remove tnt_corner at ", action[1], action[0])
                #remove the tnt_corner 
                #remove the TNT_corner on the map
                try:
                    #print("curr element at: ", action[1], action[0], " is ", self._map[action[1]][action[0]])
                    #print("curr element at: ", action[1] - 1, action[0], " is ", self._map[action[1] - 1][action[0]])
                    #print("curr element at: ", action[1], action[0] + 1, " is ", self._map[action[1]][action[0] + 1])
                    #print("curr element at: ", action[1] - 1, action[0] + 1, " is ", self._map[action[1] - 1][action[0] + 1])
                    #print(action[1], action[0])
                    if self._map[action[1]][action[0]] == tnt_corner:
                        #print("removed tc")
                        self._map[action[1]][action[0]] = empty
                    if self._map[action[1] - 1][action[0]] == tnt_ul:
                        #print("removed t_ul")
                        self._map[action[1] - 1][action[0]] = empty
                    if self._map[action[1]][action[0] + 1] == tnt_lr:
                        #print("removed t_lr")
                        self._map[action[1]][action[0] + 1] = empty 
                    if self._map[action[1] - 1][action[0] + 1] == tnt_ur:
                        #print("removed t_ur")
                        self._map[action[1] - 1][action[0] + 1] = empty
                #idk why there is sometimes a phantom tnt_corner at the edge of the map that is not rendered
                except:
                    print("===================")
                    print("phantom tnt_corner ")
                    print("===================")
                    pass
            #erase rf_corner
            elif(self._map[action[1]][action[0]] == rf_corner):
                try:

                    if self._map[action[1]][action[0]] == rf_corner:
                        #print("removed rf_c")
                        self._map[action[1]][action[0]] = empty
                    if self._map[action[1] - 1][action[0]] == rf_ul:
                        #print("removed rf_ul")
                        self._map[action[1] - 1][action[0]] = empty
                    if self._map[action[1]][action[0] + 1] == rf_lr:
                        #print("removed rf_lr")
                        self._map[action[1]][action[0] + 1] = empty 
                    if self._map[action[1] - 1][action[0] + 1] == rf_ur:
                        #print("removed rf_ur")
                        self._map[action[1] - 1][action[0] + 1] = empty
                except:
                    print("===================")
                    print("phantom rf_corner ")
                    print("===================")
                    pass
            #erase rh_corner
            elif(self._map[action[1]][action[0]] == rh_corner):
                try:

                    if self._map[action[1]][action[0]] == rh_corner:
                        #print("removed rf_c")
                        self._map[action[1]][action[0]] = empty
                    if self._map[action[1] - 1][action[0]] == rh_l:
                        #print("removed rh_l")
                        self._map[action[1] - 1][action[0]] = empty
                    if self._map[action[1] - 2][action[0]] == rh_l:
                        #print("removed rh_l")
                        self._map[action[1] - 2][action[0]] = empty
                    if self._map[action[1] - 3][action[0]] == rh_ul:
                        #print("removed rh_ul")
                        self._map[action[1] - 3][action[0]] = empty
                    
                    if self._map[action[1]][action[0] + 1] == rh_lr:
                        #print("removed rh_lr")
                        self._map[action[1]][action[0] + 1] = empty
                    if self._map[action[1] - 1][action[0] + 1] == rh_r:
                        #print("removed rh_r")
                        self._map[action[1] - 1][action[0] + 1] = empty
                    if self._map[action[1] - 2][action[0] + 1] == rh_r:
                        #print("removed rh_r")
                        self._map[action[1] - 2][action[0] + 1] = empty
                    if self._map[action[1] - 3][action[0] + 1] == rh_ur:
                        #print("removed rh_ur")
                        self._map[action[1] - 3][action[0] + 1] = empty
                except:
                    print("===================")
                    print("phantom rh_corner ")
                    print("===================")
                    pass
            #erase rs_corner
            elif(self._map[action[1]][action[0]] == rs_corner):
                try:

                    if self._map[action[1]][action[0]] == rs_corner:
                        #print("removed rs_c")
                        self._map[action[1]][action[0]] = empty
                    if self._map[action[1]][action[0] + 1] == rs_o1:
                        #print("removed rs_o1")
                        self._map[action[1]][action[0] + 1] = empty
                except:
                    print("===================")
                    print("phantom rs_corner ")
                    print("===================")
                    pass
            #erase rm_corner
            elif(self._map[action[1]][action[0]] == rm_corner):
                try:

                    if self._map[action[1]][action[0]] == rm_corner:
                        #print("removed rm_c")
                        self._map[action[1]][action[0]] = empty
                    if self._map[action[1]][action[0] + 1] == rm_o1:
                        #print("removed rm_o1")
                        self._map[action[1]][action[0] + 1] = empty
                    if self._map[action[1]][action[0] + 2] == rm_o2:
                        #print("removed rm_o2")
                        self._map[action[1]][action[0] + 2] = empty
                    if self._map[action[1]][action[0] + 3] == rm_o3:
                        #print("removed rm_o3")
                        self._map[action[1]][action[0] + 3] = empty
                except:
                    print("===================")
                    print("phantom rm_corner ")
                    print("===================")
                    pass
            #erase rl_corner
            elif(self._map[action[1]][action[0]] == rl_corner):
                try:

                    if self._map[action[1]][action[0]] == rl_corner:
                        #print("removed rl_c")
                        self._map[action[1]][action[0]] = empty
                    if self._map[action[1]][action[0] + 1] == rl_o1:
                        #print("removed rl_o1")
                        self._map[action[1]][action[0] + 1] = empty
                    if self._map[action[1]][action[0] + 2] == rl_o2:
                        #print("removed rl_o2")
                        self._map[action[1]][action[0] + 2] = empty
                    if self._map[action[1]][action[0] + 3] == rl_o3:
                        #print("removed rl_o3")
                        self._map[action[1]][action[0] + 3] = empty
                    if self._map[action[1]][action[0] + 4] == rl_o4:
                        #print("removed rl_o4")
                        self._map[action[1]][action[0] + 4] = empty
                except:
                    print("===================")
                    print("phantom rl_corner ")
                    print("===================")
                    pass
            
            #now update the block
            block_array = ["rt_corner", "rh_corner", "rs_corner", "rm_corner", "rl_corner", "rf_corner", "tnt_corner", "pig", "empty"]
            
            #print("curr_block_num: ", curr_block_num)
            curr_block_name = block_array[curr_block_num]


            #print(curr_block_name, "update start", action[2])
            #if attempt to replace with a tnt_corner, does an illegal block (block that isnt a corner), or the new block to replace has a collission, 
            if(action[2] == curr_block_num or (action[2] > empty) or self.check_collision(action[2], action[1], action[0], self._map)):
                blocks_by_size = [rh_corner,rl_corner,rm_corner,rf_corner,rs_corner,empty]
                if curr_block_num in blocks_by_size:
                    blocks_by_size.remove(curr_block_num)
                for each in blocks_by_size:
                    #print("Attempt replace tnt_corner with ", each)
                    if(not self.check_collision(each, action[1], action[0], self._map)):
                        self._map[action[1]][action[0]] = each
                        break
            else:
                #print("Initial replace tnt_corner good with ", action[2])
                self._map[action[1]][action[0]] = action[2]


        #print("CURRENT MAP:\n", self._map)
        self.writeXML(self._map)
        self.fillin(self._map)
        self.fix(self._map)

        return change, action[0], action[1]
    
    """
    check with collisions with other blocks and with the map size 
    """

    def check_collision(self,type_block,y,x,map):
        # map looks like this 
        # top-most row is the top most level
        # bottom-most row is the bottom most level
        x_length = len(map[0]) - 1 #subtract one since this is supposed to represent possible indexes of the map
        y_length = len(map)
        #print("CURR_COORD: ",x,y)
        #rt
        if type_block == rt_corner or type_block == empty or type_block == pig:
            return False
        #rh
        elif type_block == rh_corner:
            #check if collide with map
            if(x >= x_length or y < 3):
                return True
            #if the block is filled correctly, just exit out
            elif(map[y-1][x] == rh_l and map[y][x+1] == rh_lr and 
                map[y-2][x] == rh_l and map[y-1][x+1] == rh_r and 
                map[y-3][x] == rh_ul and map[y-2][x+1] == rh_r and 
                                    map[y-3][x+1] == rh_ur ):
                    return False
            #check if adjacent block is not empty
            elif(map[y-1][x] != empty or map[y][x+1] != empty or 
                map[y-2][x] != empty or map[y-1][x+1] != empty or 
                map[y-3][x] != empty or map[y-2][x+1] != empty or 
                                    map[y-3][x+1] != empty ):
                    return True
            return False
        #rs
        elif type_block == rs_corner:
            #check if collide with map
            if(x >= x_length):
                return True
            #if the block is filled correctly, just exit out
            elif(map[y][x+1] == rs_o1 ):
                    return False
            #check if adjacent block is not empty
            elif(map[y][x+1] != empty ):
                return True
            return False
        #rm
        elif type_block == rm_corner:
            #check if collide with map
            if(x >= x_length - 2):
                return True
            #if the block is filled correctly, just exit out
            elif(map[y][x+1] ==rm_o1 or map[y][x+2] == rm_o2 or map[y][x+3] == rm_o3 ):
                    return False
            #check if adjacent block is not empty
            elif(map[y][x+1] != empty or map[y][x+2] != empty or map[y][x+3] != empty ):
                return True
            return False
        #rl
        elif type_block == rl_corner:
            #check if collide with map
            if(x >= x_length - 3):
                return True
            #if the block is filled correctly, just exit out
            elif(map[y][x+1] ==rl_o1 or map[y][x+2] == rl_o2 or map[y][x+3] == rl_o3 and map[y][x+4] == rl_o4):
                    return False
            #check if adjacent block is not empty
            elif(map[y][x+1] != empty or map[y][x+2] != empty or map[y][x+3] != empty or map[y][x+4] != empty):
                return True
            return False
        #rf
        elif type_block == rf_corner:
            #check if collide with map
            if(x >= x_length or y < 1):
                return True
            #if the block is filled correctly, just exit out
            elif(map[y-1][x] == rf_ul or map[y][x+1] == rf_lr or 
                                    map[y-1][x+1] == rf_ur):
                    return False
            #check if adjacent block is not empty
            elif(map[y-1][x] != empty or map[y][x+1] != empty or 
                                    map[y-1][x+1] != empty):
                return True
            return False
        #tnt
        elif type_block == tnt_corner:
            #check if collide with map
            if(x >= x_length or y < 1):
                return True
            #if the block is filled correctly, just exit out
            elif(map[y-1][x] == tnt_ul or map[y][x+1] == tnt_lr or 
                                    map[y-1][x+1] == tnt_ur):
                    return False
            #check if adjacent block is not empty
            elif(map[y-1][x] != empty or map[y][x+1] != empty or 
                                    map[y-1][x+1] != empty):
                return True
            return False
        else:
            print("ERROR IN CC", type_block)

    def fillin(self,map):
        coords = []

        # map looks like this 
        # top-most row is the top most level
        # bottom-most row is the bottom most level
        # 0,0 is upper left corner 
        x_length = len(map[0])
        y_length = len(map)

        #each row is a y value
        #each col is a x value
        for y in range(y_length):
            for x in range(x_length):
                #print("COORDS: ",x,y, "max:", x_length, y_length)
                #to iterate the map, the x value is the first index. the y value is the second index 
                if(map[y][x] >= 0 and map[y][x] <= 6):
                    coords.append([map[y][x],y,x])
        
        #print("COORDS: \n", coords)

        for each in coords:
            #each[0] is type
            #each[1] is row in the map (so height)
            #each[2] is the col in the map (so width)
            if(self.check_collision(each[0],each[1],each[2],map)):
                #just remove the block if it collides with something
                #print("REMOVED BLOCK")
                map[each[1]][each[2]] = empty
                continue 
            #if there is no collission, fill it in
            else:
                y = each[1]
                x = each[2]
                #print("FILL-IN @", y,x, "BLOCK TYPE: ", each[0])
                #rt
                if each[0] == rt_corner:
                    continue 
                #rh
                elif each[0] == rh_corner:
                    #subtract to go upwards the row/height
                    map[y-1][x] = rh_l
                    map[y-2][x] = rh_l
                    map[y-3][x] = rh_ul 

                    #x stay + to move to the right
                    map[y][x+1] = rh_lr
                    map[y-1][x+1] = rh_r 
                    map[y-2][x+1] = rh_r
                    map[y-3][x+1] = rh_ur

                #rs
                elif each[0] == rs_corner:
                    map[y][x+1] = rs_o1
                    #map[x+1][y] = 8
                #rm
                elif each[0] == rm_corner:
                    map[y][x+1] = rm_o1
                    map[y][x+2] = rm_o2
                    map[y][x+3] = rm_o3

                #rl
                elif each[0] == rl_corner:
                    map[y][x+1] = rl_o1
                    map[y][x+2] = rl_o2
                    map[y][x+3] = rl_o3
                    map[y][x+4] = rl_o4

                #rf
                elif each[0] == rf_corner:
                    map[y-1][x] = rf_ul
                    map[y][x+1] = rf_lr
                    map[y-1][x+1] = rf_ur

                #tnt
                elif each[0] == tnt_corner:
                    map[y-1][x] = tnt_ul
                    map[y][x+1] = tnt_lr
                    map[y-1][x+1] = tnt_ur

                #error
                else:
                    print("ERROR in FI", each[0])
        
        #print(map)
        return map


    """
    Override gen_random_map
    """
    def gen_random_map(self,random, width, height, prob):
        #print("DOING IT HERE")
        #print("MAP VALUES", list(prob.values()))
        #print(sum(list(prob.values())))

        p_list= list(prob.values())
        #TEMPORARY FIX 
        if(sum(list(prob.values())) <= 1.0):
            #print("HERE: ", p_list[0])
            p_list[0] += 1.0 - sum(list(prob.values()))
        new_map = random.choice(list(prob.keys()),size=(height,width),p=p_list).astype(np.uint8)

        #FILL IN THE BLOCKS
        #print(map)
        return self.fillin(new_map)
