from nedoc.core import Core
from nedoc.config import create_config_file, Config
from nedoc.utils import parse_cname
from nedoc.unit import Function

import os


def test_project1(project1):
    # output = project1.mkdir("target")
    # output = "/tmp/html"

    conf_path = str(project1.join("nedoc.conf"))
    create_config_file(conf_path, "Project1", "myproject")

    conf = Config(conf_path)

    core = Core(conf)
    assert set(core.scan_directories()) == set([
        "myproject/__init__.py",
        "myproject/mymodule1/myclass.py",
        "myproject/mymodule1/another.py",
        "myproject/mymodule1/functions.py"]
    )

    core.build()

    assert os.path.isfile(
        str(project1.join("html").join("assets").join("style.css")))

    modules = core.gctx.modules

    myproject = modules[("myproject",)]
    myproject_mymodule1 = modules[("myproject", "mymodule1")]
    myproject_mymodule1_f = modules[("myproject", "mymodule1", "functions")]
    myclass = modules[("myproject", "mymodule1", "myclass")]

    assert myproject.name == "myproject"
    assert myproject.parent is None
    assert myproject_mymodule1.name == "mymodule1"
    assert myproject_mymodule1.parent == myproject
    assert myproject_mymodule1_f.name == "functions"
    assert myproject_mymodule1_f.parent == myproject_mymodule1

    def find(m, cname):
        return m.find_by_cname(cname, core.gctx)

    MyClass = find(myclass, parse_cname("MyClass"))
    assert MyClass.name == "MyClass"
    m = myclass.module()
    assert find(m, MyClass.bases[0]).name == "BaseClass"
    assert find(m, MyClass.bases[1]).name == "AnotherClass"

    mt = MyClass.local_find("abs_method")
    assert isinstance(mt, Function)
    assert mt.is_method
    assert not mt.is_static()
    assert mt.abstract_method

    mt = MyClass.local_find("static_method")
    assert isinstance(mt, Function)
    assert mt.is_method and mt.static_method and not mt.class_method
    assert mt.is_static()
    assert not mt.abstract_method

    mt = MyClass.local_find("class_method")
    assert isinstance(mt, Function)
    assert mt.is_method and not mt.static_method and mt.class_method
    assert mt.is_static()
    assert not mt.abstract_method

    MyClass = find(myclass, parse_cname("MyClass2"))
    assert MyClass.name == "MyClass2"
    m = myclass.module()
    assert find(m, MyClass.bases[0]).name == "AnotherClass2"

    MyClass = find(myclass, parse_cname("MyClass3"))
    assert MyClass.name == "MyClass3"
    m = myclass.module()
    assert find(m, MyClass.bases[0]).name == "AnotherClass3"

    assert myproject.all_classes(core.gctx)[0].name == "MyClass"
