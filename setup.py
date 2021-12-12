from setuptools import setup, find_packages

install_requires = [
    "adafruit-circuitpython-ads1x15",
    "attrs",
    "docker-compose",
    "fastapi",
    "psycopg2",
    "pytz",    
    "RPi.GPIO",
    "RPLCD",
    "smbus",
    "uvicorn",
]

setup(
    name="septic_monitor",
    version="0.1",
    packages=find_packages(),
    install_requires=install_requires,
)
