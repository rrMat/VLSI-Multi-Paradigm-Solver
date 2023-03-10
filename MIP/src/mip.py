from amplpy import AMPL, Environment
from pathlib import Path
import re

from utils.utils import load_data, plot_device, write_sol, write_stat_line, write_experimental_result, display_times_comparison

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

    def __init__(self, model='std', rotation=False, solver='gurobi', ampl_dir=None, print_image=False, verbose=True):

        if ampl_dir is None:
            self.ampl = AMPL()
        else:
            self.ampl = AMPL(Environment(ampl_dir))

        self.ampl.set_option('time', 1)

        self.model = model
        self.rotation = rotation
        self.solver = solver

        self.verbose = verbose

        self.__set_paths(model, rotation, solver)

        self.print_image = print_image

        self.set_solver(solver)

    def set_model(self, model):
        if self.verbose:
            print(f'\nSOLVING WITH {model} MODEL')
        self.model = model
        self.__set_paths(self.model, self.rotation, self.solver)

    def set_rotation(self, rotation):
        if self.verbose:
            print(f'Rotation is {rotation}')
        self.rotation = rotation
        self.__set_paths(self.model, self.rotation, self.solver)

    def set_solver(self, solver):
        if self.verbose:
            print(f'\n\nSOLVING WITH {solver} SOLVER')
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
        self.stats_path = (src_path / f'../stats/{"" if self.rotation else "no_"}rot/{models_dict[model]}_{solver}{rot}.csv').resolve()

        self.image_folder_path.mkdir(parents=True, exist_ok=True)
        self.output_folder_path.mkdir(parents=True, exist_ok=True)

    def solve(self, instance):
        print(f'Solving instance {instance}')

        image_path = (self.image_folder_path / f'{instance}.jpg').resolve()
        output_path = (self.output_folder_path / f'{instance}.txt').resolve()

        self.ampl.reset()

        self.ampl.read(self.model_path)

        w, n, widths, heights = load_data(instance)

        self.ampl.get_parameter('w').set(w)
        self.ampl.get_parameter('n').set(n)
        self.ampl.get_parameter('widths').set_values(widths)
        self.ampl.get_parameter('heights').set_values(heights)

        if self.verbose:
            self.ampl.solve()
        else:
            self.ampl.get_output('solve;')

        solve_result = self.ampl.get_value("solve_result")
        solve_time = self.ampl.get_data('_solve_elapsed_time').to_list()[0]
        max_height = self.ampl.get_objective('H').value()
        coordinates_x = [c[1] for c in self.ampl.get_variable('Coordinates_x').get_values().to_list()]
        coordinates_y = [c[1] for c in self.ampl.get_variable('Coordinates_y').get_values().to_list()]
        rotated = [r[1] for r in self.ampl.get_variable('Rotated').get_values().to_list()] if self.rotation else []

        if solve_result == 'solved':
            sol_type = 'optimal'
        elif (solve_result == 'failure' or solve_result == 'limit' or solve_result == 'solved?') and max_height > 0:
            sol_type = 'non-optimal'
        elif solve_result == 'infeasible':
            sol_type = 'UNSAT'
        else:
            sol_type = 'N|A'

        if self.verbose:
            print(f'Instance solved with result: {sol_type}\n'
                  f'Height found: {max_height}\n'
                  f'Time needed: {solve_time}')

        if sol_type == 'optimal' or sol_type == 'non-optimal':
            if self.print_image:
                plot_device(coordinates_x, coordinates_y, widths, heights, w, max_height, rotated, image_path)
            write_sol(output_path, w, max_height, n, widths, heights, coordinates_x, coordinates_y, rotated)

        write_stat_line(self.stats_path, instance, max_height, solve_time, sol_type)

    def execute(self, instance):
        if instance is not None:
            self.solve(instance)
        else:
            for i in range(1, 41):
                self.solve(i)


def sorting_files(file):
    result = re.search(r"(.+?)_([a-zA-Z]+)(_rot)?.csv", file.name)
    return result.group(2) + result.group(1)


def write_results():
    result_path = (src_path / f'../stats/results_mip.csv').resolve()
    stat_paths = [p for p in (src_path / f'../stats/no_rot/').resolve().glob('*.csv')]
    stat_paths.sort(key=sorting_files)

    names = [re.search(r"(.+).csv", p.name).group(1) for p in stat_paths]
    names = [name.replace('standard', 'std').replace('strong_bounds', 'stb').replace('_rot', '').replace('_', ' ')
             for name in names]

    write_experimental_result(result_path, stat_paths, names)


def plot_times():
    pattern = re.compile(r"(.+gurobi.+csv)")
    plot_path = (src_path / f'../img/times_mip_rot.png').resolve()
    stat_paths = [p for p in (src_path / f'../stats/rot/').resolve().glob('*.csv') if pattern.match(p.name)]
    stat_paths.sort(key=sorting_files)

    names = [re.search(r"(.+).csv", p.name).group(1) for p in stat_paths]
    names = [name.replace('standard', 'std').replace('strong_bounds', 'stb').replace('_rot', '').replace('_', ' ')
             for name in names]

    display_times_comparison(stat_paths, names, 40, plot_path)


if __name__ == '__main__':

    plot_times()

    #mip = MIP(ampl_dir='C:/Program Files/ampl.mswin64/', solver='highs', print_image=False, rotation=False)
    #mip.solve(1)







