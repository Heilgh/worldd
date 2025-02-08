from setuptools import setup, find_packages

setup(
    name="world-simulation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame==2.5.2",
        "numpy==1.24.3",
    ],
    entry_points={
        'console_scripts': [
            'world-simulation=src.main:main',
        ],
    },
    python_requires='>=3.8',
    author="Your Name",
    description="A world simulation game with intelligent entities",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 