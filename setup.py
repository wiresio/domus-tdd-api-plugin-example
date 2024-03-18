#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="TDD API plugin Example",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "tdd-api",
    ],
    extras_require={
        "dev": [
            "pytest",
            "mock",
        ]
    },
    entry_points={
        "tdd_api.plugins.blueprints": [
            "example=tdd_api_plugin_example:blueprint",
        ],
        "tdd_api.plugins.transformers": [
            "example=tdd_api_plugin_example.example:td_to_example",
        ],
    },
)
