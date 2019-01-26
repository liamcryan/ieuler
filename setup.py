import os
from setuptools import setup, find_packages
from io import open

here = os.path.abspath(os.path.dirname(__file__))

install_requires = ['click', 'Pillow', 'requests-html']
tests_require = ['pytest', 'vcrpy']

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(name='ieuler',
      version='0.0.0',
      description='interact with project euler',
      long_description=readme,
      author='Liam Cryan',
      author_email='cryan.liam@gmail.com',
      packages=find_packages(),
      py_modules=['cli'],
      entry_points='''
            [console_scripts]
            ieuler=cli:cli
      ''',
      install_requires=install_requires,
      tests_require=tests_require,
      include_package_data=True,
      url='https://github.com/liamcryan/ieuler',
      classifiers=['Programming Language :: Python :: 3']
      )