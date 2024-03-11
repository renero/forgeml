import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mlforge",
    version="0.1.0-alpha",
    author="J. Renero",
    author_email="jesus.renero@gmail.com",
    description="A package to design and run sequential ML pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renero/forgeml",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6"
)
