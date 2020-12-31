"""
Intersection logic for a satellite track and a series of (lat,long,timestamp)

Given: a satellite's trajectory, and a list of ships' locations at various 
points in time, we need to return the list of time periods & points where
a satellite could see each ship.

The temporal resolution of the satellite motion is every minute, while
AIS pings are typically every 2-5 minutes, although sometimes they update
more frequently (e.g. close in to harbor).

We have precomputed the trajectory of every satellite over the time periods
of interest, and stored them in a HDF5 file for fast retrieval.

The pseudocode for the algorithm is:

    for each vessel:
      for each year:
        ais = load_ais(vessel, year)     # quantize ais timestamp to the minute
        sat_track = get_sat_track_for_year(year)
        start_index = sat_track.searchsorted(ais.date_time[0])
        sat_loc = sat_track[start_index : len(ais)]
        hit_mask = ... # perform Euclidean distance filter against satellite FOV
        hits[vessel].append(ais[hit_mask])


The basic algorithm is:
  1. Compute a set of interpolated satellite lat/longs for an input list
     of timestamps.
  
  2. Compute the distance of each AIS ping from the satellite location
     at each time point.
  
  3. Filter based on FOV calculation.

"""

import numpy as np
from numpy import float64
from math import pi, cos, sin, asin, acos, sqrt, atan2
import pandas as pd
from pandas import DataFrame
import datetime as dt
from numba import njit, guvectorize
import time

# Number of degrees off the horizon that a satellite must be
# in order for it to count as being able to "see" a ship
MIN_HORIZON_ELEVATION = float64(0)

# If set to True, then dumps out debug timing info etc.
PRINT_INFO = False

EARTH_RADIUS = 6371.0  # radius of earth, in km

@njit(inline="always", fastmath=True)
def haversine_angle(lon1, lat1, lon2, lat2):
    """ haversine angle between two points, returned in radians 
    """
    # convert decimal degrees to radians 
    dlon = (lon2 - lon1) / 180.0 * pi
    dlat = (lat2 - lat1) / 180.0 * pi

    # haversine formula 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 

    #R = 6371.0 # Radius of earth in kilometers
    return c
    

@guvectorize(["float64[:], float64[:], float64[:], float64[:], float64[:], float64[:], float64[:], boolean[:]"],
              "(m),(m),(m),(m),(n),(n),(n)->(n)", nopython=True, fastmath=True, target="parallel")
