
from random import randint
from random import uniform
from math import sqrt, ceil
from copy import deepcopy
import itertools

# blocks number and size
blocks = {'1':[0.84,0.84], '2':[0.85,0.43], '3':[0.43,0.85], '4':[0.43,0.43],
          '5':[0.22,0.22], '6':[0.43,0.22], '7':[0.22,0.43], '8':[0.85,0.22],
          '9':[0.22,0.85], '10':[1.68,0.22], '11':[0.22,1.68],
          '12':[2.06,0.22], '13':[0.22,2.06]}

# blocks number and name
# (blocks 3, 7, 9, 11 and 13) are their respective block names rotated 90 degrees clockwise
block_names = {'1':"SquareHole", '2':"RectFat", '3':"RectFat", '4':"SquareSmall",
               '5':"SquareTiny", '6':"RectTiny", '7':"RectTiny", '8':"RectSmall",
               '9':"RectSmall",'10':"RectMedium",'11':"RectMedium",
               '12':"RectBig",'13':"RectBig"}

# additional objects number and name
additional_objects = {'1':"TriangleHole", '2':"Triangle", '3':"Circle", '4':"CircleSmall"}

# additional objects number and size
additional_object_sizes = {'1':[0.82,0.82],'2':[0.82,0.82],'3':[0.8,0.8],'4':[0.45,0.45]}

# blocks number and probability of being selected
probability_table_blocks = {'1':0.10, '2':0.10, '3':0.10, '4':0.05,
                            '5':0.02, '6':0.05, '7':0.05, '8':0.10,
                            '9':0.05, '10':0.16, '11':0.04,
                            '12':0.16, '13':0.02}

# materials that are available
materials = ["wood", "stone", "ice"]

# bird types number and name
bird_names = {'1':"BirdRed", '2':"BirdBlue", '3':"BirdYellow", '4':"BirdBlack", '5':"BirdWhite"}

# bird types number and probability of being selected
bird_probabilities = {'1':0.35, '2':0.2, '3':0.2, '4':0.15, '5':0.1}

TNT_block_probability = 0.3

pig_size = [0.5,0.5]    # size of pigs

platform_size = [0.62,0.62]     # size of platform sections

edge_buffer = 0.11      # buffer uesd to push edge blocks further into the structure center (increases stability)

absolute_ground = -3.5          # the position of ground within level

max_peaks = 5           # maximum number of peaks a structure can have (up to 5)
min_peak_split = 10     # minimum distance between two peak blocks of structure
max_peak_split = 50     # maximum distance between two peak blocks of structure

minimum_height_gap = 3.5        # y distance min between platforms
platform_distance_buffer = 0.4  # x_distance min between platforms / y_distance min between platforms and ground structures

# defines the levels area (ie. space within which structures/platforms can be placed)
level_width_min = -3.0
level_width_max = 9.0
level_height_min = -2.0         # only used by platforms, ground structures use absolute_ground to determine their lowest point
level_height_max = 6.0

pig_precision = 0.01                # how precise to check for possible pig positions on ground

min_ground_width = 2.5                      # minimum amount of space allocated to ground structure
ground_structure_height_limit = ((level_height_max - minimum_height_gap) - absolute_ground)/1.5    # desired height limit of ground structures

max_attempts = 100                          # number of times to attempt to place a platform before abandoning it





# write level out in desired xml format

