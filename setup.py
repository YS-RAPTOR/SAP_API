from setuptools import setup, find_namespace_packages

setup(
    name='SAP_API',
    version='1.0.0',
    description='API for the game Super Auto Pets',
    author='YS-RAPTOR',
    url='https://github.com/YS-RAPTOR/SAP_API',
    license='GPLv3',
    requires=['cv2', 'numpy', 'pytesseract', 'PIL', 'selenium'],
    package_dir={'': 'SAP_API'},
    packages=find_namespace_packages(exclude=['SAP_API.Assets.*']),
    package_data={'SAP_API.Assets': ['*.png', 'EmptySlots/*.png', 'NotAvailableSlots/*.png']}
)
