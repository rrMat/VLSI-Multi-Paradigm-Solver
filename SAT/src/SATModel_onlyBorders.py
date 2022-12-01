from z3 import *
import math
import numpy as np 
import time

import SAT.src.sat_utils as sat_utils


class SATModel_onlyBorders:

    NAME = 'SATModel_onlyBorders'

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
        self.rotated = []

        # Init
        self.solved = False
        self.plate_height = 0
        self.solving_time = time_available

    def solve(self, _, returned_values, verbose):
        # Timer
        start_time = time.time()

        # By now the problem hasn't been solved yet...
        returned_values['is_solved'] = False
        returned_values['result'] = 'N|A'
        returned_values['solving_time'] = self.solving_time
                
        # Constraint initialization
        overlapping_check = []
        placing_check = []
        symmetry_breaking_check = []

        # For each chip the combinations of literals which describe all the possible positions 
        values = {k: [] for k in range(self.n_chips)}           # Those which has to be True
        not_values = {k: [] for k in range(self.n_chips)}       # Those which has to be False
        if self.rotation:
            values_rotated = {k: [] for k in range(self.n_chips)}           # Those which has to be True (with rotation)
            not_values_rotated = {k: [] for k in range(self.n_chips)}       # Those which has to be False (with rotation)
            
        if verbose:
            print(f'Min height: {self.min_height}')
            print(f'Max height: {self.max_height}')
            print(f'With rotation: {self.rotation}')

        if self.rotation:
            self.rotated += [Bool(f"rotated_{i}") for i in range(self.n_chips)]

        # Starting from the lowest height, try all of them, increasing one by one
        for new_height in range(self.min_height, self.max_height):
            
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
                template_line_false = [self.plate[new_height - 1][w][k] for w in range(self.plate_width)]
                for i in range(len(not_values[k])):
                    not_values[k][i] += template_line_false
                    if self.rotation:
                        not_values_rotated[k][i] += template_line_false
                        
                # Define all the possible positions of each chipset with literals
                # *. Without rotation
                for y in range(new_height - 1, max(self.chips_heights[k] - 2, self.plate_height - 1), -1):
                    for x in range(self.plate_width - self.chips_widths[k] + 1):
                        points = []
                        points += [self.plate[y][x + slide_x][k] for slide_x in range(self.chips_widths[k])]
                        points += [self.plate[y - self.chips_heights[k] - 1][x + slide_x][k] for slide_x in range(self.chips_widths[k])]
                        points += [self.plate[y - slide_y - 1][x][k] for slide_y in range(self.chips_heights[k]-1)]   
                        points += [self.plate[y - slide_y - 1][x + self.chips_widths - 1][k] for slide_y in range(self.chips_heights[k]-1)]     
                        values[k].append(points)
                             
                        not_values[k].append(list(set(template_false) - set(values[k][-1])))
                # *. With rotation
                if self.rotation:
                    for y in range(new_height - 1, max(self.chips_widths[k] - 2, self.plate_height - 1), -1):
                        for x in range(self.plate_width - self.chips_heights[k] + 1):
                            values_rotated[k].append([self.plate[y - slide_y][x + slide_x][k] for slide_x in range(self.chips_heights[k]) 
                                                                                              for slide_y in range(self.chips_widths[k])])     
                            points = []
                            points += [self.plate[y][x + slide_x][k] for slide_x in range(self.chips_heights[k])]
                            points += [self.plate[y - self.chips_widths[k] - 1][x + slide_x][k] for slide_x in range(self.chips_heights[k])]
                            points += [self.plate[y - slide_y - 1][x][k] for slide_y in range(self.chips_widths[k]-1)]   
                            points += [self.plate[y - slide_y - 1][x + self.chips_heights - 1][k] for slide_y in range(self.chips_widths[k]-1)]     
                            values[k].append(points)
                        
                            not_values_rotated[k].append(list(set(template_false) - set(values_rotated[k][-1])))
                
            # Available positions of chips
            chip_places = {k: [] for k in range(self.n_chips)}
            if self.rotation:
                chip_places_rotated = {k: [] for k in range(self.n_chips)}
                
            for k in range(self.n_chips):
                for i in range(len(values[k])):             
                    chip_places[k].append(And(sat_utils.all_true(values[k][i]), sat_utils.all_false(not_values[k][i])))
                    if self.rotation:
                        chip_places_rotated[k].append(And(sat_utils.all_true(values_rotated[k][i]), sat_utils.all_false(not_values_rotated[k][i])))
                    
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
                                        And([sat_utils.exactly_one[self.encoding_type](chip_places_rotated[k])] + [self.rotated[k]])
                                    ])]
            
            # - 3° constraint
            if self.symmetry_breaking:
                # Find the tallest piece
                symmetry_breaking_check += [self.plate[0][0][np.argmax(self.chips_heights)]]
    
            # Solver initialization
            solver = Solver()

            # Add constraints
            solver.add(overlapping_check)
            solver.add(placing_check)
            solver.add(symmetry_breaking_check)

            # We have so created a model with a height increased by one respect to before...
            self.plate_height = new_height

            # Solve the model
            if solver.check() == sat:
                returned_values['solving_time'] = time.time() - start_time
                returned_values['is_solved'] = True
                returned_values['pos_x'], \
                returned_values['pos_y'], \
                returned_values['chips_w_a'], \
                returned_values['chips_h_a'], \
                returned_values['plate_width'], \
                returned_values['min_height'], \
                returned_values['plate_height'], \
                returned_values['rotation'] = self.getSolutionParsed(solver.model())
                returned_values['result'] = 'optimal'
                returned_values['result'] = 'optimal' if new_height == self.min_height else 'non-optimal'
                
                if verbose:
                    sat_utils.plot_device(solver.model(), self.plate, self.plate_width, self.plate_height, self.n_chips, 'SAT/img/img.png')
                return True
            else:
                if verbose:
                    print(f'Height {new_height} not valid')
    
            
        # Any valid model has been found            
        returned_values['solving_time'] = time.time() - start_time
        returned_values['is_solved'] = False
        returned_values['result'] = 'UNSAT'
        return False
    
    def getSolutionParsed(self, model):
        chip_positions = []
        for k in range(self.n_chips):
            found = False
            for x in range(self.plate_height):
                for y in range(self.plate_width):
                    if not found and model.evaluate(self.plate[x][y][k]):
                        if self.rotation:   
                            chip_positions.append((y, x, self.chips_widths[k], self.chips_heights[k], True if model.evaluate(self.rotated[k]) else False))
                        else:
                            chip_positions.append((y, x, self.chips_widths[k], self.chips_heights[k], False))
                        found = True
                        
        pos_x = [x for x, _, _, _, _ in chip_positions]
        pos_y = [y for _, y, _, _, _ in chip_positions]
        chips_w_a = [w for _, _, w, _, _ in chip_positions]
        chips_h_a = [h for _, _, _, h, _ in chip_positions]
        rotated = [r for _, _, _, _, r in chip_positions]

        return pos_x, pos_y, chips_w_a, chips_h_a, self.plate_width, self.min_height, self.plate_height, rotated

    def getSolutionUnsolved(self):
        return self.plate_height, self.solving_time

    def __str__(self):
        returned_values = f'Time available: {self.time_available}\nMin height: {self.min_height}\nMax height: {self.max_height}\n\nWidth of the plate: {self.plate_width}\nNumber of chips: {self.n_chips}\n\n'
        for i in range(self.n_chips):
            returned_values += f'Size of {i}° chip: ({self.chips_widths[i]}, {self.chips_heights[i]})\n' 
        return returned_values