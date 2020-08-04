import argparse
import rasterio
from wrf_nalcms.demo import demo
from wrf_nalcms.nalcms import process_nalcms_to_geo_em
import xarray


def cli():

    parser = argparse.ArgumentParser(description='nalcms - Process NALCMS land use data for ingestion into WRF')
    parser.add_argument('nalcms_path', type=str, \
                        help='Path to the NALCMS source TIFF file')
    parser.add_argument('geo_em_path', type=str, \
                        help='Path to the geo_em target NetCDF file')
    parser.add_argument('-d', '--demo', action='store_true', \
                        help='NALCMS sampling algorithm demo')
    parser.add_argument('-c', '--classes', type=str, default='all', \
                        help='Which classes to process (all, urban-single, urban-multi)')
    args = parser.parse_args()

    if args.classes not in ['all', 'urban-single', 'urban-multi']:
        raise ValueError('value of --classes must be "all", "urban-single", or "urban-multi"')

    nalcms = rasterio.open(args.nalcms_path)
    geo_em = xarray.open_dataset(args.geo_em_path)

    if args.demo:
        demo(nalcms, geo_em)
        quit()

    process_nalcms_to_geo_em(nalcms, geo_em)
