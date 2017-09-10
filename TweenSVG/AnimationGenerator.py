import itertools
from defusedxml.ElementTree import parse
from xml.etree import ElementTree as ElementTreeModule
from xml.etree.ElementTree import ElementTree # Dr Watson
from xml.etree.ElementTree import Element
import re

from TweenSVG.SVGUtils import SVGUtils as SVU

ElementTreeModule.register_namespace('', "http://www.w3.org/2000/svg")

class AnimationGenerator():
    def __init__(self, duration="5s", fadein_late=False, fadeout_early=False):
        self.animation_number = 0
        self.fadein_duration = "1s"
        self.fadeout_duration = "1s"
        self.duration = duration
        self.fadein_late = fadein_late
        self.fadeout_early = fadeout_early

    def attr_diff(self, from_attrs, to_attrs):
        anim_from = {}
        anim_to = {}
        for from_attr in from_attrs:
            to_attr_val = to_attrs.get(from_attr, "")
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

    def animate_tags_custom(self, from_attrs, to_attrs, begin=None, eid=None, dur=None):
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
            # For path sequences, make the paths tweenable
            if attr == 'd':
                from_parts = SVU.path_parts(from_val)
                to_parts = SVU.path_parts(to_val)
                from_parts, to_parts = SVU.tweenable_paths(from_parts, to_parts)
                from_val = SVU.path_string(from_parts)
                to_val = SVU.path_string(to_parts)

            if attr == 'transform':
                # Transforms are handled with animateTransform tags
                from_transforms = SVU.transforms(from_val)
                to_transforms = SVU.transforms(to_val)
                if len(from_transforms) == len(to_transforms):
                
                    for (from_type, from_args), (to_type, to_args) in zip(from_transforms, to_transforms):
                        if from_type != to_type:
                            break
                        if from_args != to_args:
                            animtag = Element("animateTransform",
                                              {
                                                  "attributeType": "XML",
                                                  "attributeName": "transform",
                                                  "type": from_type,
                                                  "from": from_args,
                                                  "to": to_args,
                                                  "dur": dur,
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

    def animate_tags(self, from_attrs, to_attrs):
        return self.animate_tags_custom(from_attrs, to_attrs, begin="tween_transition.begin")

    def _fade_animation(self, direction, opacity, begin=None, dur=None):
        if direction not in {-1, 1}:
            raise ValueError("Direction must be 1 or -1")
        (fromval, toval) = (opacity, "0") if direction == -1 else ("0", opacity)
        from_attr = {"opacity": fromval}
        to_attr = {"opacity": toval}
        return self.animate_tags_custom(from_attr, to_attr, begin=begin, dur=dur)

    def fade_in_animation(self, opacity, begin="tween_fadein.begin"):
        return self._fade_animation(1, opacity, begin=begin, dur=self.fadein_duration)

    def fade_out_animation(self, opacity, begin="tween_fadeout.begin"):
        return self._fade_animation(-1, opacity, begin=begin, dur=self.fadeout_duration)

    def fade_out_element(self, element, transition_phase=False):
        opacity = element.attrib.get("opacity", "1")
        element.attrib['opacity'] = opacity
        if transition_phase:
            return self.fade_out_animation(opacity, begin="tween_transition.begin")
        else:
            return self.fade_out_animation(opacity)

    def fade_in_element(self, element, transition_phase=False):
        opacity = element.attrib.get("opacity", "1")
        element.attrib['opacity'] = "0"
        if transition_phase:
            return self.fade_in_animation(opacity, begin="tween_transition.begin")
        else:
            return self.fade_in_animation(opacity)

    def sync_element(self):
        # Create an invisible dummy element to contain
        # root animations for synchronisation
        invisible = Element("g", {"opacity": "0"})
        text = Element("text", {"y": "20", "opacity": "0"})
        text.text = "Test"
        common_attrs = {"attributeName": "opacity",
                        "attributeType": "XML",
                        "from": "0",
                        "to": "1"
                       }
        fadeout_attribs = {"id": "tween_fadeout",
                           "begin": "0s",
                           "dur": self.fadeout_duration,
                          }
        transition_attribs = {"id": "tween_transition",
                              "begin": "0s; tween_fadein.end",
                              "dur": self.duration,
                             }
        fadein_attribs = {"id": "tween_fadein",
                          "begin": "tween_transition.start",
                          "dur": self.fadein_duration,
                         }
        # add the common attrs to all other attribute dicts
        for attr_dict in [fadeout_attribs, transition_attribs, fadein_attribs]:
            for key in common_attrs:
                attr_dict[key] = common_attrs[key]
        if self.fadeout_early:
            # Delay the main transitions until fadout had ended
            transition_attribs['begin'] = "tween_fadeout.end"
        if self.fadein_late:
            fadein_attribs['begin'] = "tween_transition.end"

        start_fadein = Element("animate", fadein_attribs)
        start_transition = Element("animate", transition_attribs)
        start_fadeout = Element("animate", fadeout_attribs)
        text.append(start_fadein)
        text.append(start_transition)
        text.append(start_fadeout)
        invisible.append(text)
        return invisible
