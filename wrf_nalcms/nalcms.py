import matplotlib.path as path
import numpy as np
from pyproj import Proj


NALCMS_CLASSES = {
    0: {'name': 'No data', 'wrf_class': None},
    1: {'name': 'Temperate or sub-polar needleleaf forest', 'wrf_class': 18},
    2: {'name': 'Sub-polar taiga needleleaf forest', 'wrf_class': 1},
    3: {'name': 'Tropical or sub-tropical broadleaf evergreen forest', 'wrf_class': 2},
    4: {'name': 'Tropical or sub-tropical broadleaf deciduous forest', 'wrf_class': 4},
    5: {'name': 'Temperate or sub-polar broadleaf deciduous forest', 'wrf_class': 4},
    6: {'name': 'Mixed Forest', 'wrf_class': 5},
    7: {'name': 'Tropical or sub-tropical shrubland', 'wrf_class': 7},
    8: {'name': 'Temperate or sub-polar shrubland', 'wrf_class': 7},
    9: {'name': 'Tropical or sub-tropical grassland', 'wrf_class': 9},
    10: {'name': 'Temperate or sub-polar grassland ', 'wrf_class': 10},
    11: {'name': 'Sub-polar or polar shrubland-lichen-moss', 'wrf_class': 19},
    12: {'name': 'Sub-polar or polar grassland-lichen-moss', 'wrf_class': 19},
    13: {'name': 'Sub-polar or polar barren-lichen-moss', 'wrf_class': 20},
    14: {'name': 'Wetland', 'wrf_class': 11},
    15: {'name': 'Cropland', 'wrf_class': 12},
    16: {'name': 'Barren Lands', 'wrf_class': 16},
    17: {'name': 'Urban and Built-up', 'wrf_class': 13},
    18: {'name': 'Water', 'wrf_class': 17},
    19: {'name': 'Snow and Ice', 'wrf_class': 15}
}


def get_grid_cell_corner_latlon(i: int, j: int, lat: np.ndarray, lon: np.ndarray, extent: int=1):
    """Given i, j indices and lat and lon arrays, returns latitude 
    and longitude of 4 corners of the grid cell at (j, i)."""
    jc = [j, j, j+extent, j+extent]
    ic = [i, i+extent, i+extent, i]
    return lat[jc, ic], lon[jc, ic]


def get_grid_cell_polygon(xc: np.ndarray, yc: np.ndarray) -> path.Path:
    """Returns a matplotlib polygon (path.Path instance)
    given x and y coordinates as 1-d arrays."""
    return path.Path(np.vstack((xc, yc)).T)


def get_nalcms_data_in_target_grid_cell(i0, j0, latc, lonc, projection, ds, extent=1):
    """Returns (x, y) coordinates, data, and logical mask arrays
    of landuse on source grid that fit in a target grid cell (j0, i0)."""
    corner_lat, corner_lon = get_grid_cell_corner_latlon(i0, j0, latc, lonc, extent=extent)
    xc, yc = projection(corner_lon, corner_lat)
    
    jmax, imin = ds.index(np.min(xc), np.min(yc))
    jmin, imax = ds.index(np.max(xc), np.max(yc))

    xsrc = np.linspace(ds.xy(0, imin)[0], ds.xy(0, imax)[0], \
                       imax - imin + 1, endpoint=True)
    ysrc = np.linspace(ds.xy(jmin, 0)[1], ds.xy(jmax, 0)[1], \
                       jmax - jmin + 1, endpoint=True)
    xx, yy = np.meshgrid(xsrc, ysrc)
    
    source_grid_cells = np.vstack((xx.flatten(), yy.flatten())).T
    target_grid_cell = get_grid_cell_polygon(xc, yc)
    
    mask = target_grid_cell.contains_points(source_grid_cells).reshape(xx.shape)
    data = ds.read(window=((jmin, jmax + 1), (imin, imax + 1)))[0,:,:]
    
    return xx, yy, data, mask, xc, yc


