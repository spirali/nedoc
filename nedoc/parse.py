import ast
import asttokens
import logging


from .unit import Class, Function, Argument
from .utils import parse_cname


def construct_cname(node):
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        cname = construct_cname(node.value)
        return cname + (node.attr,)
    # TODO
    return ("XXX",)


def construct_unit_body(atok, node, unit):
    unit.docstring = ast.get_docstring(node)
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            unit.add_child(construct_function(atok, child))
        if isinstance(child, ast.ClassDef):
            unit.add_child(construct_class(atok, child))


def construct_function(atok, node):
    assert isinstance(node, ast.FunctionDef)
    if node.args.vararg:
        vararg = node.args.vararg.arg
    else:
        vararg = None
    if node.args.kwarg:
        kwarg = node.args.kwarg.arg
    else:
        kwarg = None
    args = [Argument(a.arg, None) for a in node.args.args]
    kwonlyargs = [Argument(a.arg, None) for a in node.args.kwonlyargs]
    for a, d in zip(reversed(args), reversed(node.args.defaults)):
        a.default = atok.get_text(d)
        if a.default == "(),":
            a.default = "()"
    for a, d in zip(reversed(kwonlyargs), reversed(node.args.kw_defaults)):
        a.default = atok.get_text(d)
        if a.default == "(),":
            a.default = "()"
    unit = Function(node.name, node.lineno, args, kwonlyargs, vararg, kwarg)
    unit.docstring = ast.get_docstring(node)

    for d in node.decorator_list:
        if isinstance(d, ast.Name) and d.id == "staticmethod":
            unit.static_method = True

        if isinstance(d, ast.Name) and d.id == "classmethod":
            unit.class_method = True

        text = atok.get_text(d)
        if "abstractmethod" in text:
            unit.abstract_method = True
        if text and text[0] == "@":
            text = text[1:]
        unit.decorators.append(text)
    return unit


def construct_class(atok, node):
    assert isinstance(node, ast.ClassDef)
    bases = [construct_cname(n) for n in node.bases]
    unit = Class(node.name, node.lineno, bases)
    construct_unit_body(atok, node, unit)
    for d in node.decorator_list:
        text = atok.get_text(d)
        if text and text[0] == "@":
            text = text[1:]
        unit.decorators.append(text)
    return unit


def extract_imports(node, module):
    imports = {}
    for n in node.body:
        if isinstance(n, ast.ImportFrom):
            if n.module is None:
                source_cname = ()
            else:
                source_cname = parse_cname(n.module)

            for name_node in n.names:
                if name_node.asname is None:
                    target_name = name_node.name
                else:
                    target_name = name_node.asname
                if n.level == 1:
                    if module.is_dir:
                        prefix = module.cname
                    else:
                        prefix = module.parent.cname

                elif n.level == 2:
                    if module.is_dir:
                        prefix = module.parent.cname
                    else:
                        prefix = module.parent.parent.cname
                else:
                    prefix = ()
                cname = prefix + source_cname + (name_node.name,)
                imports[target_name] = cname
    return imports


def construct_module(atok, node, module):
    #  DEBUG: print(ast.dump(node))
    extract_imports(node, module)
    module.imports = extract_imports(node, module)
    construct_unit_body(atok, node, module)
    return module


def parse_path(fullpath):
    try:
        with open(fullpath) as f:
            code = f.read()
        atok = asttokens.ASTTokens(code, parse=True)
        return atok, code
    except Exception as e:
        message = "Error occured in file '{}': Error: {}".format(fullpath, e)
        logging.error(message)
        raise Exception("Parsing failed: {}".format(message))
