from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="pyline-core",
    version="0.1",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    author="Alp Sakaci",
    author_email="alp@alpsakaci.com",
    description="pyline core",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[],
    python_requires=">=3.10",
)
