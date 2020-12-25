def is_public_name(name):
    return not name.startswith("_") or (name.startswith("__") and name.endswith("__"))


class UnitChild:
    def __init__(self, name, unit, imported):
        self.name = name
        self.unit = unit
        self.imported = imported


class Unit:
    def __init__(self, name, lineno):
        self.parent = None
        self.name = name
        self.lineno = lineno
        self._docstring = None
        self.childs = []
        self.aliases = []

    @property
    def has_own_docstring(self):
        return bool(self._docstring)

    @property
    def docstring(self):
        return self._docstring

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
        return [
            child
            for child in self.childs
            if (cls is None or isinstance(child, cls))
            and (public is None or public == is_public_name(child.name))
        ]

    def functions(self, public=None):
        return self.filter_childs(public, Function)

    def modules(self, public=None):
        return self.filter_childs(public, Module)

    def classes(self, public=None):
        return self.filter_childs(public, Class)

    def all_units(self, gctx, public=None, cls=None):
        return [UnitChild(c.name, c, False) for c in self.filter_childs(public, cls)]

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

    def local_find(self, name):
        for child in self.childs:
            if child.name == name:
                return child

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
    role = "module"

    def __init__(self, name, is_dir, source_filename):
        super().__init__(name, None)
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
                if (cls is None or isinstance(unit, cls)) and (
                    public is None or public == is_public_name(unit.name)
                ):
                    result.append(UnitChild(k, unit, True))
        result.sort(key=lambda c: (c.unit.sort_order, c.name))
        return result

    def all_classes(self, gctx, public=None):
        return self.all_units(gctx, public, Class)

    def all_functions(self, gctx, public=None):
        return self.all_units(gctx, public, Function)

    def imported_units(self, gctx, public=None, export=False, cls=None):
        result = []
        path = self.path
        names = set(unit.name for unit in self.childs)
        for k, v in self.imports.items():
            if k in names:
                continue
            if public is not None and public != is_public_name(k):
                continue
            unit = gctx.find_by_cname(v)
            if cls is not None and not isinstance(unit, cls):
                continue
            p = unit.path
            if export and p[: len(path)] != path:
                continue
            result.append((k, unit))
        return result

    def imported_classes(self, gctx, public=None, export=False):
        return self.imported_units(gctx, public=public, cls=Class, export=export)

    def imported_functions(self, gctx, public=None, export=False):
        return self.imported_units(gctx, public=public, cls=Function, export=export)

    def imported_modules(self, gctx, public=None, export=False):
        return self.imported_units(gctx, public=public, cls=Module, export=export)

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
                name, default_style[0], self.default, default_style[1]
            )


class Function(Unit):

    sort_order = 2
    keyword = "def"
    role = "function"

    def __init__(self, name, lineno, args, kwonlyargs, vararg, kwarg):
        super().__init__(name, lineno)
        self.args = args
        self.kwonlyargs = kwonlyargs
        self.vararg = vararg
        self.kwarg = kwarg
        self.overrides = None
        self.overriden_by = []
        self.decorators = []
        self.static_method = False
        self.class_method = False
        self.abstract_method = False

    @property
    def is_method(self):
        return isinstance(self.parent, Class)

    def render_args(self, **kw):
        args = [arg.render(**kw) for arg in self.args]
        if self.vararg:
            args.append("*" + self.vararg)
        elif self.kwonlyargs:
            args.append("*")
        if self.kwonlyargs:
            args += [arg.render(**kw) for arg in self.kwonlyargs]
        if self.kwarg:
            args.append("**" + self.kwarg)
        return ", ".join(args)

    @property
    def docstring(self):
        if self._docstring:
            return self._docstring
        if self.overrides:
            return self.overrides.docstring
        return None

    def finalize(self, gctx):
        super().finalize(gctx)
        if self.is_method:
            child = self.parent.find_method_in_super(gctx, self.name)
            if child is not None:
                assert child is not self
                self.overrides = child
                child.overriden_by.append(self)

    def is_static(self):
        return self.is_method and (self.class_method or self.static_method)


class Class(Unit):

    sort_order = 1
    keyword = "class"
    role = "class"

    def __init__(self, name, lineno, bases):
        super().__init__(name, lineno)
        self.name = name
        self.bases = bases
        self.subclasses = []
        self.decorators = []

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

    def finalize(self, gctx):
        super().finalize(gctx)
        self._add_subclasses(gctx)

        if gctx.config.copy_init_docstring:
            self._copy_init_docstring()

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

    def _add_subclasses(self, gctx):
        for base in self.bases:
            unit = self.module().find_by_cname(base, gctx)
            if isinstance(unit, Class):
                unit.subclasses.append(self)

    def _copy_init_docstring(self):
        if not self.docstring:
            fns = self.functions()
            init = [f for f in fns if f.name == "__init__"]
            if init and init[0].docstring:
                self.docstring = init[0].docstring
