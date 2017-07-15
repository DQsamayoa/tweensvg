from defusedxml.ElementTree import parse
from xml.etree import ElementTree as ElementTreeModule
from xml.etree.ElementTree import ElementTree # Dr Watson
from xml.etree.ElementTree import Element
import itertools
import re

ElementTreeModule.register_namespace('', "http://www.w3.org/2000/svg")

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def _tagname(tag):
    m = re.match("^(?:\{[^{]*})?(.*)$", tag)
    if not m:
        raise ValueError("Not a valid [namespaced] xml tag name")
    return m.groups()[0]

class Tweener():
    def __init__(self, duration="10s"):
        self.duration = duration
        self.keyframes = []

    def add_keyframe(self, keyframe):
        if not isinstance(keyframe, ElementTree):
            raise TypeError("keyframe must be an ElementTree object")
        self.keyframes.append(keyframe)

    def add_keyframe_from_file(self, filename):
        self.add_keyframe(parse(filename))

    def _attr_diff(self, from_attrs, to_attrs):
        anim_from = {}
        anim_to = {}
        for from_attr in from_attrs:
            to_attr_val = to_attrs.get(from_attr, None)
            if from_attrs[from_attr] != to_attr_val:
                anim_from[from_attr] = from_attrs[from_attr]
                anim_to[from_attr] = to_attr_val
            if to_attr_val is None:
                # Attribute has gone :(
                pass
        for to_attr in to_attrs:
            if to_attr not in anim_from:
                # Attribute has appeared :S
                pass
        return anim_from, anim_to
            

    def _animate_tags(self, from_attrs, to_attrs):
        for attr, from_val in from_attrs.items():
            to_val = to_attrs[attr]
            animtag = Element("animate",
                 {
                    "attributeType": "XML",
                    "attributeName": attr,
                    "from": from_val,
                    "to": to_val,
                    "dur": self.duration,
                    "repeatCount": "indefinite"
                })
            yield animtag

    def _tween_elements(self, from_element: Element, to_element: Element):
        result_element = Element(from_element.tag, from_element.attrib)
        result_element.text = from_element.text
        result_element.tail = from_element.tail
        for sub_from_element in from_element:
            anim_tags = []
            eid = sub_from_element.attrib.get('id', None)
            tagname = sub_from_element.tag
            sub_to_element = to_element.find(sub_from_element.tag)
            if sub_to_element is None:
                # TODO animate fade out
                pass
            else:
                from_attrs, to_attrs = self._attr_diff(sub_from_element.attrib, sub_to_element.attrib)
                if from_attrs == to_attrs and from_attrs == {}:
                    pass # TODO
                else:
                    anim_tags = self._animate_tags(from_attrs, to_attrs)
            tweened_sub_element = self._tween_elements(sub_from_element, sub_to_element)
            for anim_tag in anim_tags:
                tweened_sub_element.append(anim_tag)
            result_element.append(tweened_sub_element)
        return result_element

    def _tween(self, from_svg, to_svg):
        element = self._tween_elements(from_svg.getroot(), to_svg.getroot())
        result = ElementTree(element=element)
        return result

    def _namespace_fixup(self, elements):
        """
            This is workaround for a bug in ElementTree
            Recursively prepend namespaces to all tags and attributes
        """
        for element in elements:
            if not "{" in element.tag:
                element.tag = "{http://www.w3.org/2000/svg}%s" % (element.tag)
            replacements = {}
            for attr in element.attrib:
                if not "{" in attr:
                    replacements[attr] = "{http://www.w3.org/2000/svg}%s" % (attr)
            for replace, with_this in replacements.items():
                element.attrib[with_this] = element.attrib[replace]
                del element.attrib[replace]
            self._namespace_fixup(element)

    def tweens(self):
        for a, b in pairwise(self.keyframes):
            tween = self._tween(a, b)
            self._namespace_fixup([tween.getroot()])
            yield tween
            
