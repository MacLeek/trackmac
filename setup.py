from setuptools import setup

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
    version='0.0.1',
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
            'tm = trackmac.main:cli',
            'trackmac_service = trackmac.app:main',
        ]
    },
)
