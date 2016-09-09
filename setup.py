import sys
from setuptools import setup
from setuptools.command.install import install

from trackmac.utils import generate_plist, create_dir
from trackmac.config import TRACK_SCRIPT, TRACK_DAEMON, VERSION


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        """
        should generate plist file first
        """
        create_dir()
        if sys.prefix.startswith('/System/Library/Frameworks/'):
            install_dir = self.install_scripts
        else:
            install_dir = self.install_base + '/bin'
        generate_plist(install_dir)
        install.run(self)


def parse_requirements(requirements, ignore=('setuptools',)):
    """Read dependencies from requirements file (with version numbers if any)
    Note: this implementation does not support requirements files with extra
    requirements
    """
    with open(requirements) as f:
        packages = set()
        for line in f:
            line = line.strip()
            if line.startswith(('#', '-r', '--')):
                continue
            if '#egg=' in line:
                line = line.split('#egg=')[1]
            pkg = line.strip()
            if pkg not in ignore:
                packages.add(pkg)
        return packages


setup(
    name='trackmac',
    version=VERSION,
    description="A command-line tool to track application usage for OS X",
    url='http://github.com/MacLeek/trackmac',
    author='MacLeek',
    author_email='inaoqi@gmail.com',
    packages=['trackmac'],
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    license='MIT',
    entry_points={
        'console_scripts': [
            '{} = trackmac.main:cli'.format(TRACK_SCRIPT),
            '{} = trackmac.app:main'.format(TRACK_DAEMON),
        ]
    },
    cmdclass={
        'install': PostInstallCommand,
    }
)
