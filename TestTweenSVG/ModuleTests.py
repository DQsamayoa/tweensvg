"""
    Test the TweenSVG module
"""
import unittest
from tempfile import NamedTemporaryFile
import TweenSVG
import itertools
from itertools import chain
from xml.etree.ElementTree import ElementTree


class ModuleTests(unittest.TestCase):
    """ 
        Test class for SVGUtils class
    """

    BASIC_FRAME_1 = r"""
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg
           xmlns="http://www.w3.org/2000/svg"
           version="1.1"
           id="svg4989"
           viewBox="0 0 354.33071 354.33071"
           height="100mm"
           width="100mm">
          <g
             transform="translate(0,-698.0315)"
             id="layer1">
            <ellipse
               ry="46.467018" rx="45.961941"
               cy="778.6109" cx="74.246216"
               id="path5556"
               style="fill:#ff0000;fill-opacity:1;stroke:none;stroke-width:14.17300034;stroke-miterlimit:4;stroke-dasharray:none" />
            <ellipse
               ry="52.022858" rx="49.497475"
               cy="971.04492" cx="73.741135"
               id="path5558"
               style="fill:#ffff00;fill-opacity:1;stroke:none;stroke-width:14.17300034;stroke-miterlimit:4;stroke-dasharray:none" />
            <ellipse
               ry="52.527931" rx="50.002552"
               cy="777.60077" cx="279.30722"
               id="path5560"
               style="fill:#0000ff;fill-opacity:1;stroke:none;stroke-width:14.17300034;stroke-miterlimit:4;stroke-dasharray:none" />
          </g>
        </svg>
    """
    BASIC_FRAME_2 = r"""
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg
           xmlns="http://www.w3.org/2000/svg"
           version="1.1"
           id="svg4989"
           viewBox="0 0 354.33071 354.33071"
           height="100mm"
           width="100mm">
          <g
             transform="translate(0,-698.0315)"
             id="layer1">
            <ellipse
               ry="52.022858" rx="49.497475"
               cy="762.58221" cx="289.4693"
               id="path5558"
               style="fill:#ffff00;fill-opacity:1;stroke:none;stroke-width:14.17300034;stroke-miterlimit:4;stroke-dasharray:none" />
            <ellipse
               ry="52.527931" rx="50.002552"
               cy="976.0036" cx="74.1978"
               id="path5560"
               style="fill:#0000ff;fill-opacity:1;stroke:none;stroke-width:14.17300034;stroke-miterlimit:4;stroke-dasharray:none" />
            <ellipse
               ry="46.467018" rx="45.961941"
               cy="977.6109" cx="277.79196"
               id="path5556-3"
               style="fill:#00ff00;fill-opacity:1;stroke:none;stroke-width:14.17300034;stroke-miterlimit:4;stroke-dasharray:none" />
          </g>
        </svg>
    """
    def __init__(self, args):
        unittest.TestCase.__init__(self, args)
        self.uut = TweenSVG

    def test_tween_svgs_from_filenames(self):
        with NamedTemporaryFile(mode="w+") as file1, NamedTemporaryFile(mode="w+") as file2:
            file1.write(ModuleTests.BASIC_FRAME_1.strip())
            file1.flush()
            file2.write(ModuleTests.BASIC_FRAME_2.strip())
            file2.flush()
            tweens = TweenSVG.tween_svgs_from_filenames([file1.name, file2.name])
            for tween in tweens:
                self.assertIsInstance(tween, ElementTree)

    def try_tweening_files(self, files):
        for group, fadeout, fadein in itertools.product([True, False], repeat=3):
           tweens = TweenSVG.tween_svgs_from_filenames(files,
                group_matching=group, fadeout_early=fadeout, fadein_late=fadein)
           for tween in tweens:
               self.assertIsInstance(tween, ElementTree)


    def test_tween_svgs_from_filenames2(self):
        self.try_tweening_files([
            "test_inputs/dot1/frame1.svg",
            "test_inputs/dot1/frame2.svg",
            "test_inputs/dot1/frame3.svg"
        ])

    def test_tween_svgs_from_filenames3(self):
        self.try_tweening_files([
            "test_inputs/dot2/frame1.svg",
            "test_inputs/dot2/frame2.svg"
        ])

    def test_tween_svgs_from_filenames4(self):
        self.try_tweening_files([
            "test_inputs/test1/frame1.svg",
            "test_inputs/test1/frame2.svg"
        ])

    def test_tween_svgs_from_filenames5(self):
        self.try_tweening_files([
            "test_inputs/test2/frame1.svg",
            "test_inputs/test2/frame2.svg",
            "test_inputs/test2/frame3.svg"
        ])

    def test_tween_svgs_from_filenames6(self):
        self.try_tweening_files([
            "test_inputs/test3/paths1.svg",
            "test_inputs/test3/paths2.svg"
        ])

    def test_tween_svgs_from_filenames7(self):
        self.try_tweening_files([
            "test_inputs/test4/frame1.svg",
            "test_inputs/test4/frame2.svg"
        ])
