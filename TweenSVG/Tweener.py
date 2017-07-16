from copy import deepcopy
import itertools
from defusedxml.ElementTree import parse
from xml.etree import ElementTree as ElementTreeModule
from xml.etree.ElementTree import ElementTree # Dr Watson
from xml.etree.ElementTree import Element
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

def _value_unit(string):
    m = re.match(r"([\d.]+)([^\d]*)", string)
    if not m:
        raise ValueError("invalid dimension value '%s'" % (string))
    g = m.groups()
    return float(g[0]), g[1]

def _to_unit_val(value, unit):
    return "%f%s"%(value, unit)

def _viewbox_vals(string):
    m = re.match(r"(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*)", string)
    if not m:
        raise ValueError("invalid viewbox string")
    groups = m.groups()
    return tuple(float(groups[i]) for i in range(4))

def _to_viewbox_val(left, top, width, height):
    return "%f %f %f %f" % (left, top, width, height)

def _transforms(string):
    matches = re.findall(r"(translate|rotate|scale|matrix|skew(?:x|y))\(([^)]+)\)", string)
    return {transform: args for transform, args in matches}

class Tweener():
    def __init__(self, duration="5s", group_matching=False, fadein_late=False, fadeout_early=False):
        self.duration = duration
        self.fadein_duration = "1s"
        self.fadeout_duration = "1s"
        self.fadein_late = fadein_late
        self.fadeout_early = fadeout_early
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

    def add_keyframe(self, keyframe):
        """ Add a keyframe to the animation. Units must match other frames """
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
            self.maxwidth = max(self.maxwidth, width)
        if 'height' in root_attrs:
            height, heightunit = _value_unit(root_attrs['height'])
            if self.heightunit is None or self.heightunit == heightunit:
                self.heightunit = heightunit
            else:
                raise ValueError("Mixed units in keyframe dimensions")
            self.maxheight = max(self.maxheight, height)

        if 'viewBox' in root_attrs:
            vb = root_attrs['viewBox']
            left, top, width, height = _viewbox_vals(vb)
            self.min_vb_top = min(self.min_vb_top, top)
            self.min_vb_left = min(self.min_vb_left, left)
            self.max_vb_width = max(self.max_vb_width, width)
            self.max_vb_height = max(self.max_vb_height, height)

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
            

    def _animate_tags_custom(self, from_attrs, to_attrs, begin=None, eid=None, dur=None):
        def common_attrs(animtag):
            if begin is not None:
                animtag.attrib['begin'] = begin
                animtag.attrib['fill'] = 'freeze'
            if eid is None:
                animtag.attrib['id'] = "tween_%d" % (self.animation_number)
                self.animation_number += 1
            else:
                animtag.attrib['id'] = eid
        if dur is None:
            dur = self.duration
        for attr, from_val in from_attrs.items():
            to_val = to_attrs[attr]
            if attr == 'transform':
                # Transforms are handled with animateTransform tags
                from_transforms = _transforms(from_val)
                to_transforms = _transforms(to_val)
                for trans_type, from_args in from_transforms.items():
                    if trans_type in to_transforms:
                        to_args = to_transforms[trans_type]
                        if from_args != to_args:
                            animtag = Element("animateTransform",
                                {
                                    "attriuteType": "XML",
                                    "attributeName": "transform",
                                    "type": trans_type,
                                    "from": from_args,
                                    "to": to_args,
                                    "dur": dur,
                                    #"repeatCount": "indefinite"
                                })
                            common_attrs(animtag)
                            yield animtag
            else:
                animtag = Element("animate",
                     {
                        "attributeType": "XML",
                        "attributeName": attr,
                        "from": from_val,
                        "to": to_val,
                        "dur": dur,
                        #"repeatCount": "indefinite"
                    })
                common_attrs(animtag)
                yield animtag

    def _animate_tags(self, from_attrs, to_attrs):
        return self._animate_tags_custom(from_attrs, to_attrs, begin="tween_transition.begin")

    def _fade_animation(self, direction, opacity, begin=None, dur=None):
        if direction not in {-1, 1}:
            raise ValueError("Direction must be 1 or -1")
        (fromval, toval) = (opacity, "0") if direction == -1 else ("0", opacity)
        from_attr = {"opacity": fromval}
        to_attr = {"opacity": toval}
        return self._animate_tags_custom(from_attr, to_attr, begin=begin, dur=dur)

    def _fade_in_animation(self, opacity):
        return self._fade_animation(1, opacity, begin="tween_fadein.begin", dur=self.fadein_duration)

    def _fade_out_animation(self, opacity):
        return self._fade_animation(-1, opacity, begin="tween_fadeout.begin", dur=self.fadeout_duration)

    def _fade_out_element(self, element):
        opacity = element.attrib.get("opacity", "1")
        element.attrib['opacity'] = opacity
        return self._fade_out_animation(opacity)


    def _fade_in_element(self, element):
        opacity = element.attrib.get("opacity", "1")
        element.attrib['opacity'] = "0"
        return self._fade_in_animation(opacity)

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
                        tweened_sub_element = deepcopy(sub_from_element)
                        #anim_tags = self._fade_out_animation()
                        anim_tags = self._fade_out_element(tweened_sub_element)
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
                    #anim_tags = self._fade_out_animation()
                    tweened_sub_element = deepcopy(sub_from_element)
                    anim_tags = self._fade_out_element(tweened_sub_element)
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
                for anim in self._fade_in_element(fade_in_element):
                    fade_in_element.append(anim)
                result_element.append(fade_in_element)
        return result_element

    def _tween(self, from_svg, to_svg, extras=None):
        element = self._tween_elements(from_svg.getroot(), to_svg.getroot())
        element.attrib['width'] = _to_unit_val(self.maxwidth, self.widthunit)
        element.attrib['height'] = _to_unit_val(self.maxheight, self.heightunit)
        element.attrib['viewBox'] = _to_viewbox_val(self.min_vb_left, self.min_vb_top, self.max_vb_width, self.max_vb_height)
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
                    replacements[attr] = "{http://www.w3.org/2000/svg}%s" % (attr)
            for replace, with_this in replacements.items():
                element.attrib[with_this] = element.attrib[replace]
                del element.attrib[replace]
            self._namespace_fixup(element)

    def _sync_element(self):
        # Create an invisible dummy element to contain
        # root animations for synchronisation
        invisible = Element("g", {"opacity": "0"})
        text = Element("text", {"y": "20", "opacity":"0"})
        text.text = "Test"
        common_attrs = {"attributeName": "opacity", "attributeType": "XML", "from":"0", "to":"1"}
        fadeout_attribs = {"id": "tween_fadeout",
                           "begin": "0s",
                           "dur": self.fadeout_duration,
                           **common_attrs}
        transition_attribs = {"id": "tween_transition",
                              "begin": "0s; tween_fadein.end",
                              "dur": self.duration,
                              **common_attrs}
        fadein_attribs = {"id": "tween_fadein",
                          "begin": "tween_transition.start",
                          "dur": self.fadein_duration,
                          **common_attrs}
        if self.fadeout_early:
            # Delay the main transitions until fadout had ended
            transition_attribs['begin'] = "tween_fadeout.end"
        if self.fadein_late:    
            fadein_attribs['begin'] = "tween_transition.end"

        #if not self.fadein_late and not self.fadeout_early:
        #    transition_attribs['repeatCount'] = 'indefinite'
        start_fadein = Element("animate", fadein_attribs)
        start_transition = Element("animate", transition_attribs)
        start_fadeout = Element("animate", fadeout_attribs)
        text.append(start_fadein)
        text.append(start_transition)
        text.append(start_fadeout)
        invisible.append(text)
        return invisible

    def tweens(self):
        for a, b in pairwise(self.keyframes):
            sync_element = self._sync_element()
            tween = self._tween(a, b, extras=[sync_element])
            self._namespace_fixup([tween.getroot()])
            yield tween
            
