"""
    Test module for SVGUtils module
"""
import unittest
from TweenSVG import SVGUtils
from itertools import chain


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
            self.assertAlmostEqual(
                dim_out, dim_out_expect, "Incorrect dimension")
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


    def test_viewbox_vals(self):
        test_vector = {
            "0 0 0 0": (0, 0, 0, 0),
            "0,0,0,0": (0, 0, 0, 0),
            "0, 0,  0,   0": (0, 0, 0, 0),
            "1,2,3,4": (1, 2, 3, 4),
            "0.1 0.2 0 123": (0.1, 0.2, 0, 123),
            "-1, -2, -3, -4" : (-1, -2, -3, -4),
            "-1 -2 -3 -4" : (-1, -2, -3, -4),
        }
        for input_val, expected_output in test_vector.items():
            output = self.uut.viewbox_vals(input_val)
            self.assertEqual(output, expected_output)

        error_test_vector = [
            "not a valid string",
            "",
            "1234"
        ]
        for input_val in error_test_vector:
            with self.assertRaises(ValueError):
                self.uut.viewbox_vals(input_val)

    def test_to_viewbox_val(self):
        test_vector = {
            "0 0 0 0": (0, 0, 0, 0),
            "1 2 3 4": (1, 2, 3, 4),
            "0.1 0.2 0 123": (0.1, 0.2, 0, 123),
            "-1 -2 -3 -4" : (-1, -2, -3, -4),
        }
        for expected_output, input_val in test_vector.items():
            output = self.uut.to_viewbox_val(*input_val)
            self.assertEqual(output, expected_output)

    def test_num_args_for_path_command(self):
        # This is a really trivial test
        # Let's not do an exhasutive test of all output values here
        # there isn't much point. Just test all the vals to see
        # that they produce outputs of roughly the right types
        letters = [chr(val) for val in range(97, 122+1)]
        for letter in letters:
            if letter in "mlhvcsqtaz":
                output = self.uut.num_args_for_path_command(letter)
                self.assertIsInstance(output, list)
                output_upper = self.uut.num_args_for_path_command(letter.upper())
                self.assertIsInstance(output_upper, list)
            else:
                with self.assertRaises(ValueError):
                    self.uut.num_args_for_path_command(letter)

    def test_path_parts(self):
        test_vector = {
            "M0 0": [("M", ["0", "0"])],
            "M 0 0": [("M", ["0", "0"])],
            "M 0,0": [("M", ["0", "0"])],
            "M 0,  0": [("M", ["0", "0"])],
            "M 0,0Z": [("M", ["0", "0"]), ("Z", [])],
            "M 0, 0 0, 0 0, 0": [("M", ["0", "0"]), ("L", ["0", "0"]), ("L", ["0", "0"])],
            "M0,0 V8 C3,8 4,7 4,4 C4,1 3,0 0,0z": [
                ("M", ["0", "0"]),
                ("V", ["8"]),
                ("C", ["3", "8", "4", "7", "4", "4"]),
                ("C", ["4", "1", "3", "0", "0", "0"]),
                ("z", [])
            ],
            "M0 4000l2000 -4000l2000 4000Z": [
                ("M", ["0", "4000"]),
                ("l", ["2000", "-4000"]),
                ("l", ["2000", "4000"]),
                ("Z", [])
            ],
            "M0 0m0 0L0 0l0 0H0h0V0v0C0 0 0 0 0 0c0 0 0 0 0 0S0 0 0 0s0 0 0 0Q0 0 0 0q0 0 0 0T0 0t0 0A0 0 0 0 0 0 0a0 0 0 0 0 0 0Z": [
                ("M", ["0", "0"]),
                ("m", ["0", "0"]),
                ("L", ["0", "0"]),
                ("l", ["0", "0"]),
                ("H", ["0"]),
                ("h", ["0"]),
                ("V", ["0"]),
                ("v", ["0"]),
                ("C", ["0", "0", "0", "0", "0", "0"]),
                ("c", ["0", "0", "0", "0", "0", "0"]),
                ("S", ["0", "0", "0", "0"]),
                ("s", ["0", "0", "0", "0"]),
                ("Q", ["0", "0", "0", "0"]),
                ("q", ["0", "0", "0", "0"]),
                ("T", ["0", "0"]),
                ("t", ["0", "0"]),
                ("A", ["0", "0", "0", "0", "0", "0", "0"]),
                ("a", ["0", "0", "0", "0", "0", "0", "0"]),
                ("Z", []),
            ],
            # Lineto is implicit after a moveto command
            "M0 0 10 10":[
                ("M", ["0", "0"]),
                ("L", ["10", "10"])
            ],
            "m0 0 10 10":[
                ("m", ["0", "0"]),
                ("l", ["10", "10"])
            ],
            "m0 0 10 10 M 0 10 10 0":[
                ("m", ["0", "0"]),
                ("l", ["10", "10"]),
                ("M", ["0", "10"]),
                ("L", ["10", "0"])
            ]
        }
        for input_value, expected_output in test_vector.items():
            output = self.uut.path_parts(input_value)
            self.assertEqual(output, expected_output)

        error_test_vector=[
            "Invliad path",
            "M0Z",
            "M []'#-="
        ]
        for input_value in error_test_vector:
            with self.assertRaises(ValueError):
                self.uut.path_parts(input_value)

    def test_path_string(self):
        test_vector = {
            "M 0 0": [("M", ["0", "0"])],
            "M 0 0 M 0 0": [("M", ["0", "0"]), ("M", ["0", "0"])],
            "M 0 0 V 8 C 3 8, 4 7, 4 4 C 4 1, 3 0, 0 0 z": [
                ("M", ["0", "0"]),
                ("V", ["8"]),
                ("C", ["3", "8", "4", "7", "4", "4"]),
                ("C", ["4", "1", "3", "0", "0", "0"]),
                ("z", [])
            ],
            "M 0 4000 l 2000 -4000 l 2000 4000 Z": [
                ("M", ["0", "4000"]),
                ("l", ["2000", "-4000"]),
                ("l", ["2000", "4000"]),
                ("Z", [])
            ],
            "M 0 0 m 0 0 L 0 0 l 0 0 H 0 h 0 V 0 v 0 C 0 0, 0 0, 0 0 c 0 0, 0 0, 0 0 S 0 0, 0 0 s 0 0, 0 0 Q 0 0, 0 0 q 0 0, 0 0 T 0 0 t 0 0 A 0 0 0 0 0 0 0 a 0 0 0 0 0 0 0 Z": [
                ("M", ["0", "0"]),
                ("m", ["0", "0"]),
                ("L", ["0", "0"]),
                ("l", ["0", "0"]),
                ("H", ["0"]),
                ("h", ["0"]),
                ("V", ["0"]),
                ("v", ["0"]),
                ("C", ["0", "0", "0", "0", "0", "0"]),
                ("c", ["0", "0", "0", "0", "0", "0"]),
                ("S", ["0", "0", "0", "0"]),
                ("s", ["0", "0", "0", "0"]),
                ("Q", ["0", "0", "0", "0"]),
                ("q", ["0", "0", "0", "0"]),
                ("T", ["0", "0"]),
                ("t", ["0", "0"]),
                ("A", ["0", "0", "0", "0", "0", "0", "0"]),
                ("a", ["0", "0", "0", "0", "0", "0", "0"]),
                ("Z", []),
            ]
        }
        for expected_output, input_val in test_vector.items():
            output = self.uut.path_string(input_val)
            self.assertEqual(output, expected_output)


    def test_path_end_point(self):
        test_vector={
            "M0,0": (0, 0),
            "M0,0 H1 V2": (1, 2),
            "M1,2 h1 v2": (2, 4),
            "M0,0 L-1,-3": (-1, -3),
            "M1,3 l-1,-3": (0, 0),
            "M1,1 m2,2": (3,3),
            "M0,0 m1,1 l1,1 c0 0, 0 0, 1 1 s0 0, 1 1 q 0 0, 1 1 t 0 0, 1 1 a 0 0 0 0 0 1 1": (7, 7),
            "C0 0, 0 0, 1 1": (1, 1),
            "S0 0, 1 1": (1, 1),
            "Q 0 0, 1 1": (1, 1),
            "T 0 0, 1 1": (1, 1),
            "A 0 0 0 0 0 1 1": (1, 1)
        }
        for input_val, expected_output in test_vector.items():
            output = self.uut.path_end_point(self.uut.path_parts(input_val))
            self.assertEqual(output, expected_output)

    def test_path_to_point(self):
        test_vector = {
            "M 0 0": ((10, -10), "M 10 -10"),
            "M 0 0 H 1 V 2": ((0, 0), "M 0 0 H 0 V 0"),
            "M 1 2 h 1 v 2": ((2, 4), "M 2 4 h 0 v 0"),
            "M 0 0 L -1 -3": ((-1, -3), "M -1 -3 L -1 -3"),
            "M 1 3 l -1 -3": ((0, 0), "M 0 0 l 0 0"),
            "M 1 1 m 2 2": ((3,3), "M 3 3 m 0 0"),
            "M 0 0 m 1 1 l 1 1 c 0 0, 0 0, 1 1 s 0 0, 1 1 q 0 0, 1 1 t 0 0 t 1 1 a 0 0 0 0 0 1 1": ((4, 5), 
            "M 4 5 m 0 0 l 0 0 c 0 0, 0 0, 0 0 s 0 0, 0 0 q 0 0, 0 0 t 0 0 t 0 0 a 0 0 0 0 0 0 0"),
            "C 0 0, 0 0, 1 1": ((2, 2), "C 2 2, 2 2, 2 2"),
            "S 0 0, 1 1": ((3, 4), "S 3 4, 3 4"),
            "Q 0 0, 1 1": ((5, 6), "Q 5 6, 5 6"),
            "T 0 0, 1 1": ((7, 8), "T 7 8 T 7 8"),
            "A 0 0 0 0 0 1 1": ((9, 0), "A 0 0 0 0 0 9 0")

        }

        for input_val, (point, expected_output) in test_vector.items():
            output = self.uut.path_string(
                        self.uut.path_to_point(
                            self.uut.path_parts(input_val), point))
            self.assertEqual(output, expected_output)

    def test_match_paths(self):
        test_vector = [
            ("Hello", "Hello"),
            ("abcdef", "abcdefghij"),
            ("abcdef", "defghij"),
            ("abcdef", "ghij"),
            ("ababab", "abcabab"),
            ("abca", "acba"),
            ("abaca", "acba"),
            ("acba", "abaca")
        ]
        for path_a, path_b in test_vector:
            out_a, out_b = self.uut.match_paths(path_a, path_b)
            self.assertEqual(len(out_a), len(out_b), "match_paths returned different length lists")
            orig_a = list(i for i in out_a if i >= 0)
            orig_b = list(i for i in out_b if i >= 0)
            self.assertEqual(orig_a, list(range(len(path_a))), "New path shape is different to old path shape")
            self.assertEqual(orig_b, list(range(len(path_b))), "New path shape is different to old path shape")

    @staticmethod
    def _path_commands_match(path1, path2):
        for (command1, args1), (command2, args2) in zip(chain(*path1), chain(*path2)):
            if command1 != command2:
                return False
        return True

