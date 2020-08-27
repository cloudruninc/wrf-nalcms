import argparse
import rasterio
from wrf_nalcms.demo import demo
from wrf_nalcms.nalcms import process_nalcms_to_geo_em_all, process_nalcms_to_geo_em_urban
import xarray


def cli():

    parser = argparse.ArgumentParser(description='nalcms - Process NALCMS land use data for ingestion into WRF')
    parser.add_argument('nalcms_path', type=str,
                        help='Path to the NALCMS source TIFF file')
    parser.add_argument('geo_em_path', type=str,
                        help='Path to the geo_em target NetCDF file')
    parser.add_argument('-d', '--demo', action='store_true',
                        help='NALCMS sampling algorithm demo')
    parser.add_argument('-c', '--classes', type=str, default='all',
                        choices=['all', 'urban'],
                        help='Which classes to process')
    parser.add_argument('-u', '--urban', type=str, default='multi',
                        choices=['single', 'multi'],
                        help='Whether to use single or multiple (3) urban classes (default single)')
    parser.add_argument('--low-density-residential', type=float, default=0.6,
                        help='Low density residential urban fraction threshold (default 0.6)')
    parser.add_argument('--high-density-residential', type=float, default=0.9,
                        help='High density residential urban fraction threshold (default 0.9)')
    parser.add_argument('--commercial-industrial', type=float, default=0.95,
                        help='Commercial/industrial urban fraction threshold (default 0.95)')
    args = parser.parse_args()

    nalcms = rasterio.open(args.nalcms_path)
    geo_em = xarray.open_dataset(args.geo_em_path)

    if args.demo:
        demo(nalcms, geo_em)
        return

    urban_multi = True if args.urban == 'multi' else False
    
    urban_fractions = [
        args.low_density_residential,
        args.high_density_residential,
        args.commercial_industrial
        ]

    if args.classes == 'all':
        process_nalcms_to_geo_em_all(nalcms, geo_em, urban_multi, urban_fractions)
    elif args.classes == 'urban':
        process_nalcms_to_geo_em_urban(nalcms, geo_em, urban_multi, urban_fractions)
