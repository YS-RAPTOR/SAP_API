from setuptools import setup, find_namespace_packages
from pathlib import Path

def get_install_requires() -> list[str]:
    requirementsFile = Path(__file__).parent / 'requirements.txt'
    requirements = []
    if requirementsFile.exists():
        with open(requirementsFile, 'r') as f:
            requirements = f.read().splitlines()
    return requirements

setup(
    name='SAP_API',
    version='1.0.0',
    description='API for the game Super Auto Pets',
    author='YS-RAPTOR',
    url='https://github.com/YS-RAPTOR/SAP_API',
    license='GPLv3',
    requires=get_install_requires(),
    packages=find_namespace_packages(exclude=['SAP_API.Assets.*']),
    package_data={'SAP_API.Assets': ['*.png', 'EmptySlots/*.png', 'NotAvailableSlots/*.png']}
)
