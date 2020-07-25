import argparse
import numpy as np
from pyproj import Proj
import rasterio
from wrf_nalcms.nalcms import get_nalcms_data_in_target_grid_cell
import xarray

import matplotlib.pyplot as plt

def cli():

    parser = argparse.ArgumentParser(description='nalcms - Process NALCMS land use data for ingestion into WRF')
    parser.add_argument('nalcms_path', type=str, help='Path to the NALCMS source TIFF file')
    parser.add_argument('geo_em_path', type=str, help='Path to the geo_em target NetCDF file')
    args = parser.parse_args()

    nalcms = rasterio.open(args.nalcms_path)
    geo_em = xarray.open_dataset(args.geo_em_path)

    # get the projection from the NALCMS dataset
    projection = Proj(nalcms.crs)

    jm, im = geo_em.XLONG_M[0,:,:].shape
    j0, i0 = jm // 2, im // 2

    latc = np.array(geo_em.XLAT_V[0,:,:])
    lonc = np.array(geo_em.XLONG_U[0,:,:])

    xx, yy, data, mask, xc, yc = get_nalcms_data_in_target_grid_cell(i0, j0, latc, lonc, \
                                                                     projection, nalcms, extent=10)

    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, aspect='equal')
    plt.plot(xc, yc, 'ro', mec='r', ms=12)
    plt.plot([xc[0], xc[1], xc[2], xc[3], xc[0]], \
             [yc[0], yc[1], yc[2], yc[3], yc[0]], 'r-')
    #plt.plot(xx, yy, 'k.')
    plt.scatter(xx[mask], yy[mask], c=data[mask], s=1)
    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.savefig('nalcms_to_geoem_demo.png')
    plt.close(fig)
