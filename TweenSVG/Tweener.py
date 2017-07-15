from copy import deepcopy
import itertools
import re
from defusedxml.ElementTree import parse
from xml.etree import ElementTree as ElementTreeModule
from xml.etree.ElementTree import ElementTree # Dr Watson
from xml.etree.ElementTree import Element

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

def _value_unit(string):
    m = re.match(r"([\d.]+)([^\d]*)", string)
    if not m:
        raise ValueError("invalid dimension value '%s'" % (string))
    g = m.groups()
    return float(g[0]), g[1]

def _to_unit_val(value, unit):
    return "%f%s"%(value, unit)

class Tweener():
    def __init__(self, duration="5s", group_matching=False):
        self.duration = duration
        self.group_matching = group_matching
        self.maxwidth = 0
        self.maxheight = 0
        self.widthunit = None
        self.heightunit = None
        self.keyframes = []

    def add_keyframe(self, keyframe):
        if not isinstance(keyframe, ElementTree):
            raise TypeError("keyframe must be an ElementTree object")
        self.keyframes.append(keyframe)
        root_attrs = keyframe.getroot().attrib
        if 'width' in root_attrs:
            width, widthunit = _value_unit(root_attrs['width'])
            if self.widthunit is None or self.widthunit == widthunit:
                self.widthunit = widthunit
            else:
                raise ValueError("Mixed units in keyframe dimensions")
        if 'height' in root_attrs:
            height, heightunit = _value_unit(root_attrs['height'])
            if self.heightunit is None or self.heightunit == heightunit:
                self.heightunit = heightunit
            else:
                raise ValueError("Mixed units in keyframe dimensions")

        self.maxwidth = max(self.maxwidth, width)
        self.maxheight = max(self.maxheight, height)

        print(root_attrs)

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
        assert "id" not in anim_from, "Erm, something's really wrong, I can't animate an id attribute!?!?!?!?!?"
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

    def _fade_animation(self, direction):
        if direction not in {-1, 1}:
            raise ValueError("Direction must be 1 or -1")
        (fromval, toval) = ("1", "0") if direction == -1 else ("0", "1")
        from_attr = {"opacity": fromval}
        to_attr = {"opacity": toval}
        return self._animate_tags(from_attr, to_attr)

    def _fade_in_animation(self):
        return self._fade_animation(1)

    def _fade_out_animation(self):
        return self._fade_animation(-1)

    def _tween_elements(self, from_element: Element, to_element: Element, group_merge=False):
        result_element = Element(from_element.tag, from_element.attrib)
        result_element.text = from_element.text
        result_element.tail = from_element.tail
        done_ids = []
        merged_to_elements = []
        for sub_from_element in from_element:
            anim_tags = []
            group_merge_next = False
            eid = sub_from_element.attrib.get('id', None)
            tweened_sub_element = None
            if eid is None:
                if not group_merge:
                    # Cannot tween, just fade out
                    anim_tags = self._fade_out_animation()
                    tweened_sub_element = deepcopy(sub_from_element)
                else:
                    found = False
                    # Try to merge this with something from the "to" elements
                    for sub_to_element in to_element:
                        if sub_to_element.tag == sub_from_element.tag:
                            if sub_to_element not in merged_to_elements:
                                # Merge!
                                from_attrs, to_attrs = self._attr_diff(sub_from_element.attrib, sub_to_element.attrib)
                                anim_tags = self._animate_tags(from_attrs, to_attrs)
                                tweened_sub_element = self._tween_elements(sub_from_element, sub_to_element, group_merge=True)
                                found = True
                                merged_to_elements.append(sub_to_element)
                                break
                    if not found:
                        # Couldn't merge, just fade out...
                        anim_tags = self._fade_out_animation()
                        tweened_sub_element = deepcopy(sub_from_element)
            else:
                done_ids.append(eid)
                tagname = sub_from_element.tag
                if self.group_matching and _tagname(tagname) == 'g':
                    # Match children without IDs in the order they appear in the file
                    group_merge_next = True
                    pass
                sub_to_elements = to_element.findall(sub_from_element.tag)
                sub_to_element = None
                for maybe_sub_to_element in sub_to_elements:
                    if maybe_sub_to_element.attrib.get('id', None) == eid:
                        sub_to_element = maybe_sub_to_element
                if sub_to_element is None:
                    # No mathching element in from, animate fade out
                    anim_tags = self._fade_out_animation()
                    tweened_sub_element = deepcopy(sub_from_element)
                else:
                    from_attrs, to_attrs = self._attr_diff(sub_from_element.attrib, sub_to_element.attrib)
                    anim_tags = self._animate_tags(from_attrs, to_attrs)
                    tweened_sub_element = self._tween_elements(sub_from_element, sub_to_element, group_merge=group_merge_next)
            for anim_tag in anim_tags:
                tweened_sub_element.append(anim_tag)
            result_element.append(tweened_sub_element)

        for sub_to_element in to_element:
            eid = sub_to_element.attrib.get('id', None)

            if ((eid is None) and group_merge and (sub_to_element not in merged_to_elements)) or (eid is not None and eid not in done_ids):
                # This is a new element, fade it in
                fade_in_element = deepcopy(sub_to_element)
                for anim in self._fade_in_animation():
                    fade_in_element.append(anim)
                result_element.append(fade_in_element)
        return result_element

    def _tween(self, from_svg, to_svg):
        element = self._tween_elements(from_svg.getroot(), to_svg.getroot())
        element.attrib['width'] = _to_unit_val(self.maxwidth, self.widthunit)
        element.attrib['height'] = _to_unit_val(self.maxheight, self.heightunit)
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
            
