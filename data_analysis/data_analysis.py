
import pandas as pd

data = pd.read_csv("./info_false_fire_47_15")
data = data.loc[data['fire_x'] == 47]
data = data.loc[data["civil_info_exchange"] == False]


data = data.loc[data["K"] == 0]
data = data.loc[data["N"] == 300]
print(data["List dead agents"][200].split()[1])
