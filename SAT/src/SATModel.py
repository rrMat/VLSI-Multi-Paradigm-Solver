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



    def solve(self, _, returned_values, verbose):
        returned_values['is_solved'] = False
                
        # Constraint initialization
        overlapping_check = []
        placing_check = None

        # Available positions of chips
        chip_places = {k: [] for k in range(self.n_chips)}
        
        start_time = time.time()

        values = {}
        for k in range(self.n_chips):
            values[k] = []

        print(f'Height: {self.max_height}')
        for new_height in range(self.min_height, self.max_height + 1):
            if verbose:
                print('Height: ', new_height)

            # Defining literals
            self.plate += [[[Bool(f"plate_{k}_{j}_{i}") for i in range(self.n_chips)] 
                                                        for j in range(self.plate_width)] 
                                                        for k in range(self.plate_height, new_height)]

            if verbose:
                print(f'Size of plate: ({len(self.plate)}, {len(self.plate[-1])}, {len(self.plate[-1][-1])})')
                print(f'Plate height: {self.plate_height}')
                print(f'New height: {new_height}')

                
            # Defining available positions for each chip
            for k in range(self.n_chips):
                
                template_false = [self.plate[h][w][k] for h in range(new_height)
                                                      for w in range(self.plate_width)]
                
                # Define all the possible positions of each chipset with literals
                # *. Without rotation
                for y in range(new_height - 1, max(self.chips_heights[k] - 2, self.plate_height - 1), -1):
                    for x in range(self.plate_width - self.chips_widths[k] + 1):
                        values[k].append([self.plate[y - slide_y][x + slide_x][k] for slide_x in range(self.chips_widths[k]) 
                                                                                  for slide_y in range(self.chips_heights[k])])     
                chip_places[k] = []
                for i in range(len(values[k])):             
                    chip_places[k].append(And(sat_utils.all_true(values[k][i]), 
                                                sat_utils.all_false(list(set(template_false) - set(values[k][i])))))

                        
                        

           
            # Defining constraints:
            # - 1° constraint 
            overlapping_check += [sat_utils.at_most_one[self.encoding_type](self.plate[i][j]) for i in range(self.plate_height, new_height) 
                                                                                              for j in range(self.plate_width)]
            # - 2° constraint
            placing_check = []
            for k in range(self.n_chips):  
                if not self.rotation:
                    placing_check += [sat_utils.exactly_one[self.encoding_type](chip_places[k])]
                else:
                    placing_check += [sat_utils.exactly_one[self.encoding_type]([
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

            if self.plate_height == self.min_height:
                continue
            

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

                
                sat_utils.plot_device(solver.model(), self.plate, self.plate_width, self.plate_height, self.n_chips, 'SAT/img')

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
                        
                        if x + self.chips_heights[k] > self.plate_height or y + self.chips_widths[k] > self.plate_width:
                            print(f'{k} block out of boundaries')
                        else:
                            for h in range(self.chips_heights[k]):
                                for w in range(self.chips_widths[k]):
                                    if not model.evaluate(self.plate[x + h][y + w][k]):
                                        print(f'{k} block should be also in {x+h} {y+w}')
                                        
        for x in range(self.plate_height):
            for y in range(self.plate_width):
                for k in range(self.n_chips):
                    if model.evaluate(self.plate[x][y][k]):
                        print(f'({x},{y}) -> {k}')
        
        # Check if some blocks are overlapped
        for x in range(self.plate_height):
            for y in range(self.plate_width):
                sum = 0 
                for k in range(self.n_chips):
                    if model.evaluate(self.plate[x][y][k]):
                        sum += 1
                if sum > 1:
                    print(f'Overlapping ({x} {y})')
                if sum == 0:
                    print(f'None occupy this zone {x} {y}')
                        
                
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