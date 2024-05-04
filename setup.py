import os
import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# get __version__ from _version.py
ver_file = os.path.join('mlforge', '_version.py')
with open(ver_file) as f:
    exec(f.read())

setuptools.setup(
    name="mlforge",
    version=__version__,
    author="J. Renero",
    author_email="jesus.renero@gmail.com",
    description="A package to design and run sequential ML pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renero/mlforge",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "mlforge"},
    # packages=setuptools.find_packages(where="mlforge"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6"
)

EXTRAS_REQUIRE = {
    'tests': [
        'pytest',
        'pytest-cov'],
    'docs': [
        'sphinx',
        'sphinx-gallery',
        'sphinx_rtd_theme',
        'numpydoc',
        'matplotlib'
    ]
}