def process_nalcms_to_geo_em_all(nalcms, geo_em, urban_multi=True):
    
    # get the projection from the NALCMS dataset
    projection = Proj(nalcms.crs)

    lon = np.array(geo_em.XLONG_M[0,:,:])
    lat = np.array(geo_em.XLAT_M[0,:,:])
    latc = np.array(geo_em.XLAT_V[0,:,:])
    lonc = np.array(geo_em.XLONG_U[0,:,:])

    jm, im = lon.shape

    geo_em.LANDUSEF[:] = 0
    geo_em.FRC_URB2D[:] = 0

    for j in range(jm-1):
        print('Processing row', j, '/', jm)
        for i in range(im-1):
            xx, yy, data, mask, xc, yc = \
                get_nalcms_data_in_target_grid_cell(i, j, latc, lonc, projection, nalcms)

            # skip if we are out of bounds of source data
            if not data.shape == mask.shape:
                continue

            # skip if point is found but no landcover data
            if np.all(data == 0):
                continue

            bincount = np.bincount(data[mask])
            fractions = bincount / np.sum(bincount)
            dominant_class = np.argmax(fractions) 

            # skip if dominant bin is "no data"
            if dominant_class == 0:
                continue

            # set fraction for each landuse index
            for n in range(1, fractions.size):
                geo_em.LANDUSEF[0,NALCMS_CLASSES[n]['wrf_class']-1,j,i] = fractions[n]
            
            # set landuse index
            geo_em.LU_INDEX[0,j,i] = NALCMS_CLASSES[dominant_class]['wrf_class']
           
            # set urban fraction and multi-classes
            if fractions.size > 17:
                geo_em.FRC_URB2D[0,j,i] = fractions[17]
                
                if urban_multi and dominant_class == 17:
                    if fractions[dominant_class] >= 0.95:
                        geo_em.LU_INDEX[0,j,i] = 33
                    elif fractions[dominant_class] >= 0.9:
                        geo_em.LU_INDEX[0,j,i] = 32
                    elif fractions[dominant_class] >= 0.6:
                        geo_em.LU_INDEX[0,j,i] = 31
                    else:
                        geo_em.LU_INDEX[0,j,i] = NALCMS_CLASSES[dominant_class]['wrf_class']

    geo_em.to_netcdf('geo_em.d%2.2i.new.nc' % geo_em.grid_id)



def process_nalcms_to_geo_em_urban(nalcms, geo_em, urban_multi=True):
    
    # get the projection from the NALCMS dataset
    projection = Proj(nalcms.crs)

    lon = np.array(geo_em.XLONG_M[0,:,:])
    lat = np.array(geo_em.XLAT_M[0,:,:])
    latc = np.array(geo_em.XLAT_V[0,:,:])
    lonc = np.array(geo_em.XLONG_U[0,:,:])

    jm, im = lon.shape

    # initialize urban fraction
    geo_em.FRC_URB2D[:] = 0
            
    for j in range(jm-1):
        print('Processing row', j, '/', jm)
        for i in range(im-1):
            xx, yy, data, mask, xc, yc = \
                get_nalcms_data_in_target_grid_cell(i, j, latc, lonc, projection, nalcms)

            # skip if we are out of bounds of source data
            if not data.shape == mask.shape:
                continue

            # skip if point is found but no landcover data
            if np.all(data == 0):
                continue

            bincount = np.bincount(data[mask])
            fractions = bincount / np.sum(bincount)
            dominant_class = np.argmax(fractions) 
                
            # set urban fraction
            if fractions.size > 17:
                geo_em.FRC_URB2D[0,j,i] = fractions[17]

            # set landuse index
            if dominant_class == 17:
                if urban_multi:
                    if fractions[dominant_class] >= 0.95:
                        geo_em.LU_INDEX[0,j,i] = 33
                    elif fractions[dominant_class] >= 0.9:
                        geo_em.LU_INDEX[0,j,i] = 32
                    elif fractions[dominant_class] >= 0.6:
                        geo_em.LU_INDEX[0,j,i] = 31
                    else:
                        geo_em.LU_INDEX[0,j,i] = NALCMS_CLASSES[dominant_class]['wrf_class']
                else:
                    geo_em.LU_INDEX[0,j,i] = NALCMS_CLASSES[dominant_class]['wrf_class']

    # set landuse fraction for urban class only; leave others alone
    geo_em.LANDUSEF[0,NALCMS_CLASSES[17]['wrf_class']-1,:,:] = geo_em.FRC_URB2D[0,:,:]
            
    geo_em.to_netcdf('geo_em.d%2.2i.new.nc' % geo_em.grid_id)
