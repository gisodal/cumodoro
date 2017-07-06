from setuptools import setup, find_packages

setup(
    name='cumodoro',
    version="0.1.0",
    description='Terminal interface to pomodoro timer.',
    keywords='Pomodoro ncurses terminal',
    license='MIT',
    url='https://github.com/gisodal/cumodoro',
    packages=find_packages(),
    scripts = ['bin/cumodoro'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities'
    ]
    )
