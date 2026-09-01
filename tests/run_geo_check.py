import os
import unittest

os.chdir(r"c:/Users/jpmic/OneDrive/Documents/projet itinéraire/api")

import tests.test_geo as module

suite = unittest.defaultTestLoader.loadTestsFromModule(module)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
