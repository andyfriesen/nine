#!python

from glob import glob
import os
import os.path

source = []

for name, dirs, files in os.walk('.'):
    source.extend(
        [os.path.join(name, file) for file in files if file.endswith('.py')]
    )

import coverage
coverage.erase()

import runtests
coverage.start()
runtests.main()
coverage.stop()

coverage.report(source)
