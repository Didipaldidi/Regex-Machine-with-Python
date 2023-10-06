RE_REPEAT_LIMIT = 1000
# a|b|c...
def parse_split(r, idx):
    idx, prev = parse_concat(r, idx)
    while idx < len(r):
        if r[idx] == ')':
            # return to the outer parse_node
            break
        assert r[idx] == '|', 'BUG'
        idx, node = parse_concat(r, idx + 1)
        prev = ('split', prev, node)
    return idx, prev

# abc...
def parse_concat(r, idx):
    prev = None
    while idx < len(r):
        if r[idx] in '|)':
            # return to the outer parse_split or parse_node
            break
        idx, node = parse_node(r, idx)
        if prev is None:
            prev = node
        else:
            prev = ('cat', prev, node)
    # when the prev is still None, it denotes the empty string
    return idx, prev

# parse a single element
def parse_node(r, idx):
    ch = r[idx]
    idx += 1
    assert ch not in '|)'
    if ch == '(':
        idx, node = parse_split(r, idx)
        if idx < len(r) and r[idx] == ')':
            idx += 1
        else:
            raise Exception('unbalanced parenthesis')
    elif ch == '.':
        node = 'dot'
    elif ch in '*+{':
        raise Exception('nothing to repeat')
    else:
        node = ch

    idx, node = parse_postfix(r, idx, node)
    return idx, node

# a*, a+, a{x}, a{x,}, a{x,y}
def parse_postfix(r, idx, node):
    if idx == len(r) or r[idx] not in '*+{':
        return idx, node

    ch = r[idx]
    idx += 1
    if ch == '*':
        rmin, rmax = 0, float('inf')
    elif ch == '+':
        rmin, rmax = 1, float('inf')
    else:
        # the first number inside the {}
        idx, i = parse_int(r, idx)
        if i is None:
            raise Exception('expect int')
        rmin = rmax = i
        # the optional second number
        if idx < len(r) and r[idx] == ',':
            idx, j = parse_int(r, idx + 1)
            rmax = j if (j is not None) else float('inf')
        # close the brace
        if idx < len(r) and r[idx] == '}':
            idx += 1
        else:
            raise Exception('unbalanced brace')

    # sanity checks
    if rmax < rmin:
        raise Exception('min repeat greater than max repeat')
    if rmin > RE_REPEAT_LIMIT:
        raise Exception('the repetition number is too large')

    node = ('repeat', node, rmin, rmax)
    return idx, node

def parse_int(r, idx):
    save = idx
    while idx < len(r) and r[idx].isdigit():
        idx += 1
    return idx, int(r[save:idx]) if save != idx else None

def re_parse(r):
    idx, node = parse_split(r, 0)
    if idx != len(r):
        # parsing stopped at a bad ")"
        raise Exception('unexpected ")"')
    return node

# the backtracking method is pretty much a brute force method
# can also add some caching to elimate duplicate idx
def match_backtrack(node, text, idx):
    if node is None:
        yield idx #empty string
    elif node == "dont":
        if idx < len(text):
            yield idx + 1
    elif isinstance(node, str):
        assert len(node) == 1 # single char
        if idx < len(text) and text[idx] == node:
            yield idx + 1
    elif node[0] == "cat":
        # the 'yield from' is equivalent to:
        # for idx1 in match_backtrack_concat(node, text, idx):
        #   yield idx1
        yield from match_backtrack_concat(node, text, idx)
    elif node[0] == "split":
        yield from match_backtrack(node[1], text, idx)
        yield from match_backtrack(node[2], text, idx)
    elif node[0] == "repeat":
        yield from match_backtrack_repeat(node, text, idx)
    else:
        assert not 'reachable'

def match_backtrack_concat(node, text, idx):
    print()
def match_backtrack_repeat(node, text, idx):
    print()


assert re_parse('') is None
assert re_parse('.') == 'dot'
assert re_parse('a') == 'a'
assert re_parse('ab') == ('cat', 'a', 'b')
assert re_parse('a|b') == ('split', 'a', 'b')
assert re_parse('a+') == ('repeat', 'a', 1, float('inf'))
assert re_parse('a{3,6}') == ('repeat', 'a', 3, 6)
assert re_parse('a|bc') == ('split', 'a', ('cat', 'b', 'c'))
