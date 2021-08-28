from setuptools import setup, find_packages

install_requires = [
    "RPi.GPIO",
]

setup(
    name="septic_monitor",
    version="0.1",
    packages=find_packages(),
    install_requires=install_requires,
)
