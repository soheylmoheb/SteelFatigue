import numpy as np

file_name = "corrective_0.2_increasing_120_140.npz"
parameter = np.load(file_name)
result = parameter['arr_0']
print(result)
