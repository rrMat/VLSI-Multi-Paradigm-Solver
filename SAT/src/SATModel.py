from z3 import *
import math
import numpy as np 
import time

import SAT.src.sat_utils as sat_utils


class SATModel:

    NAME = 'SATModel'

    def __init__(self, plate_width, n_chips, chips_widths, chips_heights, rotation, symmetry_breaking, encoding_type, time_available, interrupt):
        self.plate_width = plate_width
        self.n_chips = n_chips
        self.chips_widths = chips_widths
        self.chips_heights = chips_heights
        self.rotation = rotation
        self.symmetry_breaking = symmetry_breaking  
        self.encoding_type = encoding_type
        self.time_available = time_available
        self.interrupt = interrupt

        self.min_height = math.ceil(np.sum(chips_widths * chips_heights) / plate_width)
        self.max_height = np.sum([min(h, w) for h, w in zip(chips_heights, chips_widths)]) if rotation else np.sum(chips_heights)

        # Literals containers
        self.plate = []
        if self.rotation:
            self.rotated = [Bool(f"rotated_{i}") for i in range(self.n_chips)]

        # Init
        self.solved = False
        self.plate_height = 0
        self.solving_time = 0



    def solve(self, _, returned_values):
        returned_values['is_solved'] = False
                
        # Constraint initialization
        overlapping_check = []
        placing_check = None

        # Available positions of chips
        chip_places = {k: [] for k in range(self.n_chips)}
        if self.rotation:
            chip_rotated_places = {k: [] for k in range(self.n_chips)}
        
        start_time = time.time()
        self.min_height = self.min_height  + 2
        for new_height in range(self.min_height, self.max_height):
            print('Height: ', new_height)

            # Defining literals
            self.plate += [[[Bool(f"plate_{k}_{j}_{i}") for i in range(self.n_chips)] for j in range(self.plate_width)] for k in range(self.plate_height, new_height)]

            # Defining available positions for each chip
            for k in range(self.n_chips):
                # Define all the possible positions of each chipset with literals
                # *. Without rotation
                for x in range(self.plate_width - self.chips_widths[k] + 1):
                    for y in range(new_height - 1, self.chips_heights[k] - 2, -1):
                        chip_places[k].append(sat_utils.all_true([self.plate[y - slide_y][x + slide_x][k] for slide_x in range(self.chips_widths[k]) 
                                                                                                          for slide_y in range(self.chips_heights[k])]))
                # *. With rotation (if needed)
                if self.rotation:
                    for x in range(self.plate_width - self.chips_heights[k] + 1):
                        for y in range(new_height - 1,  self.chips_widths[k] -2, -1):
                            chip_rotated_places[k].append(sat_utils.all_true([self.plate[y + slide_y][x + slide_x][k] for slide_x in range(self.chips_heights[k]) 
                                                                                                                      for slide_y in range(self.chips_widths[k])]))

            # Defining constraints:
            # - 1° constraint 
            overlapping_check += [sat_utils.at_most_one[self.encoding_type](self.plate[i][j]) for i in range(self.plate_height, new_height) for j in range(self.plate_width)]
            # - 2° constraint
            placing_check = []
            for k in range(self.n_chips):  
                if not self.rotation:
                    placing_check = placing_check + [sat_utils.exactly_one[self.encoding_type](chip_places[k])]
                else:
                    placing_check = placing_check + [sat_utils.exactly_one[self.encoding_type]([
                        And([sat_utils.exactly_one[self.encoding_type](chip_places[k])] + [Not(self.rotated[k])]),
                        And([sat_utils.exactly_one[self.encoding_type](chip_rotated_places[k])] + [self.rotated[k]])
                    ])]
            
            # Solver initialization
            solver = Solver()

            # Add constraints
            solver.add(overlapping_check)
            solver.add(placing_check)

            # We have so created a model with a height increased by one respect to before...
            self.plate_height = new_height

            # Solve the model
            if solver.check() == sat:
                returned_values['solving_time'] = time.time() - start_time
                returned_values['is_solved'] = True
                
                pos_x, pos_y, chips_w_a, chips_h_a, self.plate_width, self.min_height, self.plate_height, rotation, self.solving_time = self.get_solution_solved_parsed(solver.model())

                returned_values['pos_x'] = pos_x
                returned_values['pos_y'] = pos_y
                returned_values['chips_w_a'] = chips_w_a
                returned_values['chips_h_a'] = chips_h_a
                returned_values['plate_width'] = self.plate_width
                returned_values['min_height'] = self.min_height
                returned_values['plate_height'] = self.plate_height
                returned_values['rotation'] = rotation

                return True
            else:
                print('Height not valid.')
            
            
        # Any valid model has been found            
        returned_values['solving_time'] = time.time() - start_time
        returned_values['is_solved'] = False
        return False
    


    def get_solution_unsolved_parsed(self):
        return self.plate_height, self.min_height, self.solving_time

    def get_solution_solved_parsed(self, model):
        chip_positions = []
        for k in range(self.n_chips):
            found = False
            for x in range(self.plate_height):
                for y in range(self.plate_width):
                    if not found and model.evaluate(self.plate[x][y][k]):
                        if self.rotation:   
                            chip_positions.append((y, x, self.chips_widths[k], self.chips_heights[k], model.evaluate(self.rotated[k])))
                        else:
                            chip_positions.append((y, x, self.chips_widths[k], self.chips_heights[k], False))
                        found = True
                        
        pos_x = [x for x, _, _, _, _ in chip_positions]
        pos_y = [y for _, y, _, _, _ in chip_positions]
        chips_w_a = [w for _, _, w, _, _ in chip_positions]
        chips_h_a = [h for _, _, _, h, _ in chip_positions]
        rotated = [r for _, _, _, _, r in chip_positions]
        print(chip_positions)

        return pos_x, pos_y, chips_w_a, chips_h_a, self.plate_width, self.min_height, self.plate_height, rotated, self.solving_time



    def __str__(self):
        returned_values = f'Time available: {self.time_available}\nMin height: {self.min_height}\nMax height: {self.max_height}\n\nWidth of the plate: {self.plate_width}\nNumber of chips: {self.n_chips}\n\n'
        for i in range(self.n_chips):
            returned_values += f'Size of {i}° chip: ({self.chips_widths[i]}, {self.chips_heights[i]})\n' 
        return returned_values 