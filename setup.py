import os

from setuptools import setup
from setuptools.command.install import install

from app import db


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)

        # Initialize DB
        if not os.path.exists('site.db'):
            db.create_all()


setup(
    name='Negroamaro',
    version='0.1',
    cmdclass={
        'install': PostInstallCommand,
    },
)