def write_level_xml(complete_locations, selected_other, final_pig_positions, final_TNT_positions, final_platforms, number_birds, current_level, restricted_combinations):

    f = open("level-%s.xml" % current_level, "w")

    f.write('<?xml version="1.0" encoding="utf-16"?>\n')
    f.write('<Level width ="2">\n')
    f.write('<Camera x="0" y="2" minWidth="20" maxWidth="30">\n')
    f.write('<Birds>\n')
    for i in range(number_birds):   # bird type is chosen using probability table
        f.write('<Bird type="%s"/>\n' % bird_names[str(choose_item(bird_probabilities))])
    f.write('</Birds>\n')
    f.write('<Slingshot x="-8" y="-2.5">\n')
    f.write('<GameObjects>\n')

    for i in complete_locations:
        material = materials[randint(0,len(materials)-1)]       # material is chosen randomly
        while [material,block_names[str(i[0])]] in restricted_combinations:     # if material if not allowed for block type then pick again
            material = materials[randint(0,len(materials)-1)]
        rotation = 0
        if (i[0] in (3,7,9,11,13)):
            rotation = 90
        f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (block_names[str(i[0])], material, str(i[1]), str(i[2]), str(rotation)))

    for i in selected_other:
        material = materials[randint(0,len(materials)-1)]       # material is chosen randomly
        while [material,additional_objects[str(i[0])]] in restricted_combinations:      # if material if not allowed for block type then pick again
            material = materials[randint(0,len(materials)-1)]
        if i[0] == '2':
            facing = randint(0,1)
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2]), str(facing*90.0)))
        else:
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="0" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2])))

    for i in final_pig_positions:
        f.write('<Pig type="BasicSmall" material="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))

    for i in final_platforms:
        for j in i:
            f.write('<Platform type="Platform" material="" x="%s" y="%s" />\n' % (str(j[0]),str(j[1])))

    for i in final_TNT_positions:
        f.write('<TNT type="" material="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))
        
    f.write('</GameObjects>\n')
    f.write('</Level>\n')

    f.close()




# generate levels using input parameters

backup_probability_table_blocks = deepcopy(probability_table_blocks)
backup_materials = deepcopy(materials)

FILE = open("parameters.txt", 'r')
checker = FILE.readline()
finished_levels = 0
while (checker != ""):
    if checker == "\n":
        checker = FILE.readline()
    else:
        number_levels = int(deepcopy(checker))              # the number of levels to generate
        restricted_combinations = FILE.readline().split(',')      # block type and material combination that are banned from the level
        for i in range(len(restricted_combinations)):
            restricted_combinations[i] = restricted_combinations[i].split()     # if all materials are baned for a block type then do not use that block type
        pig_range = FILE.readline().split(',')
        time_limit = int(FILE.readline())                   # time limit to create the levels, shouldn't be an issue for most generators (approximately an hour for 10 levels)
        checker = FILE.readline()

        restricted_blocks = []                              # block types that cannot be used with any materials
        for key,value in block_names.items():
            completely_restricted = True
            for material in materials:
                if [material,value] not in restricted_combinations:
                    completely_restricted = False
            if completely_restricted == True:
                restricted_blocks.append(value)

        probability_table_blocks = deepcopy(backup_probability_table_blocks)
        trihole_allowed = True
        tri_allowed = True
        cir_allowed = True
        cirsmall_allowed = True
        TNT_allowed = True

        probability_table_blocks = remove_blocks(restricted_blocks)     # remove restricted block types from the structure generation process
        if "TriangleHole" in restricted_blocks:
            trihole_allowed = False
        if "Triangle" in restricted_blocks:
            tri_allowed = False
        if "Circle" in restricted_blocks:
            cir_allowed = False
        if "CircleSmall" in restricted_blocks:
            cirsmall_allowed = False

        for current_level in range(number_levels):

            number_ground_structures = randint(2,4)                     # number of ground structures
            number_platforms = randint(1,3)                             # number of platforms (reduced automatically if not enough space)
            number_pigs = randint(int(pig_range[0]),int(pig_range[1]))  # number of pigs (if set too large then can cause program to infinitely loop)

            if (current_level+finished_levels+4) < 10:
                level_name = "0"+str(current_level+finished_levels+4)
            else:
                level_name = str(current_level+finished_levels+4)
            
            number_ground_structures, complete_locations, final_pig_positions = create_ground_structures()
            number_platforms, final_platforms, platform_centers = create_platforms(number_platforms,complete_locations,final_pig_positions)
            complete_locations, final_pig_positions = create_platform_structures(final_platforms, platform_centers, complete_locations, final_pig_positions)
            final_pig_positions, removed_pigs = remove_unnecessary_pigs(number_pigs)
            final_pig_positions = add_necessary_pigs(number_pigs)
            final_TNT_positions = add_TNT(removed_pigs)
            number_birds = choose_number_birds(final_pig_positions,number_ground_structures,number_platforms)
            possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions = find_additional_block_positions(complete_locations)
            selected_other = add_additional_blocks(possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions)
            write_level_xml(complete_locations, selected_other, final_pig_positions, final_TNT_positions, final_platforms, number_birds, level_name, restricted_combinations)
        finished_levels = finished_levels + number_levels



    
