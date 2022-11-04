from z3 import *
import math
import numpy as np 
import time

import SATSolver
import sat_utils


class VLSISolver:

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

        self.solved = False
        self.plate = None
        self.rotated = None
        self.plate_height = None
        self.solving_time = None
        self.solver = None

    def solve(self):
        start_time = time.time()

        for plate_height in range(self.min_height, self.max_height):
            time_remained = self.time_available - (time.time() - start_time)
            if time_remained <= 0:
                break

            # Defining SATSolver
            if self.interrupt:
                self.solver = SATSolver(timeout=int(time_remained))
            else:
                self.solver = SATSolver()


            # Defining variables
            self.plate = [Bool(f"plate_{k}_{j}_{i}") for i in range(self.n_chips) for j in range(self.plate_width) for k in range(plate_height)]
            self.rotated = [Bool(f"rotated_{i}") for i in range(self.n_chips)]
            self.plate_height = plate_height

            # Defining constraints:
            # - 1° constraint 
            overlapping_check = [sat_utils.at_most_one[self.encoding_type](point) for row in self.plate for point in row]

            # - 2° constraint
            placing_check = []
            for k in range(self.n_chips):

                configurations = []
                for y in range(plate_height - self.chips_heights[k] + 1):
                    for x in range(self.plate_width - self.chips_widths[k] + 1):
                        configurations.append(sat_utils.all_true([self.plate[y + slide_y][x + slide_x][k] for slide_x in range(self.chips_widths[k]) for slide_y in range(self.chips_heights[k])]))
                
                # If chips can be rotated...
                if self.rotation:
                    configurations_r = []
                    for y in range(plate_height - self.chips_widths[k] + 1):
                        for x in range(self.plate_width - self.chips_heights[k] + 1):
                            configurations_r.append(sat_utils.all_true([self.plate[y + slide_y][x + slide_x][k] for slide_x in range(self.chips_heights[k]) for slide_y in range(self.chips_widths[k])]))
                
                    placing_check = placing_check + sat_utils.exactly_one[self.encoding_type]([
                        And(sat_utils.exactly_one[self.encoding_type](configurations) + [Not(self.rotated[k])]),
                        And(sat_utils.exactly_one[self.encoding_type](configurations_r) + [self.rotated[k]])
                    ]) 
                # Otherwise...
                else:
                    placing_check = placing_check + [sat_utils.exactly_one[self.encoding_type](configurations)]

            # - 3° constraint 
            if self.symmetry_breaking: 
                symmetry_breaking = []
                symmetry_breaking += [sat_utils.z3_lex_less_eq([self.plate[i][j] for j in range(self.plate_width) for i in range(plate_height)],
                                                               [self.plate[i][j] for j in range(self.plate_width) for i in reversed(range(plate_height))], 
                                                               self.n_chips)]
                symmetry_breaking += [sat_utils.z3_lex_less_eq([self.plate[i][j] for j in range(self.plate_width) for i in range(plate_height)],
                                                               [self.plate[i][j] for j in reversed(range(self.plate_width)) for i in range(plate_height)], 
                                                               self.n_chips)]
            
            # Add constraints
            self.solver.add_constraint(overlapping_check)
            self.solver.add_constraint(placing_check)
            if self.symmetry_breaking: # Only if symmetry breaking is applied!
                self.solver.add_constraint(symmetry_breaking)

            if self.solver.solve() == sat:
                self.solving_time = time.time() - start_time
                self.solved = True
                return True
            

        self.solving_time = time.time() - start_time
        self.solved = False
        return False

    def evalutate(self):
        model = self.solver.get_model()
    
        circuits_pos = []
        for k in range(self.n_chips):
            found = False
            for x in range(self.plate_height):
                for y in range(self.plate_width):
                    if not found and model.evaluate(self.plate[x][y][k]):
                        if self.rotation:
                            if model.evaluate(self.rotated[k]):
                                circuits_pos.append((y, x, self.chips_heights[k], self.chips_widths[k]))
                            else:
                                circuits_pos.append((y, x, self.chips_widths[k], self.chips_heights[k]))
                        else:
                            circuits_pos.append((y, x, self.chips_widths[k], self.chips_heights[k]))
                        found = True

        pos_x = [x for x, _, _, _ in circuits_pos]
        pos_y = [y for _, y, _, _ in circuits_pos]
        chips_w_a = [w for _, _, w, _ in circuits_pos]
        chips_h_a = [h for _, _, _, h in circuits_pos]

        return pos_x, pos_y, chips_w_a, chips_h_a, self.plate_width, self.plate_height, self.solving_time

    def __str__(self):
        output = f'Time available: {self.time_available}\nMin height: {self.min_height}\nMax height: {self.max_height}\n\nWidth of the plate: {self.plate_width}\nNumber of chips: {self.n_chips}\n\n'
        for i in range(self.n_chips):
            output += f'Size of {i}° chip: ({self.chips_widths[i]}, {self.chips_heights[i]})\n' 
        return output 