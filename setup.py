from setuptools import setup, find_packages

setup(
    name='ohada-financial-extractor',
    version='0.1.0',
    description='Extract and normalize financial data from OHADA-compliant Excel financial statements (DSF)',
    long_description=open('docs/README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Kamguia Wabo, Leonel B. ; Ndayou, Ronald V. ',
    author_email='bomyr.kamguia@bkresearchandanalytics.com',
    url='https://github.com/bomyrk/ohada-financial-extractor',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.10',
    install_requires=[
        'openpyxl>=3.1.5',
        'numpy>=2.2.0',
        'pandas>=2.2.0',
        'xarray>=0.21.0',
        'pyqt5>=5.15.11',
        'matplotlib>=3.10.1',
        'plotly>=6.5.0',
        'streamlit>=1.56.0'
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
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)