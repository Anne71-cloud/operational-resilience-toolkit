from setuptools import setup, find_packages

setup(
    name="operational-resilience-toolkit",
    version="1.0.0",
    description="A Python framework for operational resilience management in financial institutions",
    author="Saranne Ndamba",
    author_email="saranne.ndamba@outlook.com",
    url="https://github.com/anne71-cloud/operational-resilience-toolkit",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "networkx>=3.1",
        "pandas>=2.0",
        "matplotlib>=3.7",
        "plotly>=5.15",
        "streamlit>=1.28",
        "numpy>=1.24",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
)
