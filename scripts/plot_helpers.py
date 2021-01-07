""" plot_helpers - functions to help plot things 

"""
import numpy as np
import pandas as pd
import holoviews as hv
from colorcet import fire
from holoviews.operation.datashader import rasterize, dynspread

def plot_points(df, width=700, height=500):
    """ Given a dataframe with columns "lat" and "lon", returns a datashader
    plot suitable for embedding in a Panel layout.
    """
    eastings, northings = hv.util.transform.lon_lat_to_easting_northing(df['lon'], df['lat'])

    tiles = hv.element.tiles.ESRI().redim(x='easting', y='northing')

    r = dynspread(rasterize(hv.Points(pd.DataFrame({'northing':northings, 
                            'easting':eastings}), ['easting', 'northing'])))

    return tiles * r.opts(cmap=fire[180:], width=width, height=width,
                          cnorm='eq_hist', alpha=0.8)


def plot_satellite(lats, lons, lat_clip=85.5):
    """ Returns a holoviews Curve that shows a satellite track. 
    Longitudes are assumed to be between (-180,180), i.e. no correction is done on them.
    """
    lats = lats.to_numpy()
    lons = lons.to_numpy()
    mask = np.abs(lats) > lat_clip
    lats[mask] = np.nan
    lons[mask] = np.nan

    eastings, northings = hv.util.transform.lon_lat_to_easting_northing(lons,lats)
    # Heuristic to insert NaNs to break up Curve (prevent wrapping issues at date line)
    inds = np.where(np.abs(np.diff(eastings)) > 2e7)[0] # Big delta to split on
    inds += 1
    eastings  = np.insert(eastings,  inds, [np.nan for i in range(len(inds))])
    northings = np.insert(northings, inds, [np.nan for i in range(len(inds))])
    return hv.Curve((eastings, northings)).opts(color='red')

def plot_visibility(hits, mmsi):
    """ Render a histogram plot of all the times that a vessel was visible
    """
    pass
