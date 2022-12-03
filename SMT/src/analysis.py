import os 
import utils.utils as ut

class analysis:
    def __init__(self):
      pass
    
    def execute(self):

        csv_paths_encodings = []
        folder_path = os.path.join(
                            os.path.dirname(__file__),
                            '../Timings'
                            )

        for file in os.listdir(folder_path):
          tmp = os.path.join(folder_path, file)
          csv_paths_encodings.append(tmp)


        result_pat = os.path.join(
            os.path.dirname(__file__),
            '../src/experimental_result' + '.csv'
            )


        labels = ['z3Py', 'z3Py_parallel', 'pySMT_z3', 'pySMT_msat']

        ut.write_experimental_result(result_pat, csv_paths_encodings, labels)
        ut.display_times_comparison( csv_paths_encodings, labels, 9, 'SMT/out/comparison.png' )
        #rotation

        csv_paths_encodings_rotation = []
        folder_path_rotation = os.path.join(
                            os.path.dirname(__file__),
                            '../Timings_rotation'
                            )

        for file in os.listdir(folder_path_rotation):
          tmp = os.path.join(folder_path_rotation, file)
          csv_paths_encodings_rotation.append(tmp)

        result_pat_rotation = os.path.join(
            os.path.dirname(__file__),
            '../src/experimental_result_rotation' + '.csv'
            )

        labels_rotation = ['z3Py_rotation', 'z3Py_parallel_rotation']

        ut.write_experimental_result(result_pat_rotation, csv_paths_encodings_rotation, labels_rotation)
        ut.display_times_comparison( csv_paths_encodings_rotation, labels_rotation, 9, 'SMT/out/comparison_rotation.png')



