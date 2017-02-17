# -*- coding: utf-8 -*-

import numpy as np

data = np.load("/media/tamas/Sör2/CurrencyData/AUDCAD_windowed.npz")

o_data = np.load("/media/tamas/Sör2/CurrencyData/data.npz")
o_data = o_data['AUDCAD.npy']
o_data = o_data[20-1:]
#settings = {"nrof_bins" : 5,
#            "look_forward": 15,
#            "look_backward": 20}
np.savez("/media/tamas/Sör2/CurrencyData/AUDCAD_windowed2", datax=data["datax"], datay=data["datay"], original=o_data, settings=data["settings"])
s = 2