def _compute(sat_time, sat_lat, sat_long, sat_alt, v_time, v_lat, v_long, output):
    """ Vectorized, JITted function to return list of vessel locations that
    were observed by the satellite.

    Satellite data: (minimum length-2 array)
    sat_time: datetime64, sorted
    sat_lat, sat_long: float64
    sat_alt: float32  (satellite distance from center-of-earth, in KM)

    Vessel data: 
    v_time: datetime64, sorted
    v_lat, v_long: float32

    output: bool; True if point is a hit, False otherwise

    """

    # The basic algorithm:
    #  1. For each AIS time point within the vessel data, find the two 
    #     closest satellite time points
    #  2. Do a simple interpolation of the satellite position to the exact
    #     AIS time point.
    #  3. Compute the haversine_angle() between the satellite position
    #     and the AIS coordinates.
    #  4. If less than or equal to max_visible_angle, then store the
    #     vessel information in the new output

    # A few notes on the algorithm:
    #   1. sat_time is sorted, and v_time is sorted. Thus we can just
    #      make one pass through the array
    #   2. v_times are often duplicated, so it's worth caching the last 
    #      interpolated value of the satellite
    #   3. Although the input lat/long are in float32, we cast to float64 for the computation

    min_horizon_angle = MIN_HORIZON_ELEVATION/180.0*pi 

    # Handle the case when we have AIS data that is before the first sat data
    # Now find the starting index into the satellite data
    sat_idx = 1
    sat_left = sat_time[sat_idx - 1]
    sat_right = sat_time[sat_idx]
    sat_length = sat_time.shape[0]
    dirty = True

    for i in range(v_time.shape[0]):
        vtime = v_time[i]

        # Sweep to the correct interval in the satellite data
        if vtime < sat_left:
            continue
        while vtime >= sat_right:
            sat_idx += 1
            if sat_idx == sat_length:
                return
            sat_left = sat_right
            sat_right = sat_time[sat_idx]
            dirty = True

        # Loop condition: sat_left <= vtime < sat_right

        if dirty:
            dirty = False
            time_diff = sat_right - sat_left
            lat_left, lat_right = sat_lat[sat_idx - 1], sat_lat[sat_idx]
            lng_left, lng_right = sat_long[sat_idx - 1], sat_long[sat_idx]
            alt_left, alt_right = sat_alt[sat_idx - 1], sat_alt[sat_idx]

        # Interpolate the lat, long, and altitude values
        alpha = (vtime - sat_left) / time_diff
        beta = (sat_right - vtime) / time_diff
        sat_interp_lat  = beta * lat_left + alpha * lat_right
        sat_interp_long = beta * lng_left + alpha * lng_right
        sat_interp_alt  = beta * alt_left + alpha * alt_right

        if sat_interp_alt < EARTH_RADIUS:
            sat_interp_alt = EARTH_RADIUS

        if MIN_HORIZON_ELEVATION < 1e6:
            # if horizon elevation is nearly 0, then do optimized FOV calc
            sat_fov_max_angle = acos(EARTH_RADIUS / sat_interp_alt)
        else:
            sat_fov_max_angle = pi/2 - min_horizon_angle - \
                    asin(EARTH_RADIUS/sat_interp_alt * sin(min_horizon_angle+pi/2))

        angle = haversine_angle(sat_interp_long, sat_interp_lat, v_long[i], v_lat[i])
        if angle <= sat_fov_max_angle:
            output[i] = True
    
    # No return value; output is written into **output** array.
    return 


def compute_hits(sat_track: DataFrame, vessel_points: DataFrame, workers=None) -> DataFrame:
        #start_time: dt.datetime, end_time: dt.datetime) -> DataFrame:
    """ Returns a list of points that fall within a satellite track.
    Assumes a FOV of half-earth.

    sat_track: DataFrame["date_time", "lat", "long", "alt"]
    
    vessel_points: DataFrame["MMSI", "date_time", "lat", "long"]

    start: starting index to work on
    numrows: number of rows to process. If None, then process all remaining rows

    Returns:
        a DataFrame with the same columns as input `points`
    """
    sat_length = len(sat_track)
    if sat_length < 2:
        raise (ValueError, "Satellite track data must have minimum array length 2")

    start_time = time.time()
    sat_args = (sat_track["date_time"].to_numpy(dtype=float64),
                sat_track["lat"].to_numpy(dtype=float64),
                sat_track["long"].to_numpy(dtype=float64),
                sat_track["alt"].to_numpy(dtype=float64))
    vsl_args = (vessel_points["date_time"].to_numpy(dtype=float64),
                vessel_points["lat"].to_numpy(dtype=float64),
                vessel_points["long"].to_numpy(dtype=float64))
    numvessels = len(vessel_points)
    hit_mask = np.zeros(numvessels, dtype=bool)
    if workers is None:
        workers = 4
        while workers < 32 and (numvessels % (2 * workers)) == 0:
            workers *= 2
    if PRINT_INFO:
        print('Using %d chunks' % workers)

    if workers > 1:
        chunksize = int(numvessels / workers)
        totalsize = chunksize * workers
        _compute(*sat_args,
                 *(np.reshape(v[:totalsize], (-1, chunksize)) for v in vsl_args),
                 np.reshape(hit_mask[:totalsize], (-1, chunksize)))
        if numvessels > totalsize:
            _compute(*sat_args,
                     *(v[totalsize:] for v in vsl_args),
                     hit_mask[totalsize:])
    else:
        _compute(*sat_args, *vsl_args, hit_mask)
    comp_time = time.time()

    res = vessel_points[hit_mask]
    if PRINT_INFO:
        print("  compute time: %.6f"%(comp_time - start_time), "\t extract time: %.6f"%(time.time() - comp_time))
    return res
