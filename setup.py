from setuptools import setup, find_packages

setup(
    name='ohada-financial-extractor',
    version='0.1.0',
    description='Extract and normalize financial data from OHADA-compliant Excel financial statements (DSF)',
    long_description=open('docs/README.md').read(),
    long_description_content_type='text/markdown',
    author='Leonel B. Kamguia Wabo; Ronald V. Ndayou',
    author_email='bomyr.kamguia@bkresearchandanalytics.com',
    url='https://github.com/bomyrk/ohada-financial-extractor',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        'openpyxl>=3.8.0',
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'xarray>=0.21.0',
    ],
    extras_require={
        'dev': ['pytest>=6.0', 'pytest-cov>=2.12.0'],
    },
    keywords=['OHADA', 'financial-extraction', 'accounting', 'Excel', 'data-extraction', 'financial statements'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)