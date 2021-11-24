import setuptools
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="commercialscraperomartwo",
    version="0.0.1",
    author="Omar 4ldrich Tahmas",
    author_email="o.ismail@aol.co.uk",
    description="A dynamic and scalable data pipeline from Airbnbs commercial site to your local system / cloud storage.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlairMar/Airbnb-webscraping-project",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "Pipeline"},
    # packages=setuptools.find_packages(where="Pipeline"),
    packages = find_packages(),
    #install_requires= parse_requirements('requirements.txt', session='hack')

    python_requires=">=3.6",
)
