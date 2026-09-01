import os
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parent
os.chdir(root)

try:
    import tests.test_geo as test_module  # type: ignore
except ModuleNotFoundError:
    print("Module tests.test_geo introuvable depuis", root)
    sys.exit(1)

suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
result = unittest.TextTestRunner(verbosity=2).run(suite)

if result.wasSuccessful():
    print("\nVERIFICATION_OK")
    sys.exit(0)
print("\nVERIFICATION_KO")
sys.exit(1)
