from nedoc.unit import Function


def test_parse(module1):
    m = module1

    assert m.docstring == "Mod comment"
    assert len(m.childs) == 4
    assert len(list(m.functions())) == 2
    assert len(list(m.classes())) == 2
    f = m.childs[0]
    assert isinstance(f, Function)
    assert f.name == "my_fn"
    assert f.docline == "This is my fn"
    assert len(f.args) == 2
    assert f.args[0].name == "a"
    assert f.args[0].default is None
    assert f.args[1].name == "b"
    assert f.args[1].default == "5"
