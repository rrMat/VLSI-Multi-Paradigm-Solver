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
        labels = []
        for file in os.listdir(folder_path):
          tmp = os.path.join(folder_path, file)
          f = file.replace(".csv", "")
          labels.append(f)
          csv_paths_encodings.append(tmp)


        result_pat = os.path.join(
            os.path.dirname(__file__),
            '../src/experimental_result' + '.csv'
            )

      

        ut.display_times_comparison(csv_paths_encodings, labels, 40, 'SMT/out/comparison.png' )
        ut.write_experimental_result(result_pat, csv_paths_encodings, labels)
        
        # #rotation

        csv_paths_encodings_rotation = []
        folder_path_rotation = os.path.join(
                            os.path.dirname(__file__),
                            '../Timings_rotation'
                            )

        labels_rotation = []
        for file in os.listdir(folder_path_rotation):
          tmp = os.path.join(folder_path_rotation, file)
          f = file.replace(".csv", "")
          labels_rotation.append(f)
          csv_paths_encodings_rotation.append(tmp)
        
        print(labels_rotation)
        result_pat_rotation = os.path.join(
            os.path.dirname(__file__),
            '../src/experimental_result_rotation' + '.csv'
            )



        ut.display_times_comparison( csv_paths_encodings_rotation, labels_rotation, 40, 'SMT/out/comparison_rotation.png')
        ut.write_experimental_result(result_pat_rotation, csv_paths_encodings_rotation, labels_rotation)
        


