#!/usr/bin/env python
from TweenSVG import tween_svgs_from_filenames
from xml.etree import ElementTree as ElementTreeModule

#filenames = ["frame1.svg", "frame2.svg"]
#filenames = ["test_inputs/test1/frame1.svg", "test_inputs/test1/frame2.svg"]
filenames = ["test_inputs/dot1/frame1.svg", "test_inputs/dot1/frame2.svg"]

count = 0
for tween in tween_svgs_from_filenames(filenames):
    tween.write("tween%04d.svg" % (count), xml_declaration=True,encoding='utf-8', method='xml', default_namespace="http://www.w3.org/2000/svg")
    count += 1
