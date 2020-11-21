def parse_cname(name):
    return tuple(name.split("."))


def make_cname(name):
    return (name,)


def render_cname(cname):
    return ".".join(cname)
