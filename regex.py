assert re_parse('') is None
assert re_parse('.') == 'dot'
assert re_parse('a') == 'a'
assert re_parse('ab') == ('cat', 'a', 'b')
assert re_parse('a|b') == ('split', 'a', 'b')
assert re_parse('a+') == ('repeat', 'a', 1, float('inf'))
assert re_parse('a{3,6}') == ('repeat', 'a', 3 ,6)
assert re_parse('a|bc') == ('split', 'a', ('cat', 'b', 'c'))

# a|b|c|.........
def parse_split(r, idx):
    idx, prev = parse_concat(r, idx)
    while idx < len(r):
        if r[idx] == ')':
            #return to the outer parse_node
            break
        assert r[idx] == '|', 'BUG'
        idx, node = parse_concat(r, idx + 1)
        prev = ('split', prev, node)
    return idx, prev

# abc......
def parse_concat(r, idx):
    prev = None
    while idx < len(r):
        if r[idx] in '|)':
            #return to the outer parse_split or parse_node
            break
        idx, node = parse_node(r, idx)
        if prev is None:
            prev = node
        else:
            prev = ('cat', prev, node)
    # when the prev is still None, it donetes the empty string
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
    elif ch in '*+{}':
        raise Exception('nothing to repeat')
    else:
        node = ch

    idx, node = parse_postfix(r, idx, node)
    return idx, node

# a*, a+, a{x}, a{x,}, a{x,y}
def parse_postfix(r, idx, node):
    