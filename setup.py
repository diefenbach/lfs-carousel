import os

from setuptools import find_packages, setup

version = "2.0.0"

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md"), encoding="utf-8").read()

setup(
    name="lfs-carousel",
    version=version,
    description="An image carousel for the start page of an LFS shop, managed in the LFS management interface",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 5.2",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    keywords="django e-commerce online-shop",
    author="Maciej Wisniowski",
    maintainer="Kai Diefenbach",
    maintainer_email="kai.diefenbach@iqpp.de",
    url="https://github.com/diefenbach/lfs-carousel",
    license="BSD-3-Clause",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.12",
    install_requires=[
        "django-lfs>=1.0,<2",
    ],
)
