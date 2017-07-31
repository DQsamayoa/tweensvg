from copy import deepcopy
import itertools
from defusedxml.ElementTree import parse
from xml.etree import ElementTree as ElementTreeModule
from xml.etree.ElementTree import ElementTree # Dr Watson
from xml.etree.ElementTree import Element
import re

from TweenSVG.SVGUtils import SVGUtils as SVU
from TweenSVG.AnimationGenerator import AnimationGenerator as AnimGen

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
    def __init__(self, duration="5s", group_matching=False, fadein_late=False, fadeout_early=False):
        #self.duration = duration
        #self.fadein_late = fadein_late
        #self.fadeout_early = fadeout_early
        self.group_matching = group_matching
        self.maxwidth = 0
        self.maxheight = 0
        self.min_vb_top = 0
        self.min_vb_left = 0
        self.max_vb_width = 0
        self.max_vb_height = 0
        self.widthunit = None
        self.heightunit = None
        self.keyframes = []
        self.animation_number = 0
        self.anim_gen = AnimGen(duration, fadein_late=fadein_late, fadeout_early=fadeout_early)

    def add_keyframe(self, keyframe):
        """ Add a keyframe to the animation. Units must match other frames """
        if not isinstance(keyframe, ElementTree):
            raise TypeError("keyframe must be an ElementTree object")
        self.keyframes.append(keyframe)
        root_attrs = keyframe.getroot().attrib
        if 'width' in root_attrs:
            width, widthunit = SVU.value_unit(root_attrs['width'])
            if self.widthunit is None or self.widthunit == widthunit:
                self.widthunit = widthunit
            else:
                raise ValueError("Mixed units in keyframe dimensions")
            self.maxwidth = max(self.maxwidth, width)
        if 'height' in root_attrs:
            height, heightunit = SVU.value_unit(root_attrs['height'])
            if self.heightunit is None or self.heightunit == heightunit:
                self.heightunit = heightunit
            else:
                raise ValueError("Mixed units in keyframe dimensions")
            self.maxheight = max(self.maxheight, height)

        if 'viewBox' in root_attrs:
            vb = root_attrs['viewBox']
            left, top, width, height = SVU.viewbox_vals(vb)
            self.min_vb_top = min(self.min_vb_top, top)
            self.min_vb_left = min(self.min_vb_left, left)
            self.max_vb_width = max(self.max_vb_width, width)
            self.max_vb_height = max(self.max_vb_height, height)

    def add_keyframe_from_file(self, filename):
        self.add_keyframe(parse(filename))

    def _tween_elements(self, from_element: Element, to_element: Element, group_merge=False):
        result_element = Element(from_element.tag, from_element.attrib)
        result_element.text = from_element.text
        result_element.tail = from_element.tail

        done_ids = []
        merged_to_elements = []
        for sub_from_element in from_element:
            sub_to_element = None
            anim_tags = []
            group_merge_next = False
            eid = sub_from_element.attrib.get('id', None)
            tweened_sub_element = None
            tagname = sub_from_element.tag
            if eid is None:
                if not group_merge:
                    # Cannot tween, just fade out
                    tweened_sub_element = deepcopy(sub_from_element)
                    anim_tags = self._fade_out_element(tweened_sub_element)
                else:
                    found = False
                    # Try to merge this with something from the "to" elements
                    for sub_to_element in to_element:
                        if sub_to_element.tag == sub_from_element.tag:
                            if sub_to_element not in merged_to_elements:
                                # Merge!
                                from_attrs, to_attrs = self._attr_diff(
                                    sub_from_element.attrib, sub_to_element.attrib)
                                anim_tags = self.anim_gen.animate_tags(
                                    from_attrs, to_attrs)
                                tweened_sub_element = self._tween_elements(
                                    sub_from_element, sub_to_element, group_merge=True)
                                found = True
                                merged_to_elements.append(sub_to_element)
                                break
                    if not found:
                        # Couldn't merge, just fade out...
                        tweened_sub_element = deepcopy(sub_from_element)
                        #anim_tags = self._fade_out_animation()
                        anim_tags = self._fade_out_element(tweened_sub_element)
            else:
                done_ids.append(eid)
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
                    #anim_tags = self._fade_out_animation()
                    tweened_sub_element = deepcopy(sub_from_element)
                    anim_tags = self.anim_gen.fade_out_element(tweened_sub_element)
                else:
                    from_attrs, to_attrs = self.anim_gen.attr_diff(
                        sub_from_element.attrib, sub_to_element.attrib)
                    anim_tags = self.anim_gen.animate_tags(from_attrs, to_attrs)
                    tweened_sub_element = self._tween_elements(
                        sub_from_element, sub_to_element, group_merge=group_merge_next)
            double_tween = False
            if _tagname(tagname) == "text":
                # This is a text element
                if sub_to_element is not None and sub_from_element.text != sub_to_element.text: 
                    # Oh no! text needs tweening
                    double_tween = True
            if double_tween:
                # Take a copy of the tweened item
                tweened_sub_element_2 = deepcopy(tweened_sub_element)
                tweened_sub_element_2.text = sub_to_element.text
                # apply the animation now
                # Also fade out the old element:
                for anim_tag in anim_tags:
                    tweened_sub_element.append(anim_tag)
                    tweened_sub_element_2.append(anim_tag)
                for anim_tag in self.anim_gen.fade_out_element(tweened_sub_element, transition_phase=True):
                    tweened_sub_element.append(anim_tag)
                for anim_tag in self.anim_gen.fade_in_element(tweened_sub_element_2, transition_phase=True):
                    tweened_sub_element_2.append(anim_tag)
                anim_tags = [] # clear the animation tags, so we don't add them again later
                # Create a group for the two cross-faded elements
                group = Element("g")
                group.append(tweened_sub_element)
                group.append(tweened_sub_element_2)
                tweened_sub_element = group

            for anim_tag in anim_tags:
                tweened_sub_element.append(anim_tag)
            result_element.append(tweened_sub_element)

        for sub_to_element in to_element:
            eid = sub_to_element.attrib.get('id', None)

            if ((eid is None) and group_merge and (sub_to_element not in merged_to_elements)) or (eid is not None and eid not in done_ids):
                # This is a new element, fade it in
                fade_in_element = deepcopy(sub_to_element)
                for anim in self.anim_gen.fade_in_element(fade_in_element):
                    fade_in_element.append(anim)
                result_element.append(fade_in_element)
        return result_element

    def _tween(self, from_svg, to_svg, extras=None):
        element = self._tween_elements(from_svg.getroot(), to_svg.getroot())
        element.attrib['width'] = SVU.to_unit_val(
            self.maxwidth, self.widthunit)
        element.attrib['height'] = SVU.to_unit_val(
            self.maxheight, self.heightunit)
        element.attrib['viewBox'] = SVU.to_viewbox_val(
            self.min_vb_left, self.min_vb_top, self.max_vb_width, self.max_vb_height)
        if not all(value == 0 for value in [
                self.max_vb_height,
                self.max_vb_width,
                self.min_vb_left,
                self.min_vb_top
            ]):
            element.attrib['viewBox'] = SVU.to_viewbox_val(self.min_vb_left, self.min_vb_top, self.max_vb_width, self.max_vb_height)
        if extras is not None:
            for extra in extras:
                element.append(extra)
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
                    replacements[attr] = "{http://www.w3.org/2000/svg}%s" % (
                        attr)
            for replace, with_this in replacements.items():
                element.attrib[with_this] = element.attrib[replace]
                del element.attrib[replace]
            self._namespace_fixup(element)


    def tweens(self):
        for a, b in pairwise(self.keyframes):
            sync_element = self.anim_gen.sync_element()
            tween = self._tween(a, b, extras=[sync_element])
            self._namespace_fixup([tween.getroot()])
            yield tween
