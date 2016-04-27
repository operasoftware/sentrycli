#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

from sentrycli import __version__


setup(name='sentrycli',
      version=__version__,
      description='CLI scripts to query and analyze data gathered by Sentry',
      author='Opera Wrocław Services',
      author_email='svc-code@opera.com',
      url='https://github.com/operasoftware/sentrycli/',
      license='MIT',
      keywords='sentry cli aggregation analysis events errors logging',
      download_url=('https://github.com/operasoftware/sentrycli/tarball/' +
                    __version__),
      packages=['sentrycli'],
      install_requires=['argh==0.26.1',
                        'cached-property==1.2.0',
                        'progressbar2==2.7.3',
                        'prettytable==0.7.2',
                        'requests==2.9.1',
                        'python-dateutil==2.5.0'],
      entry_points={'console_scripts': [
        'sentrycli = sentrycli.main:main']
      },
      zip_safe=False)
