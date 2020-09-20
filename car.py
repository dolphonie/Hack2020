# Created by Patrick Kao
import torch
import pandas as pd
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset

COLUMNS_DICT = {
    "id": 0,
    "injuries": 9,
    "fatalities" : 10,
    "direction": ,
    "weather": ,
    ""
}
class CarDataset(Dataset):
    def __init__(self):
        super(CarDataset, self).__init__()
        raw = pd.read_excel("/media/dolphonie/Datasets/car/CrashReport2014.xlsx")
        data = np.array(raw)
        # get columns [id, injuries, speeding,

        self.data = data

    def __len__(self):
        return self.data.size[0]

    def __getitem__(self, idx):
        pass

loader = torch.utils.data.DataLoader(CarDataset(), batch_size = 10, shuffle = True)
for epoch in range(5):
    for i, data in enumerate(loader):
        print(data)

