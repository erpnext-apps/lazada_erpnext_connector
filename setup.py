# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in lazada_erpnext_connector/__init__.py
from lazada_erpnext_connector import __version__ as version

setup(
	name='lazada_erpnext_connector',
	version=version,
	description='Lazada Ecommerce Platform Integration witH E',
	author='Raaj Tailor',
	author_email='tailorraj111@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
