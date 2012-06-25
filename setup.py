from setuptools import setup
import os

version = '0.0'

setup(name='transaction_filesytem',
      version=version,
      description="File manipulation within transaction management",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("CHANGES.txt")).read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='',
      license='GPL',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'transaction'
      ])
