#!/usr/bin/env python

from distutils.core import setup

setup(name='TCC Utils',
      version='1.0',
      description='UDP Python Utilities',
      author='JCMBsoft',
      author_email='Geoffrey@jcmbsoft.com',
      url='https://jcmbsoft.com/',
      license="MIT For Trimble, GPL V3 for everyone else",
      py_modules=['TCC','TSD_Process'],
      scripts=[
        'UDP_Delay.py',
        'UDP_Count.py',
        'UDP_Sender.py',
        'UDP_Cat.py']
     )
