from setuptools import setup, find_packages

setup(
    name="rebel_rhythms",
    version="0.1.0",
    author="Yevhenii Nepsha",
    author_email="yevhenii.nepsha@gmail.com",
    description="A Python library for interacting with the Spotify API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yevhenii-nepsha/rebel-rhythms",
    packages=find_packages(),
    install_requires=[
        "requests==2.30.0",
        "pydantic==2.1.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
