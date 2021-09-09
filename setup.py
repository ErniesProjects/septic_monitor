from setuptools import setup, find_packages

install_requires = [
    "attrs",
    "docker-compose",
    "fastapi",
    "redistimeseries",
    "RPi.GPIO",
    "RPLCD",
]

setup(
    name="septic_monitor",
    version="0.1",
    packages=find_packages(),
    install_requires=install_requires,
)
