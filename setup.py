from setuptools import setup, find_packages

setup(
    name="pyline-core",
    version="2.2.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    author="Alp Sakaci",
    author_email="alp@alpsakaci.com",
    description="pyline core",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[],
    python_requires=">=3.10",
)
