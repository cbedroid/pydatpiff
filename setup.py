from __init__ import __version__
from setuptools import setup,find_packages

with open('README.md',encoding='utf-8') as f:
    readme = f.read()

#package_dir={'datpiff':'pydatpiff'},
setup( name='pydatpiff',
       version=__version__,
       description='PyDatpiff Mixtape player',
       url='https://github.com/cbedroid/pydatpiff',
       long_description=readme,
       long_description_content_type='text/markdown',
       author='Cornelius Brooks',
       author_email='cbedroid1614@gmail.com',
       install_requires=open('requirements.txt').readline(),
       license='MIT',
       tests_require=['pytest==5.2.4'],
       classifiers=[
                    'License :: OSI Approved :: MIT License',
                    'Intended Audience :: Developers',
                    'Programming Language :: Python :: 3',
                    'Programming Language :: Python :: 3.3',
                    'Programming Language :: Python :: 3.4',
                    'Programming Language :: Python :: 3.6',
                    'Programming Language :: Python :: 3.7',
                    'Programming Language :: Python :: 3.8',
                    'Operating System :: OS Independent',
                    'Topic :: Multimedia :: Sound/Audio :: Players',

                    ],
       zip_safe=False,
       packages=find_packages(exclude=['tests'])
     )

