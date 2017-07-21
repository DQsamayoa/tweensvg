"""
    Test module for SVGUtils module
"""
import unittest
from TweenSVG import SVGUtils 

class SVGUtilsTests(unittest.TestCase):
    """ 
        Test class for SVGUtils class
    """
    def __init__(self, args):
        unittest.TestCase.__init__(self, args)
        self.uut = SVGUtils.SVGUtils

    def test_value_unit(self):
        # Test some valid inputs
        test_vector = {
            "0": (0.0, ""),
            "0.67": (0.67, ""),
            "1.0 ": (1.0, ""),
            "10": (10.0, ""),
            ".2": (0.2, ""),
            " 112 ": (112.0, ""),
            "100%": (100.0, "%"),
            "2.083%": (2.083, "%"),
            "10px": (10.0, "px"),
            "1in ": (1.0, "in"),
            "20em": (20.0, "em"),
            "2.54cm": (2.54, "cm"),
            "25.4mm": (25.4, "mm"),
            "40ex": (40.0, "ex"),
            "6pc ": (6.0, "pc"),
            "72pt": (72.0, "pt"),
        }
        for input_val, (dim_out_expect, unit_out_expect) in test_vector.items():
            dim_out, unit_out = self.uut.value_unit(input_val)
            self.assertAlmostEqual(dim_out, dim_out_expect, "Incorrect dimension")
            self.assertEqual(unit_out, unit_out_expect, "Incorrect units")

        # Test some invalid inputs
        error_test_vector = [
            'not a valid value'
            '1 2'
            '1,2'
        ]
        for input_val in error_test_vector:
            with self.assertRaises(ValueError):
                self.uut.value_unit(input_val)


    def test_to_unit_val(self):
        test_vector = {
            "0": (0.0, ""),
            "0.67": (0.67, ""),
            "1": (1.0, ""),
            "10": (10.0, ""),
            "0.2": (0.2, ""),
            "112": (112.0, ""),
            "100%": (100.0, "%"),
            "2.083%": (2.083, "%"),
            "10px": (10.0, "px"),
            "1in": (1.0, "in"),
            "20em": (20.0, "em"),
            "2.54cm": (2.54, "cm"),
            "25.4mm": (25.4, "mm"),
            "40ex": (40.0, "ex"),
            "6pc": (6.0, "pc"),
            "72pt": (72.0, "pt"),
        }
        for expected_unit_val, (input_value, input_unit) in test_vector.items():
            unit_val = self.uut.to_unit_val(input_value, input_unit)
            self.assertEqual(unit_val, expected_unit_val)

    def test_transforms(self):
        test_vector = {
            "matrix(0 0 0 0 0 0)": [("matrix", "0 0 0 0 0 0")],
            "matrix(0 1 -1 0 0 0)": [("matrix", "0 1 -1 0 0 0")],
            "matrix(0.9659 0.2588 -0.2588 0.9659 0 0)": [("matrix", "0.9659 0.2588 -0.2588 0.9659 0 0")],
            "rotate(0)": [("rotate", "0")],
            "rotate(0,0,0)": [("rotate", "0,0,0")],
            "rotate(0,40,40)": [("rotate", "0,40,40")],
            "rotate(180) translate(-120 -250)": [("rotate", "180"), ("translate", "-120 -250")],


            "rotate(45,120,170) translate(70,120)": [("rotate", "45,120,170"), ("translate", "70,120")],
            "scale(0.02 0.02) translate(4000 2000)": [("scale", "0.02 0.02"), ("translate", "4000 2000")],
            "scale(0.02929)": [("scale", "0.02929")],
            "scale(0.2, 0.2)": [("scale", "0.2, 0.2")],
            "scale(0.3) translate(-30, 500)": [("scale", "0.3"), ("translate", "-30, 500")],
            "scale(0.3) translate(390, 500)": [("scale", "0.3"), ("translate", "390, 500")],
            "scale(0.6),rotate(45)": [("scale", "0.6"), ("rotate", "45")],
            "skewX(-30)": [("skewX", "-30")],
            "skewX(30) rotate(90) scale(2,2)": [("skewX", "30"), ("rotate", "90"), ("scale", "2,2")],
            "skewX(45) skewY(45)": [("skewX", "45"), ("skewY", "45")],
            "skewY(3)": [("skewY", "3")],
            "translate( 0,  0)  ": [("translate", " 0,  0")],
            "translate(0 0)": [("translate", "0 0")],
            "translate(0, 0)": [("translate", "0, 0")],
            "translate(-10 -15) scale(2) scale(-1,-1)": [("translate", "-10 -15"), ("scale", "2"), ("scale", "-1,-1")],
            "translate(50 50),rotate(45),skewX(15),scale(0.8)": [("translate", "50 50"), ("rotate", "45"), ("skewX", "15"), ("scale", "0.8")],
            "translate(50 50)rotate(45)skewX(15)scale(0.8) ": [("translate", "50 50"), ("rotate", "45"), ("skewX", "15"), ("scale", "0.8")],
        }
        for input_val, expected_output_list in test_vector.items():
            output_list = self.uut.transforms(input_val)
            self.assertEqual(output_list, expected_output_list)

