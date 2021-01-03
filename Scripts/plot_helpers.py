""" plot_helpers - functions to help plot things 

"""
import pandas as pd
import holoviews as hv
from colorcet import fire
from holoviews.operation.datashader import rasterize

def plot_points(df, width=700, height=500):
    """ Given a dataframe with columns "lat" and "lon", returns a datashader
    plot suitable for embedding in a Panel layout.
    """
    eastings, northings = hv.util.transform.lon_lat_to_easting_northing(df['lon'], df['lat'])

    tiles = hv.element.tiles.ESRI().redim(x='easting', y='northing')

    r = rasterize(hv.Points(pd.DataFrame({'northing':northings, 
                    'easting':eastings}), ['easting', 'northing']))

    return tiles * r.opts(cmap=fire[180:], width=width, height=width,
            cnorm='eq_hist', alpha=0.5)


def plot_visibility(hits, mmsi):
    """ Render a histogram plot of all the times that a vessel was visible
    """
    pass
