from setuptools import setup,find_packages
from vercontrol import getVersion

with open('README.md',encoding='utf-8') as f:
    readme = f.read()

#package_dir={'datpiff':'pydatpiff'},
setup( name='pydatpiff',
       version=getVersion(),
       description='Unofficial Datpiff Mixtape player - Download and play the newest Hip-Hop and RnB Songs.',
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
                    'Development Status :: 5 - Production/Stable',
                    'Intended Audience :: Developers',
                    'Intended Audience :: End Users/Desktop',
                    'Programming Language :: Python :: 3',
                    'Programming Language :: Python :: 3.1',
                    'Programming Language :: Python :: 3.2',
                    'Programming Language :: Python :: 3.3',
                    'Programming Language :: Python :: 3.4',
                    'Programming Language :: Python :: 3.5',
                    'Programming Language :: Python :: 3.6',
                    'Programming Language :: Python :: 3.7',
                    'Programming Language :: Python :: 3.8',
                    'Operating System :: OS Independent',
                    'Topic :: Internet :: WWW/HTTP',
                    'Topic :: Multimedia :: Sound/Audio :: Players',
                    'Topic :: Software Development :: Libraries :: Python Modules',

                    ],
       zip_safe=False,
       packages=find_packages(exclude=['tests'])
     )

