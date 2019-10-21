from setuptools import setup,find_packages

setup( name='Datpiff',
       version='1.0.1',
       decription='Datpiff Mixtape player',
       author='Cornelius Brooks',
       author_email='cbedroid1614@gmail.com',
       url='https://github.com/cbedroid/Datpiff',
       test_suite='tests.discover_suite',
       install_requires=open('requirements.txt').readline(),
       packages=find_packages(exclude=['test','tests.*']),
     )

