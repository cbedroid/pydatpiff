from setuptools import setup,find_packages,Extension

with open('README.md',encoding='utf-8') as f:
    readme = f.read()

setup( name='Datpiff',
       version='0.1.4',
       description='Datpiff Mixtape player',
       url='https://github.com/cbedroid/Datpiff',
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
<<<<<<< HEAD
=======
                    'Operating System :: OS Independent',
                    'Topic :: Multimedia :: Sound/Audio :: Players',

>>>>>>> eca77c0... Refactor code, Change files name and method names in backup folder, Optimized speed of media.findSong function
                    ],
       zip_safe=False,
       packages=find_packages(exclude=['tests'])
     )

