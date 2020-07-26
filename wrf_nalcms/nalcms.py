import matplotlib.path as path
import numpy as np


CLASSES = {
    0: 'No data',
    1: 'Temperate or sub-polar needleleaf forest',
    2: 'Sub-polar taiga needleleaf forest',
    3: 'Tropical or sub-tropical broadleaf evergreen forest',
    4: 'Tropical or sub-tropical broadleaf deciduous forest',
    5: 'Temperate or sub-polar broadleaf deciduous forest',
    6: 'Mixed Forest',
    7: 'Tropical or sub-tropical shrubland',
    8: 'Temperate or sub-polar shrubland',
    9: 'Tropical or sub-tropical grassland',
    10: 'Temperate or sub-polar grassland ',
    11: 'Sub-polar or polar shrubland-lichen-moss',
    12: 'Sub-polar or polar grassland-lichen-moss',
    13: 'Sub-polar or polar barren-lichen-moss',
    14: 'Wetland',
    15: 'Cropland',
    16: 'Barren Lands',
    17: 'Urban and Built-up',
    18: 'Water',
    19: 'Snow and Ice'
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
