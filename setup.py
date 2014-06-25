import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def main():
    # Check python version
    if sys.version_info < (3, 0, 0):
        sys.stderr.write('You need python 3.0 or later to run this script!' + os.linesep)
        exit(1)
    # Describe installer
    setup(
        name='pyspectator_tornado',
        version='1.0.2',
        author='Maxim Grischuk',
        author_email='uzumaxy@gmail.com',
        maintainer='Maxim Grischuk',
        maintainer_email='uzumaxy@gmail.com',
        packages=['pyspectator_tornado'],
        url='https://github.com/uzumaxy/pyspectator-tornado',
        download_url='https://github.com/uzumaxy/pyspectator-tornado/releases',
        bugtrack_url='https://github.com/uzumaxy/pyspectator-tornado/issues',
        license='BSD',
        description='''pyspectator_tornado is a web-monitoring tool ported on
                       Tornado with pyspectator as a main monitoring module.''',
        long_description=open('README.rst').read(),
        install_requires=['pyspectator >= 1.0.7', 'tornado >= 3.2.0'],
        keywords=[
            'example',
            'pyspectator', 'spectator', 'pyspectator_tornado',
            'monitoring', 'tool',
            'statistic', 'stats',
            'computer', 'pc', 'server',
            'mem', 'memory',
            'network', 'net', 'io',
            'processor', 'cpu',
            'hdd', 'hard', 'disk', 'drive',
            'web', 'tornado', 'www'
        ],
        platforms='Platform Independent',
        package_data={
            'pyspectator': ['LICENSE', 'README.rst']
        },
        scripts=['start.py'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows :: Windows 7',
            'Operating System :: Microsoft :: Windows :: Windows NT/2000',
            'Operating System :: Microsoft :: Windows :: Windows Server 2003',
            'Operating System :: Microsoft :: Windows :: Windows Server 2008',
            'Operating System :: Microsoft :: Windows :: Windows Vista',
            'Operating System :: Microsoft :: Windows :: Windows XP',
            'Operating System :: Microsoft',
            'Operating System :: OS Independent',
            'Operating System :: POSIX :: BSD :: FreeBSD',
            'Operating System :: POSIX :: Linux',
            'Operating System :: POSIX :: SunOS/Solaris',
            'Operating System :: POSIX',
            'Programming Language :: JavaScript',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python',
            'Topic :: Office/Business',
            'Topic :: System :: Benchmark',
            'Topic :: System :: Hardware',
            'Topic :: System :: Monitoring',
            'Topic :: System :: Networking :: Monitoring',
            'Topic :: System :: Networking',
            'Topic :: System :: Systems Administration'
        ],
    )


if __name__ == '__main__':
    main()