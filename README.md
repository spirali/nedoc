
# Nedoc (Non-Evaluating Documentation)

*Nedoc* is a generator of API documentation for Python 3 with the following features:

* Your code is not executed; Your program and its dependencies does not have to be installed.
* Nedoc tracks what methods was overridden and shows it in the documentation.
* Inheritance of docstrings for overridden methods is supported.
* Nedoc tracks what and where was reimported.
* Resulting documentation is a set of static HTML files.


## Examples

* Django documentation generated by Nedoc: https://spirali.github.io/nedoc-demo/django/django.html
* Dask/Distributed documentation generated by Nedoc: https://spirali.github.io/nedoc-demo/distributed/distributed.html

<img width="80%" src="docs/screenshot.png">

## Installation

```
$ pip3 install nedoc
```


## Getting started (short version)

```
python3 -m nedoc init MyProjectName /path/to/project
python3 -m nedoc build
```

## Getting starter (longer version)

First, we need to generate `nedoc.conf`; *PathToProject* should lead to toplevel
directory with Python source codes (i.e. directory containing toplevel
`__init__.py`).


```
python3 -m nedoc init <ProjectName> <PathToProject>
```

This command creates `nedoc.conf` in the current working directory. You can edit
it for more customized settings.

The documentation is built by the following command:

```
python3 -m nedoc build
```

By default, you can find the result in `html` directory.
