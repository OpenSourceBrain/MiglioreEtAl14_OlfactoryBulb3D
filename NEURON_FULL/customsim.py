
import custom_params
custom_params.filename = 'fig7'
import params

import common
common.nmitral=1


import runsim

params.tstop = 50
runsim.build_complete_model('c10.dic')
runsim.run()

