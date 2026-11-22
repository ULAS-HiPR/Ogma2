"""Small KiCad S-expression reader/writer; quoted strings remain distinct."""
import json
import re

class Atom(str):
    pass

def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack, roots = [], []
    for token in tokens:
        if token == '(':
            value = []
            (stack[-1] if stack else roots).append(value)
            stack.append(value)
        elif token == ')':
            if not stack:
                raise ValueError('Unbalanced close parenthesis')
            stack.pop()
        else:
            if not stack:
                raise ValueError('Atom outside root')
            stack[-1].append(json.loads(token) if token.startswith('"') else Atom(token))
    if stack or len(roots) != 1:
        raise ValueError('Incomplete or multiple roots')
    return roots[0]

def emit(value, level=0):
    if isinstance(value, Atom):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if not isinstance(value, list):
        return str(value)
    if not any(isinstance(x, list) for x in value):
        return '(' + ' '.join(emit(x) for x in value) + ')'
    out = '('
    for i, child in enumerate(value):
        if isinstance(child, list):
            out += '\n' + '  ' * (level + 1) + emit(child, level + 1)
        else:
            out += (' ' if i else '') + emit(child)
    return out + ')'

def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]

def first(node, key, default=None):
    return next(iter(children(node, key)), default)

def walk(node, key):
    if not isinstance(node, list):
        return
    if node and node[0] == key:
        yield node
    for child in node:
        if isinstance(child, list):
            yield from walk(child, key)
