from setuptools import setup, find_packages

with open('VERSION') as f:
    __version__ = f.read()

setup(
    name='omnibot-receiver',
    version=__version__,
    description=(
        'Library for use by services that receive messages from omnibot.'
    ),
    license="apache2",
    url='https://www.github.com/lyft/python-omnibot-receiver',
    maintainer='Lyft',
    maintainer_email='rlane@lyft.com',
    packages=find_packages(exclude=['tests*']),
)
