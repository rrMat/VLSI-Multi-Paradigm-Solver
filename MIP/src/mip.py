from amplpy import AMPL, Environment
import numpy as np
from pathlib import Path

from utils.utils import load_data, plot_device, write_sol, write_stat_line

models_dict = {
    'std': 'standard',
    'strong': 'strong_bounds'
}

time_options_dict = {
    'gurobi': ('gurobi_options', 'timelim=300'),
    'cplex': ('cplex_options', 'time=300'),
    'copt': ('copt_options', 'timelim=300'),
    'highs': ('highs_options', 'timelimit=300'),
    'xpress': ('xpress_options', 'maxtime=-300'),
    'cbc': ('cbc_options', 'seconds=300')
}

src_path = Path(__file__).parent


class MIP:

    def __init__(self, model='std', rotation=False, solver='gurobi', ampl_dir=None, print_image=False):

        if ampl_dir is None:
            self.ampl = AMPL()
        else:
            self.ampl = AMPL(Environment(ampl_dir))

        self.ampl.set_option('time', 1)

        self.__set_paths(model, rotation, solver)

        self.print_image = print_image

        self.model = model
        self.rotation = rotation
        self.solver = solver

        self.set_solver(solver)

    def set_model(self, model):
        self.model = model
        self.__set_paths(self.model, self.rotation, self.solver)

    def set_rotation(self, rotation):
        self.rotation = rotation
        self.__set_paths(self.model, self.rotation, self.solver)

    def set_solver(self, solver):
        self.solver = solver
        self.ampl.set_option('solver', self.solver)
        option, value = time_options_dict[solver]
        self.ampl.set_option(option, value)
        self.__set_paths(self.model, self.rotation, self.solver)

    def __set_paths(self, model, rotation, solver):
        rot = ''
        if rotation:
            rot = '_rot'

        self.model_path = (src_path / f'models/{models_dict[model]}{rot}.mod').resolve()
        self.image_folder_path = (src_path / f'../img/{models_dict[model]}_{solver}{rot}').resolve()
        self.output_folder_path = (src_path / f'../out/{models_dict[model]}_{solver}{rot}').resolve()
        self.stats_path = (src_path / f'../stats/{models_dict[model]}_{solver}{rot}.csv').resolve()

        self.image_folder_path.mkdir(parents=True, exist_ok=True)
        self.output_folder_path.mkdir(parents=True, exist_ok=True)

    def solve(self, instance):
        print(f'Solving instance {instance}')

        image_path = (self.image_folder_path / f'{instance}.jpg').resolve()
        output_path = (self.output_folder_path / f'{instance}.txt').resolve()

        self.ampl.reset()

        self.ampl.read(self.model_path)

        w, n, widths, heights = load_data(instance)
        height_lb = (np.array(widths)@np.array(heights)) / w

        self.ampl.get_parameter('w').set(w)
        self.ampl.get_parameter('n').set(n)
        self.ampl.get_parameter('widths').set_values(widths)
        self.ampl.get_parameter('heights').set_values(heights)

        self.ampl.solve()

        solve_time = self.ampl.get_data('_total_solve_time').to_list()[0]
        max_height = self.ampl.get_objective('H').value()
        coordinates_x = [c[1] for c in self.ampl.get_variable('Coordinates_x').get_values().to_list()]
        coordinates_y = [c[1] for c in self.ampl.get_variable('Coordinates_y').get_values().to_list()]

        rotated = [r[1] for r in self.ampl.get_variable('Rotated').get_values().to_list()] if self.rotation else []

        if self.print_image:
            plot_device(coordinates_x, coordinates_y, widths, heights, w, max_height, rotated)

        plot_device(coordinates_x, coordinates_y, widths, heights, w, max_height, rotated, image_path)
        write_sol(output_path, w, max_height, n, widths, heights, coordinates_x, coordinates_y, rotated)
        write_stat_line(self.stats_path, instance, max_height, height_lb, solve_time)

    def execute(self, instance):
        if instance is not None:
            self.solve(instance)
        else:
            for i in range(1, 41):
                self.solve(i)


if __name__ == '__main__':
    mip = MIP(ampl_dir='C:/Program Files/ampl.mswin64/', solver='gurobi', print_image=False, rotation=False)
    mip.solve(15)






