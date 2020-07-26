import argparse
import rasterio
from wrf_nalcms.demo import demo
import xarray


def cli():

    parser = argparse.ArgumentParser(description='nalcms - Process NALCMS land use data for ingestion into WRF')
    parser.add_argument('nalcms_path', type=str, help='Path to the NALCMS source TIFF file')
    parser.add_argument('geo_em_path', type=str, help='Path to the geo_em target NetCDF file')
    parser.add_argument('-d', '--demo', action='store_true', help='NALCMS sampling algorithm demo')
    args = parser.parse_args()

    nalcms = rasterio.open(args.nalcms_path)
    geo_em = xarray.open_dataset(args.geo_em_path)

    if args.demo:
        demo(nalcms, geo_em)
