

def is_public_name(name):
    return not name.startswith("_") or (
        name.startswith("__") and name.endswith("__"))


class UnitChild:

    def __init__(self, name, unit, imported):
        self.name = name
        self.unit = unit
        self.imported = imported


class Unit:

    def __init__(self, name):
        self.parent = None
        self.name = name
        self.docstring = None
        self.childs = []
        self.aliases = []

    @property
    def docline(self):
        if not self.docstring:
            return ""
        lines = self.docstring.split("\n")
        for line in lines:
            if line:
                return line
        return ""

    @property
    def path(self):
        if self.parent is None:
            return (self,)
        else:
            return self.parent.path + (self,)

    @property
    def fullname(self):
        return ".".join(self.cname)

    @property
    def cname(self):
        return tuple([p.name for p in self.path])

    def filter_childs(self, public=None, cls=None):
        return [child for child in self.childs
                if (cls is None or isinstance(child, cls)) and
                (public is None or public == is_public_name(child.name))]

    def functions(self, public=None):
        return self.filter_childs(public, Function)

    def modules(self, public=None):
        return self.filter_childs(public, Module)

    def classes(self, public=None):
        return self.filter_childs(public, Class)

    def all_units(self, gctx, public=None, cls=None):
        return [UnitChild(c.name, c, False)
                for c in self.filter_childs(public, cls)]

    def add_child(self, child):
        assert child.parent is None
        assert child not in self.childs
        child.parent = self
        self.childs.append(child)

    def module(self):
        if isinstance(self, Module):
            return self
        return self.parent.module()

    def find_by_cname(self, cname, gctx):
        #  print(">>> FIND_BY_NAME", repr(cname), " IN ", self)
        assert isinstance(cname, tuple)
        if not cname:
            return self
        name = cname[0]
        for child in self.childs:
            if child.name == name:
                return child.find_by_cname(cname[1:], gctx)
        target = self.imports.get(name)
        if target is not None:
            module = gctx.get_module((target[0],))
            if module:
                child = module.find_by_cname(target[1:], gctx)
                if child:
                    return child.find_by_cname(cname[1:], gctx)
        return None

    def traverse(self):
        for child in self.childs:
            yield from child.traverse()
        yield self

    def finalize(self, gctx):
        self.childs.sort(key=lambda unit: (unit.sort_order, unit.name))

    def add_alias(self, name):
        self.aliases.append(name)

    def __repr__(self):
        return "<{} name={}>".format(self.__class__.__name__, self.fullname)


class Module(Unit):

    sort_order = 0
    keyword = ""

    def __init__(self, name, is_dir, source_filename):
        super().__init__(name)
        self.imports = {}
        self.is_dir = is_dir
        self.source_filename = source_filename
        self.source_code = None

    def all_units(self, gctx, public=None, cls=None):
        result = super().all_units(gctx, public, cls)
        names = set(uc.name for uc in result)
        for k, v in self.imports.items():
            if k in names:
                continue
            unit = gctx.find_by_cname(v)
            if unit is not None:
                if ((cls is None or isinstance(unit, cls)) and
                        (public is None or
                         public == is_public_name(unit.name))):
                    result.append(UnitChild(k, unit, True))
        result.sort(key=lambda c: (c.unit.sort_order, c.name))
        return result

    def all_classes(self, gctx, public=None):
        return self.all_units(gctx, public, Class)

    def all_functions(self, gctx, public=None):
        return self.all_units(gctx, public, Function)

    def finalize(self, gctx):
        super().finalize(gctx)
        for name, target in self.imports.items():
            unit = gctx.find_by_cname(target)
            if unit:
                unit.add_alias(self.cname + (name,))


class Argument:

    def __init__(self, name, default):
        self.name = name
        self.default = default

    def __repr__(self):
        return "<Arg name={}>".format(self.name)

    def render(self, self_style=("", ""), default_style=("", "")):
        if self.name == "self":
            name = "{}self{}".format(*self_style)
        else:
            name = self.name
        if self.default is None:
            return name
        else:
            return "{}={}{}{}".format(
                name, default_style[0], self.default, default_style[1])


class Function(Unit):

    sort_order = 2
    keyword = "def"

    def __init__(self, name, args):
        super().__init__(name)
        self.args = args
        self.overrides = None
        self.overriden_by = []

    @property
    def is_method(self):
        return isinstance(self.parent, Class)

    def render_args(self, **kw):
        return ", ".join(arg.render(**kw) for arg in self.args)

    def finalize(self, gctx):
        super().finalize(gctx)
        if self.is_method:
            child = self.parent.find_method_in_super(gctx, self.name)
            if child is not None:
                assert child is not self
                self.overrides = child
                child.overriden_by.append(self)


class Class(Unit):

    sort_order = 1
    keyword = "class"

    def __init__(self, name, bases):
        super().__init__(name)
        self.name = name
        self.bases = bases

    def traverse_super(self, gctx):
        for base in self.bases:
            unit = self.module().find_by_cname(base, gctx)
            if isinstance(unit, Class):
                yield unit
                yield from unit.traverse_super(gctx)

    def find_method_in_super(self, gctx, name):
        for unit in self.traverse_super(gctx):
            for child in unit.functions():
                if child.name == name:
                    return child

    def inherited_methods(self, gctx, public):
        results = []
        names = set(unit.name for unit in self.functions())
        for unit in self.traverse_super(gctx):
            lst = []
            for f in unit.functions(public):
                if f.name not in names:
                    lst.append(f)
                    names.add(f.name)
            if lst:
                lst.sort(key=lambda u: u.name)
                results.append((unit, lst))
        return results
