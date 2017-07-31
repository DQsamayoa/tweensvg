"""
    Test module for SVGUtils module
"""
import unittest
from TweenSVG import AnimationGenerator
from itertools import chain
from xml.etree.ElementTree import Element

def elements_equal(el1: Element, el2: Element):
    print(el1)
    print(el2)
    if any([
            el1.tag != el2.tag,
            el1.text != el2.text,
            el1.tail != el2.tail,
            el1.attrib != el2.attrib,
            any(not elements_equal(child1, child2) for child1, child2 in zip(el1.getchildren(), el2.getchildren()))
        ]):
        return False
    return True

class AnimationGeneratorTests(unittest.TestCase):
    """ 
        Test class for SVGUtils class
    """

    def __init__(self, args):
        unittest.TestCase.__init__(self, args)

    def test_animate_tags(self):
        test_vector=[
            (
                {"width": "4px"},
                {"width": "10px"},
                [Element("animate", {"from": "4px",
                                     "to": "10px",
                                     "attributeName": "width",
                                     "attributeType": "XML",
                                     "begin": ""})]
            )
        ]
        uut = AnimationGenerator.AnimationGenerator("5s")
        for from_val, to_val, expected_outputs in test_vector:
            outputs = list(uut.animate_tags(from_val, to_val))
            for output, expected_output in zip(outputs, expected_outputs):
                print(output)
                self.assertTrue(elements_equal(output, expected_output))
