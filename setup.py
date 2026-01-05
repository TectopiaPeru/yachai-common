"""
Setup configuration for yachai-common package.
Shared utilities for YACHAI projects.
"""
from setuptools import setup, find_packages

setup(
    name="yachai-common",
    version="1.0.0",
    description="Shared utilities for YACHAI projects (Salud-AI, Orbe-Service)",
    author="YACHAI Team",
    packages=find_packages(),
    install_requires=[
        "redis>=5.0.0",
        "cachetools>=5.3.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
