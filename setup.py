import os
from setuptools import setup
from io import open

here = os.path.abspath(os.path.dirname(__file__))

install_requires = [
    'click',
    'Pillow',
    'numpy',
    'requests-html',
    'rever'
]

about = {}
with open(os.path.join(here, 'ieuler', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(name='ieuler',
      version=about['__version__'],
      description='interact with project euler',
      long_description=readme,
      author='Liam Cryan',
      author_email='cryan.liam@gmail.com',
      packages=['ieuler'],
      install_requires=install_requires,
      entry_points='''
            [console_scripts]
            ilr=ieuler.cli:ilr
      ''',
      include_package_data=True,
      url='https://github.com/liamcryan/ieuler',
      classifiers=['Programming Language :: Python :: 3.6']
      )
