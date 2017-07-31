"""
    Test module for SVGUtils module
"""
import unittest
from TweenSVG import AnimationGenerator
from itertools import chain
from xml.etree.ElementTree import Element

def element_diff(el1: Element, el2: Element):
    for attrname in [
            "tag",
            "text",
            "tail",
            "attrib"
        ]:
        attr1 = getattr(el1, attrname)
        attr2 = getattr(el2, attrname)
        if attr1 != attr2:
            return False, "%s differs: `%s` != `%s`" % (attrname, attr1, attr2)
    for index, (child1, child2) in enumerate(zip(el1.getchildren(), el2.getchildren())):
        equal, difftext = element_diff(child1, child2)
        if not equal:
            return False, "Child %d differs: %s" % (index, difftext)
    return True, None
    

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
                [Element("animate", {"id":"tween_0",
                                     "from": "4px",
                                     "to": "10px",
                                     "dur": "5s",
                                     "attributeName": "width",
                                     "attributeType": "XML",
                                     "fill": "freeze",
                                     "begin": "tween_transition.begin"})]
            ),
            (
                {"transform": "scale(1)"},
                {"transform": "scale(20)"},
                [Element("animateTransform", {"id":"tween_1",
                                              "from": "1",
                                              "to": "20",
                                              "type": "scale",
                                              "dur": "5s",
                                              "attributeName": "transform",
                                              "attributeType": "XML",
                                              "fill": "freeze",
                                              "begin": "tween_transition.begin"})]
            ),
            (
                {"d": "M0 0L1 1"},
                {"d": "M0 0L1 2"},
                [Element("animate", {"id":"tween_2",
                                     "from": "M 0 0 L 1 1",
                                     "to": "M 0 0 L 1 2",
                                     "dur": "5s",
                                     "attributeName": "d",
                                     "attributeType": "XML",
                                     "fill": "freeze",
                                     "begin": "tween_transition.begin"})]
            )
        ]
        uut = AnimationGenerator.AnimationGenerator("5s")
        for from_val, to_val, expected_outputs in test_vector:
            outputs = list(uut.animate_tags(from_val, to_val))
            for output, expected_output in zip(outputs, expected_outputs):
                equal, difftext = element_diff(output, expected_output)
                self.assertTrue(equal, msg=difftext)
