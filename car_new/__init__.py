from autoCar import autoCar

import logging, logging.config

logging.config.fileConfig('carLog.ini')
logr = logging.getLogger('car')

logr.info('__init__')

car = autoCar()

car.Run()       
        
