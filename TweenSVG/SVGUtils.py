import re

class SVGUtils():

    @staticmethod
    def value_unit(string):
        m = re.match(r"([\d.]+)([^\d]*)", string)
        if not m:
            raise ValueError("invalid dimension value '%s'" % (string))
        g = m.groups()
        return float(g[0]), g[1]
    
    @staticmethod
    def to_unit_val(value, unit):
        return "%f%s"%(value, unit)
    
    @staticmethod
    def viewbox_vals(string):
        m = re.match(r"(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*) *[, ] *(\d+(?:\.\d)?\d*)", string)
        if not m:
            raise ValueError("invalid viewbox string")
        groups = m.groups()
        return tuple(float(groups[i]) for i in range(4))
    
    @staticmethod
    def to_viewbox_val(left, top, width, height):
        return "%f %f %f %f" % (left, top, width, height)
    
    @staticmethod
    def transforms(string):
        matches = re.findall(r"(translate|rotate|scale|matrix|skew(?:x|y))\(([^)]+)\)", string)
        return {transform: args for transform, args in matches}

    @staticmethod
    def num_args_for_path_command(command):
        return {
            "m": [2],
            "l": [2],
            "h": [1],
            "v": [1],
            "c": [2,2,2],
            "s": [2,2],
            "q": [2,2],
            "t": [2],
            "a": [7],
        }[command.lower()]

    @staticmethod
    def path_parts(string):
        """ Return a list of parts of a path """
        output = []
        commands = "MLlHhVvCcSsQqTtAaZz"
        remaining = string.strip()
        remaining = ''.join([char if char != ',' else ' ' for char in remaining])
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
        """ Find the end point of a path """
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
        print("Path: %r ends at %r" % (parts, pos))
        return pos

    def path_to_point(parts, point):
        newpath = []
        for command, args in parts:
            if command in ['M', 'L', 'T']:
                newpath.append((command, list(point)))
            if command in ['m', 'l', 't']:
                newpath.append((command, [0,0]))
            if command == 'H':
                newpath.append((command, point[0]))
            if command == 'V':
                newpath.append((command, point[1]))
            if command in ['h', 'v']:
                newpath.append((command, 0))
            if command == 'C':
                newpath.append((command, list(point) + list(point) + list(point)))
            if command == 'c':
                newpath.append((command, list(point) + list(point) + [args[4], args[5]]))
            if command in ['S', 'Q']:
                newpath.append((command, list(point) + list(point)))
            if command in ['s', 'q']:
                newpath.append((command, list(point) + [args[2], args[3]]))
            if command == 'A':
                newpath.append((command, args[0:4] + list(point)))
            if command == 'a':
                newpath.append((command, args[0:4] + [0,0]))
        return newpath

    def split_paths_for_tweening(path1, path2):
        """
            Take two lists of commands (from path_parts function)
            and make sure they are tweenable by splitting one of
            them if needed.
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
                p1_second = [('M', [str(endpos[0]), str(endpos[1])])]+path1[len(path2):]
                return [p1_first, p1_second], [path2], 0, 0
        else:
           if p2sequence.startswith(p1sequence):
                p2_first = path2[0:len(path1)]
                endpos = SVGUtils.path_end_point(p2_first)
                p2_second = [('M', [str(endpos[0]), str(endpos[1])])] + path2[len(path1):]
                return [path1], [p2_first, p2_second], 0, 0
        # TODO handle other cases
        raise
        return [path1], [path2], None, None

    def normalize_path_split_lists(paths1, paths2, p1id, p2id):
        if len(paths1) == len(paths2):
            return paths1, paths2

        diff = p1id-p2id
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
        paths1, paths2 = SVGUtils.normalize_path_split_lists(paths1, paths2, p1id, p2id)
        for i, path in enumerate(paths1):
            other = paths2[i]
            prev = paths1[i-1]
            if path is None:
                paths1[i] = SVGUtils.path_to_point(other, SVGUtils.path_end_point(prev))
        for i, path in enumerate(paths2):
            other = paths1[i]
            prev = paths2[i-1]
            if path is None:
                paths2[i] = SVGUtils.path_to_point(other, SVGUtils.path_end_point(prev))
        return paths1, paths2
