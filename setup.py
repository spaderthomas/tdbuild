# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdbuild']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.5,<0.5.0']

setup_kwargs = {
    'name': 'tdbuild',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'spaderthomas',
    'author_email': 'thomas.spader@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
