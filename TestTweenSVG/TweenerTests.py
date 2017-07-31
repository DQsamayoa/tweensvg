"""
    Test module for Tweener module
"""
import unittest
from TweenSVG.Tweener import Tweener

class TweenerTests(unittest.TestCase):
    """ 
        Test class for SVGUtils class
    """

    def __init__(self, args):
        unittest.TestCase.__init__(self, args)
        self.uut = Tweener

    def test_animate_tags_custom(self):
        TestTweener = self.uut()
        TestTweener.animate_tags_custom(from_attrs, to_attrs)
        pass
