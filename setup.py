import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="money",
    version="0.2.0",
    author="Mirko Dziadzka",
    author_email="mirko.dziadzka@gmail.com",
    description="Interface to MoneyMoney",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MirkoDziadzka/py-money",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.9",
)
