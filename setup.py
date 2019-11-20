from setuptools import setup, find_packages

with open('VERSION') as f:
    __version__ = f.read()

DEPENDENCIES = [
    # Packages in here should rarely be pinned. This is because these packages
    # (at the specified version) are required for project consuming this
    # library. By pinning to a specific version you are the number of projects
    # that can consume this or forcing them to upgrade/downgrade any
    # dependencies pinned here in their project.
    #
    # Generally packages listed here are pinned to a major version range.
    #
    # e.g.
    # Python FooBar package for foobaring
    # pyfoobar>=1.0, <2.0
    #
    # This will allow for any consuming projects to use this library as long
    # as they have a version of pyfoobar equal to or greater than 1.x and less
    # than 2.x installed.
]

setup(
    name='omnibot-receiver',
    version=__version__,
    description=(
        'Library for use by services that receive messages from omnibot.'
    ),
    url='https://www.github.com/lyft/python-omnibot-receiver',
    maintainer='Lyft',
    maintainer_email='rlane@lyft.com',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=DEPENDENCIES
)
