#!/usr/bin/env python3

import logging
import sys

logging.basicConfig(format='%(asctime)s [%(filename)s|%(funcName)s][%(levelname)s] %(message)s', level=logging.INFO)
log = logging.getLogger('log')

sys.modules[__name__] = log
