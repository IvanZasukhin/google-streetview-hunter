from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="streetview-hunter",
    version="1.0.0",
    author="Ваше Имя",
    author_email="ваш.email@example.com",
    description="Автоматический сборщик панорам Google Street View",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ваш-username/google-streetview-hunter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Internet :: WWW/HTTP",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "streetview-hunter=streetview_hunter.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "streetview_hunter": ["configs/*.yaml"],
    },
)
