from setuptools import setup

setup(
    name='wrf-nalcms',
    version='0.1.0',
    description='Processing NALCMS land use for ingestion into WRF',
    author='Cloudrun Inc.',
    author_email='hello@cloudrun.co',
    url='https://github.com/cloudruninc/wrf-nalcms',
    packages=['wrf_nalcms'],
    install_requires=['matplotlib', 'netCDF4', 'pyproj', 'pytest', 'rasterio'],
    test_suite='wrf_nalcms.tests',
    entry_points={'console_scripts': ['nalcms = wrf_nalcms.cli:cli']},
    license='MIT'
)
