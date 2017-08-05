"""
    Test module for Tweener module
"""
import unittest
from TweenSVG.Tweener import Tweener
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element

class TweenerTests(unittest.TestCase):
    """ 
        Test class for SVGUtils class
    """

    def __init__(self, args):
        unittest.TestCase.__init__(self, args)
        self.uut = Tweener

    def test_add_keyframe(self):
        TestTweener = self.uut()
        with self.assertRaises(TypeError):
            TestTweener.add_keyframe(None)

    def test_add_keyframe2(self):
        TestTweener = self.uut()
        mm_svg = ElementTree(Element("svg", attrib={'width': '2mm', 'height':'2mm'}))
        px_svg = ElementTree(Element("svg", attrib={'width': '10px', 'height':'10px'}))
        with self.assertRaises(ValueError):
            TestTweener.add_keyframe(mm_svg)
            TestTweener.add_keyframe(px_svg)

    def test_add_keyframe3(self):
        TestTweener = self.uut()
        mm_svg = ElementTree(Element("svg", attrib={'width': '2mm', 'height':'2mm'}))
        px_svg = ElementTree(Element("svg", attrib={'width': '2mm', 'height':'10px'}))
        with self.assertRaises(ValueError):
            TestTweener.add_keyframe(mm_svg)
            TestTweener.add_keyframe(px_svg)
