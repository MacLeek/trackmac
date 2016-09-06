from setuptools import setup
from setuptools.command.install import install

from trackmac.utils import create_dir, create_database, symlink_and_load_plist


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
  install_requires=['Click', 'peewee'],
  license='MIT',
  entry_points={
      'console_scripts': [
          'tm = trackmac.main:cli',
          'trackmac_service = trackmac.app:main',
      ]
  },
  cmdclass={'install': PostInstallCommand},
)
