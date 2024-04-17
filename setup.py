from setuptools import setup, find_packages
import subprocess


def read_requirements():
    with open("requirements.txt", "r") as req:
        return req.read().splitlines()


setup(
    name="SC-Generator",
    version="0.1",
    packages=find_packages(),
    install_requires=read_requirements(),
)

# subprocess.run(["npm", "install", "-g", "solc"])
