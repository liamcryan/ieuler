import os
from setuptools import setup
from io import open

here = os.path.abspath(os.path.dirname(__file__))

install_requires = [
    'click',
    'Pillow',
    'numpy',
    'requests-html',
    # 'rever'  # not on pypi
]

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(name='ieuler',
      version='0.0.0',
      description='interact with project euler',
      long_description=readme,
      author='Liam Cryan',
      author_email='cryan.liam@gmail.com',
      py_modules=['ieuler'],
      install_requires=install_requires,
      entry_points='''
            [console_scripts]
            ilr=ilr_cli:cli
      ''',
      include_package_data=True,
      url='https://github.com/liamcryan/ieuler',
      classifiers=['Programming Language :: Python :: 3.6']
      )
