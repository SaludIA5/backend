from setuptools import find_packages, setup

setup(
    name="saluai5-ml",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "saluai5_ml": [
            "data/raw/*.xlsx",
            "data/raw/*.csv",
            "data/processed/*.csv",
            "models/*/*.pkl",
            "models/*/metrics/*.csv",
            "encoders/*.pkl",
        ]
    },
)
