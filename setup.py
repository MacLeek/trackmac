from setuptools import setup
from setuptools.command.install import install

from trackmac.utils import create_dir, create_database, symlink_and_load_plist


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


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        create_dir()
        create_database()
        symlink_and_load_plist()


setup(
    name='trackmac',
    version='0.0.1',
    description="A command-line tool to track application usage for OS X",
    url='http://happylyang.com',
    author='MacLeek',
    author_email='inaoqi@gmail.com',
    packages=['trackmac'],
    install_requires=parse_requirements('requirements.txt'),
    license='MIT',
    entry_points={
        'console_scripts': [
            'tm = trackmac.main:cli',
            'trackmac_service = trackmac.app:main',
        ]
    },
    # cmdclass={'install': PostInstallCommand},
)
