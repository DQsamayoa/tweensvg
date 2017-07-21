"""
    Various SVG Parsing and transformation utilities
    These are generally for use within the Tweener module
    and so the API of this module will change if needed
    to satisfy Tweener.
"""
import re


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
        str_value = "%f" % (value)
        while str_value[-1] == '0' and str_value[-2] != '.':
            str_value = str_value[0:-1]
        if str_value[-2:] == '.0':
            str_value = str_value[0:-2]
        return "%s%s" % (str_value, unit)

    @staticmethod
    def viewbox_vals(string):
        """ Parse an SVG viewbox string and return a 4-tuple of (left, top, widht, height) floats """
        m = re.match(
            r"(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*)", string)
        if not m:
            raise ValueError("invalid viewbox string")
        groups = m.groups()
        return tuple(float(groups[i]) for i in range(4))

    @staticmethod
    def to_viewbox_val(left, top, width, height):
        """ Return an SVG viewbox string given floating point values for left, top, width and height """
        return "%f %f %f %f" % (left, top, width, height)

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
        }[command.lower()]

    @staticmethod
    def path_parts(string):
        """ Given an SVG path string (the 'd' attribute of a <path> tag) return a list of parts of a path.
        Each part is a tuple (command, args) where command is a single character string representing the command and args is a list of strings """
        output = []
        commands = "MLlHhVvCcSsQqTtAaZz"
        remaining = string.strip()
        remaining = ''.join(
            [char if char != ',' else ' ' for char in remaining])
        cur_command = None
        num_args = None
        this_args = []
        while remaining:
            first = remaining[0]
            if first in commands:
                cur_command = first
                num_args = SVGUtils.num_args_for_path_command(cur_command)
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
        return output

    def path_string(parts):
        """ Take a list in the format output by path_parts() and turn it into an SVG path string (the 'd' attribute of a <path> tag """
        output = []
        for command, args in parts:
            argnums = SVGUtils.num_args_for_path_command(command)
            assert len(args) == sum(argnums)
            output.append(command)
            for num in argnums:
                this_args, args = args[0:num], args[num:]
                output.append(','.join(this_args))
        return ' '.join(output)

    def path_end_point(parts):
        """ Find the end point of an SVG path string (the 'd' attribute of a <path> tag) returns a tuple of two floats (x, y) """
        pos = 0, 0
        for command, args in parts:
            if command in ['M', 'L', 'T']:
                pos = args[0], args[1]
            if command in ['m', 'l', 't']:
                pos = pos[0] + args[0], pos[1] + args[1]
            if command == 'H':
                pos = args[0], pos[1]
            if command == 'h':
                pos = pos[0] + args[0], pos[1]
            if command == 'V':
                pos = pos[0], args[0]
            if command == 'v':
                pos = pos[0], pos[1] + args[0]
            if command == 'C':
                pos = args[4], args[5]
            if command == 'c':
                pos = pos[0] + args[4], pos[1] + args[5]
            if command in ['S', 'Q']:
                pos = args[2], args[3]
            if command in ['s', 'q']:
                pos = pos[0] + args[2], pos[1] + args[3]
            if command == 'A':
                pos = args[5], args[6]
            if command == 'a':
                pos = pos[0] + args[5], pos[1] + args[6]
        return pos

    def path_to_point(parts, point):
        """
        Take a list of path parts (in the same format as output by path_parts()) and produce a new path with the same types of segments where all points are collapsed into the point specified in point (a tuple of two floats (x, y))
         """
        newpath = []
        for command, args in parts:
            if command in ['M', 'L', 'T']:
                newpath.append((command, list(point)))
            if command in ['m', 'l', 't']:
                newpath.append((command, [0, 0]))
            if command == 'H':
                newpath.append((command, point[0]))
            if command == 'V':
                newpath.append((command, point[1]))
            if command in ['h', 'v']:
                newpath.append((command, 0))
            if command == 'C':
                newpath.append(
                    (command, list(point) + list(point) + list(point)))
            if command == 'c':
                newpath.append(
                    (command, list(point) + list(point) + [args[4], args[5]]))
            if command in ['S', 'Q']:
                newpath.append((command, list(point) + list(point)))
            if command in ['s', 'q']:
                newpath.append((command, list(point) + [args[2], args[3]]))
            if command == 'A':
                newpath.append((command, args[0:4] + list(point)))
            if command == 'a':
                newpath.append((command, args[0:4] + [0, 0]))
        return newpath

    def split_paths_for_tweening(path1, path2):
        """
            Take two lists of commands (from path_parts() function)
            and make sure they are tweenable by splitting one of
            them if needed.
            Returns a 4-tuple (paths1, paths2, id1, id2) where paths1 and paths2 is a list of subpaths of path1 and path2 respectively and id1 and id2 are the indexes into each path which match each other exactly. Use "normalize_path_split_lists()" to create tweenable paths from these lists and indexes.
        """
        p1sequence = ''.join(command for command, _ in path1)
        p2sequence = ''.join(command for command, _ in path2)
        if p1sequence == p2sequence:
            # Yay! No work to do, sequences already match
            return [path1], [path2], 0, 0
        if len(p2sequence) < len(p1sequence):
            if p1sequence.startswith(p2sequence):
                p1_first = path1[0:len(path2)]
                endpos = SVGUtils.path_end_point(p1_first)
                p1_second = [('M', [str(endpos[0]), str(endpos[1])])
                             ] + path1[len(path2):]
                return [p1_first, p1_second], [path2], 0, 0
        else:
            if p2sequence.startswith(p1sequence):
                p2_first = path2[0:len(path1)]
                endpos = SVGUtils.path_end_point(p2_first)
                p2_second = [('M', [str(endpos[0]), str(endpos[1])])
                             ] + path2[len(path1):]
                return [path1], [p2_first, p2_second], 0, 0
        # TODO handle other cases
        raise
        return [path1], [path2], None, None

    def normalize_path_split_lists(paths1, paths2, p1id, p2id):
        """ Take path lists and IDs such as those output by the split_paths_for_tweening() function and 'normalize' them by padding the lists with Nones so that the specified indexes line up and the path lists are of equal length. For example normalize_path_split_lists([A, B, C], [D], 1, 0) == ([A, B, C], [None, D, None])"""
        if len(paths1) == len(paths2):
            return paths1, paths2

        diff = p1id - p2id
        if diff < 0:
            paths1 = ([None] * -diff) + paths1
        else:
            paths2 = ([None] * diff) + paths2

        diff2 = len(paths1) - len(paths2)
        if diff2 == 0:
            return paths1, paths2

        if diff2 < 0:
            paths1 += [None] * -diff2
        else:
            paths2 += [None] * diff2

        return paths1, paths2

    def normalize_path_splits(paths1, paths2, p1id, p2id):
        """ Take path lists and IDs such as those output by the split_paths_for_tweening() function and turn them into lists of tweenable paths. This will fill in any None paths with paths that have been squashed to a single point. """
        paths1, paths2 = SVGUtils.normalize_path_split_lists(
            paths1, paths2, p1id, p2id)
        for i, path in enumerate(paths1):
            other = paths2[i]
            prev = paths1[i - 1]
            if path is None:
                paths1[i] = SVGUtils.path_to_point(
                    other, SVGUtils.path_end_point(prev))
        for i, path in enumerate(paths2):
            other = paths1[i]
            prev = paths2[i - 1]
            if path is None:
                paths2[i] = SVGUtils.path_to_point(
                    other, SVGUtils.path_end_point(prev))
        return paths1, paths2
