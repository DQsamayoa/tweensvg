"""
Test suite for TweenSVG
"""
import sys 
import unittest
from TestTweenSVG import SVGUtilsTests, ModuleTests

def run_tests():
    """ 
        Run all of the tests and return true if successful, false otherwise
    """
    tests = [ 
        SVGUtilsTests.SVGUtilsTests,
        ModuleTests.ModuleTests
    ]   

    loader = unittest.TestLoader()
    suites = [loader.loadTestsFromTestCase(test_class) for test_class in tests]
    runner = unittest.TextTestRunner()
    results = runner.run(unittest.TestSuite(suites))
    return results.wasSuccessful()

if not run_tests():
    sys.exit(1)

