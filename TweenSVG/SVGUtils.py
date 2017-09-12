"""
    Various SVG Parsing and transformation utilities
    These are generally for use within the Tweener module
    and so the API of this module will change if needed
    to satisfy Tweener.
"""
import re


def minimal_float_str(float_val):
    str_value = "%f" % (float(float_val))
    while str_value[-1] == '0' and str_value[-2] != '.':
        str_value = str_value[0:-1]
    if str_value[-2:] == '.0':
        str_value = str_value[0:-2]
    return str_value

class SVGUtils():
    """
        Utilities class containing functions for parsing and
        transforming SVG data.
    """

    @staticmethod
    def value_unit(string):
        """
            Parses an SVG dimension value and returns a tuple of two strings.
            The first string is the value and the second is the units.
        """
        m = re.match(r" *([\d\.]+) *([^\d\n]*) *", string)
        if not m:
            raise ValueError("invalid dimension value '%s'" % (string))
        g = m.groups()
        return float(g[0].strip()), g[1].strip()

    @staticmethod
    def to_unit_val(value, unit):
        """ Take a floating point value and a string unit and return an SVG dimension string """
        str_value = minimal_float_str(value)
        return "%s%s" % (str_value, unit)

    @staticmethod
    def viewbox_vals(string):
        """ Parse an SVG viewbox string and return a 4-tuple of (left, top, widht, height) floats """
        m = re.match(
            r"(-?\d+(?:\.\d)?\d*) *[, ] *(-?\d+(?:\.\d)?\d*) *[, ] *(-?\d+(?:\.\d)?\d*) *[, ] *(-?\d+(?:\.\d)?\d*)", string)
        if not m:
            raise ValueError("invalid viewbox string")
        groups = m.groups()
        return tuple(float(groups[i]) for i in range(4))

    @staticmethod
    def to_viewbox_val(left, top, width, height):
        """ Return an SVG viewbox string given floating point values for left, top, width and height """
        return " ".join(minimal_float_str(val) for val in [left, top, width, height])

    @staticmethod
    def transforms(string):
        """ Parse an SVG transform string and return a list of tuples of transforms. The tuples are of the form (trasform_type, args), both are strings, the args string is not parsed further and is provided as-is"""
        matches = re.findall(
            r"(translate|rotate|scale|matrix|skew(?:x|y))\(([^)]+)\)", string, flags=re.IGNORECASE)
        return [(transform, args) for transform, args in matches]

    @staticmethod
    def num_args_for_path_command(command):
        """ Given a command letter from an SVG path, rerturn a list of integers representing the argument pattern of the command.
        Each integer in the list specifies the number of arguments to seperate with commas, each group of comma seperated arguments is seperated with whitespace.

        e.g. the h command needs one argument and so num_args_for_path_command("h") == [1]
        That means this is valid: "h 1"
        something like the c command is more complicated. num_args_for_path_command("c") == [2,2,2]
        That means this is valid: "c 1,2 3,4 5,6" (three groups of 2)  """
        try:
            return {
                "m": [2],
                "l": [2],
                "h": [1],
                "v": [1],
                "c": [2, 2, 2],
                "s": [2, 2],
                "q": [2, 2],
                "t": [2],
                "a": [7],
                "z": [0]
            }[command.lower()]
        except KeyError:
            # It's not really a keyerror, it's a value error
            raise ValueError

    @staticmethod
    def path_parts(string):
        """ Given an SVG path string (the 'd' attribute of a <path> tag) return a list of parts of a path.
        Each part is a tuple (command, args) where command is a single character string representing the command and args is a list of strings """
        TRANS_MOVETO = {ord("M"):"L", ord("m"):"l"}
        output = []
        commands = "MmLlHhVvCcSsQqTtAaZz"
        remaining = string.strip()
        remaining = ''.join(
            [char if char != ',' else ' ' for char in remaining])
        cur_command = None
        num_args = None
        this_args = []
        while remaining:
            first = remaining[0]
            if first in commands:
                if this_args != []:
                    # Started new command before previous one complete
                    raise ValueError("Invalid SVG path command sequence")
                cur_command = first
                num_args = SVGUtils.num_args_for_path_command(cur_command)
                if num_args == [0]:
                    output.append((cur_command, []))
                remaining = remaining[1:].strip()
                continue
            m = re.match("^([-+]?\d+(?:\.\d)?\d*).*", remaining)
            if not m:
                raise ValueError("Invald SVG path command sequence")
            arg = m.groups()[0]
            this_args.append(arg)
            remaining = remaining[len(arg):].strip()
            if len(this_args) == sum(num_args):
                output.append((cur_command, this_args))
                this_args = []
                # If we get here and the current command is moveto
                # then we implicitly start a lineto command
                cur_command = cur_command.translate(TRANS_MOVETO)
        return output

    def path_string(parts):
        """ Take a list in the format output by path_parts() and turn it into an SVG path string (the 'd' attribute of a <path> tag """
        output = []
        for command, args in parts:
            argnums = SVGUtils.num_args_for_path_command(command)
            assert len(args) == sum(argnums)
            output.append(command)
            arglist = []
            for num in argnums:
                this_args, args = args[0:num], args[num:]
                if this_args:
                    arglist.append(' '.join(this_args))
            if arglist:
                output.append(", ".join(arglist))
        return ' '.join(output)

    def path_end_point(parts):
        """ Find the end point of an SVG path string (the 'd' attribute of a <path> tag) returns a tuple of two floats (x, y) """
        pos = 0, 0
        for command, args in parts:
            if command in ['M', 'L', 'T']:
                pos = float(args[0]), float(args[1])
            if command in ['m', 'l', 't']:
                pos = pos[0] + float(args[0]), pos[1] + float(args[1])
            if command == 'H':
                pos = float(args[0]), pos[1]
            if command == 'h':
                pos = pos[0] + float(args[0]), pos[1]
            if command == 'V':
                pos = pos[0], float(args[0])
            if command == 'v':
                pos = pos[0], pos[1] + float(args[0])
            if command == 'C':
                pos = float(args[4]), float(args[5])
            if command == 'c':
                pos = pos[0] + float(args[4]), pos[1] + float(args[5])
            if command in ['S', 'Q']:
                pos = float(args[2]), float(args[3])
            if command in ['s', 'q']:
                pos = pos[0] + float(args[2]), pos[1] + float(args[3])
            if command == 'A':
                pos = float(args[5]), float(args[6])
            if command == 'a':
                pos = pos[0] + float(args[5]), pos[1] + float(args[6])
        return pos

    def path_to_point(parts, point):
        """
        Take a list of path parts (in the same format as output by path_parts()) and produce a new path with the same types of segments where all points are collapsed into the point specified in point (a tuple of two floats (x, y))
         """
        newpath = []
        point = str(point[0]), str(point[1])
        for command, args in parts:
            if command in ['M', 'L', 'T']:
                newpath.append((command, list(point)))
            if command in ['m', 'l', 't']:
                newpath.append((command, ['0', '0']))
            if command == 'H':
                newpath.append((command, point[0]))
            if command == 'V':
                newpath.append((command, point[1]))
            if command in ['h', 'v']:
                newpath.append((command, ['0']))
            if command == 'C':
                newpath.append(
                    (command, list(point) + list(point) + list(point)))
            if command == 'c':
                newpath.append((command, ['0', '0', '0', '0', '0', '0']))
            if command in ['S', 'Q']:
                newpath.append((command, list(point) + list(point)))
            if command in ['s', 'q']:
                newpath.append((command, ['0', '0', '0', '0',]))
            if command == 'A':
                newpath.append((command, args[0:4+1] + list(point)))
            if command == 'a':
                newpath.append((command, args[0:4+1] + ['0', '0']))
        return newpath

    def match_paths(l1, l2):
        o1, o2 = [], [] # Outputs
        i1, i2 = 0, 0 # Current index
        si1, si2 = 0, 0 # For checking we advanced

        def add_paths(o, num, io):
            """ Add `num` path parts to the path `o` starting at index `io`, returning the new index """
            for i in range(num):
                o.append(io)
                io += 1
            return io

        def add_gaps(o, num):
            """ add `num` gaps to the path `o` """
            o.extend([-1] * num)

        try:
            while True:
                si1, si2 = i1, i2
                if l1[i1] == l2[i2]:
                    # Both same, add this path to both
                    i1 = add_paths(o1, 1, i1)
                    i2 = add_paths(o2, 1, i2)
                else:
                    # Different, get remaining path slice
                    r1 = l1[i1:]
                    r2 = l2[i2:]
                    if l1[i1] not in r2:
                        # If this isn't in the other one, just add to path now
                        i1 = add_paths(o1, 1, i1)
                        add_gaps(o2, 1)
                    elif l2[i2] not in r1:
                        # Same as above
                        i2 = add_paths(o2, 1, i2)
                        add_gaps(o1, 1)
                    else:
                        # Otherwise, pick the shortest distance to the next matching path part
                        d1 = l2[i2:].index(l1[i1])
                        d2 = l1[i1:].index(l2[i2])
                        if d1 < d2:
                            add_gaps(o1, 1)
                            i2 = add_paths(o2, 1, i2)
                        else:
                            add_gaps(o2, 1)
                            i1 = add_paths(o1, 1, i1)
                assert (i1 != si1) or (i2 != si2)
        except IndexError:
            # Hit end of one of the strings, stop
            pass
        # Keep adding until each one is done (one of these loops won't do anything)
        while i1 < len(l1):
            i1 = add_paths(o1, 1, i1)
            add_gaps(o2, 1)
        while i2 < len(l2):
            i2 = add_paths(o2, 1, i2)
            add_gaps(o1, 1)
        assert len(o1) == len(o2)
        return o1, o2

    def _indicies_to_path(indicies, path, fallback_indicies, fallback_path):
        output = []
        for index, fallback_index in zip(indicies, fallback_indicies):
            if index >= 0:
                part = path[index]
                output.append(part)
            else:
                assert fallback_index >= 0
                cur_end = SVGUtils.path_end_point(output)
                otherpath = fallback_path[fallback_index]
                output.extend(SVGUtils.path_to_point([otherpath], cur_end))
        return output

    def tweenable_paths(path1, path2):
        p1sequence = list(command for command, _ in path1)
        p2sequence = list(command for command, _ in path2)
        p1indicies, p2indicies = SVGUtils.match_paths(p1sequence, p2sequence)
        p1out = SVGUtils._indicies_to_path(p1indicies, path1, p2indicies, path2)
        p2out = SVGUtils._indicies_to_path(p2indicies, path2, p1indicies, path1)
        return p1out, p2out
