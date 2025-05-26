from setuptools import setup, find_packages

setup(
    name="dagligdags",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.31',
        'pdfplumber>=0.10',
        'simple-term-menu>=1.4',
    ],
    entry_points={
        'console_scripts': [
            'dagligdags=main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
