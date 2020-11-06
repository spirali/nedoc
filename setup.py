from setuptools import setup
import glob


with open('requirements.txt') as reqs:
    requirements = [line for line in reqs.read().split('\n') if line]

VERSION = None
with open("nedoc/version.py") as f:
    exec(f.read())
if VERSION is None:
    raise Exception("version.py executed but VERSION was not set")

long_desc = """
See https://github.com/spirali/nedoc for more details."""

assets = glob.glob("nedoc/templates/assets/**/*", recursive=True)

setup(name='nedoc',
      version=VERSION,
      description='Generator for API documentation',
      long_description=long_desc,
      url='https://github.com/spirali/nedoc',
      author='Stanislav Bohm',
      author_email='spirali@kreatrix.org',
      license='MIT',
      packages=["nedoc"],
      provides=["nedoc"],
      package_data={'nedoc': ["nedoc/templates/*"]},
      include_package_data=True,
      install_requires=requirements)
