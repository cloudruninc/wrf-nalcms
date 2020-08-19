import argparse
import xarray as xr


def cli():

    parser = argparse.ArgumentParser(description='replace_netcdf_field - replaces one field in a target NetCDF file given a source file')
    parser.add_argument('field', type=str, help='Field to replace')
    parser.add_argument('source_file', type=str, help='Source file that provides the field')
    parser.add_argument('target_file', type=str, help='Target file in which to replace the field')
    args = parser.parse_args()

    source = xr.open_dataset(args.source_file)
    target = xr.open_dataset(args.target_file)

    target[args.field][:] = source[args.field][:]
    target.to_netcdf(args.target_file + '_new')
