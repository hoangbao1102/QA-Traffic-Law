# setup.py
import setuptools
from setuptools import find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

vars2find = ["__author__", "__version__", "__url__"]
vars2readme = {}

with open("./nano_graphrag/__init__.py", "r", encoding="utf-8") as f:
    for line in f.readlines():
        for v in vars2find:
            if line.startswith(v):
                line = line.replace(" ", "").replace('"', "").replace("'", "").strip()
                vars2readme[v] = line.split("=")[1]

deps = []
# Se abre el archivo requirements.txt utilizando UTF-8
with open("./requirements.txt", "r", encoding="utf-8") as f:
    for line in f.readlines():
        if not line.strip():
            continue
        deps.append(line.strip())

setuptools.setup(
    name="nano-graphrag",
    url=vars2readme["__url__"],
    version=vars2readme["__version__"],
    author=vars2readme["__author__"],
    description="A simple, easy-to-hack GraphRAG implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=deps,
)
