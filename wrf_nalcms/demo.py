import numpy as np
from pyproj import Proj
import rasterio
from wrf_nalcms.nalcms import CLASSES, get_nalcms_data_in_target_grid_cell
import xarray
import matplotlib.pyplot as plt


def demo(nalcms, geo_em):

    extent = 1

    ottawa_lat, ottawa_lon = 45.421, -75.704

    lon = np.array(geo_em.XLONG_M[0,:,:])
    lat = np.array(geo_em.XLAT_M[0,:,:])
    latc = np.array(geo_em.XLAT_V[0,:,:])
    lonc = np.array(geo_em.XLONG_U[0,:,:])

    j0, i0 = np.unravel_index(np.argmin((ottawa_lon-lon)**2 + (ottawa_lat - lat)**2), lon.shape)

    # get the projection from the NALCMS dataset
    projection = Proj(nalcms.crs)

    xx, yy, data, mask, xc, yc = get_nalcms_data_in_target_grid_cell(i0, j0, latc, lonc, \
                                                                     projection, nalcms, extent=extent)

    # Step 1: Target grid cell in Cartesian space
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal')
    plt.plot([xc[0], xc[1], xc[2], xc[3], xc[0]], \
             [yc[0], yc[1], yc[2], yc[3], yc[0]], \
             'k-', marker='o', mec='k', ms=12)
    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('Step 1: Target grid cell in Cartesian space')
    fig.subplots_adjust(left=0.0, top=0.95)
    plt.savefig('nalcms_demo_step1.png')
    plt.close(fig)
    
    xcc = [np.min(xc), np.max(xc), np.max(xc), np.min(xc), np.min(xc)]
    ycc = [np.min(yc), np.min(yc), np.max(yc), np.max(yc), np.min(yc)]
    
    # Step 2: Set bounds of target grid cell extent
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal')
    plt.plot([xc[0], xc[1], xc[2], xc[3], xc[0]], \
             [yc[0], yc[1], yc[2], yc[3], yc[0]], \
             'k-', marker='o', mec='k', ms=12)
    plt.plot(xcc, ycc, 'k-', alpha=0.5)
    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('Step 2: Find bounds of target grid cell')
    fig.subplots_adjust(left=0.0, top=0.95)
    plt.savefig('nalcms_demo_step2.png')
    plt.close(fig)
   
    # Step 3: Overlay source grid points
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal')
    plt.plot([xc[0], xc[1], xc[2], xc[3], xc[0]], \
             [yc[0], yc[1], yc[2], yc[3], yc[0]], \
             'k-', marker='o', mec='k', ms=12)
    plt.plot(xx[::10,::10], yy[::10,::10], 'k.', ms=1)
    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('Step 3: Overlay source grid points')
    fig.subplots_adjust(left=0.0, top=0.95)
    plt.savefig('nalcms_demo_step3.png')
    plt.close(fig)
    
    # Step 4: Identify points inside target grid cell
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal')
    plt.plot([xc[0], xc[1], xc[2], xc[3], xc[0]], \
             [yc[0], yc[1], yc[2], yc[3], yc[0]], \
             'k-', marker='o', mec='k', ms=12)
    plt.plot(xx[::10,::10][mask[::10,::10]], \
             yy[::10,::10][mask[::10,::10]], \
             linestyle='', marker='o', mfc='w', mec='r',  ms=5)
    plt.plot(xx[::10,::10], yy[::10,::10], 'k.', ms=1)
    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('Step 4: Find source points inside target grid cell')
    fig.subplots_adjust(left=0.0, top=0.95)
    plt.savefig('nalcms_demo_step4.png')
    plt.close(fig)
    
    # Step 5: Read the land use data in target grid cell
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect='equal')
    plt.plot([xc[0], xc[1], xc[2], xc[3], xc[0]], \
             [yc[0], yc[1], yc[2], yc[3], yc[0]], \
             'k-', marker='o', mec='k', ms=12)
    plt.scatter(xx[mask], yy[mask], c=data[mask], s=1)
    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('Step 5: Read landuse data in target grid cell')
    fig.subplots_adjust(left=0.0, top=0.95)
    plt.savefig('nalcms_demo_step5.png')
    plt.close(fig)

    dist = np.bincount(data[mask], minlength=len(CLASSES.keys()))

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    plt.bar(CLASSES.keys(), dist / np.sum(dist))
    plt.xticks(list(CLASSES.keys()), rotation=90)
    ax.set_xticklabels(list(CLASSES.values()))
    plt.ylabel('Fraction')
    plt.title('Step 6: Distribution of landuse categories in target grid cell')
    fig.subplots_adjust(bottom=0.6, top=0.95)
    plt.savefig('nalcms_demo_step6.png')
    plt.close(fig)

