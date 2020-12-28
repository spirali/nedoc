def parse_cname(name):
    return tuple(name.split("."))


def make_cname(name):
    return (name,)


def render_cname(cname):
    return ".".join(cname)


def join_upto_limit(args, delimiter, limit):
    result = delimiter.join(args)
    if len(result) <= limit:
        return False, result
    limit -= 4
    while args:
        args.pop()
        result = delimiter.join(args)
        if len(result) <= limit:
            return True, result + delimiter + "..."
    return True, "..."
