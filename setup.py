from setuptools import setup, find_packages

setup(
    name="brain-in-jar",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "llama-cpp-python",
        "rich",
        "psutil",
    ],
    entry_points={
        'console_scripts': [
            'torture-cli=src.ui.torture_cli:main',
            'torture-gui=src.ui.torture_gui:main',
        ],
    },
) 