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
from math import pi, cos, sin, asin, acos, sqrt
import pandas as pd
from pandas import DataFrame
import datetime as dt
from numba import njit, jit
import time

# Number of degrees off the horizon that a satellite must be
# in order for it to count as being able to "see" a ship
MIN_HORIZON_ELEVATION = 30

# If set to True, then dumps out debug timing info etc.
PRINT_INFO = False


@njit(inline="always", fastmath=True)
def haversine_angle(lon1, lat1, lon2, lat2):
    """ haversine angle between two points, returned in radians 
    """
    # convert decimal degrees to radians 
    dlon = (lon2 - lon1) / 180.0 * pi
    dlat = (lat2 - lat1) / 180.0 * pi

    # haversine formula 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    #R = 6371.0 # Radius of earth in kilometers
    return c
    

@njit(inline="always", fastmath=True)
def _get_index_with_hint(sat_time, time, index_hint=0):
    """ returns the index value into sat_time that immediately preceeds
    the value of **time**. index_hint provides a starting value to 
    search from.

    If **time** falls outside of the values in sat_time, or prior to
    sat_time[index_hint], then returns -1.
    """
    idx = index_hint
    length = sat_time.shape[0]
    if time < sat_time[idx]:
        return -1
    while idx < length-2:
        if sat_time[idx+1] < time:
            idx += 1
        else:
            break
    
    if idx == length - 2:
        if time < sat_time[idx+1]:
            return idx
        else:
            return -1
    else:
        return idx


@njit
def _compute(sat_time, sat_lat, sat_long, sat_alt, v_mmsi, v_time, v_lat, v_long, output):
    """ Vectorized, JITted function to return list of vessel locations that
    were observed by the satellite.

    Satellite data: (minimum length-2 array)
    sat_time: datetime64, sorted
    sat_lat, sat_long: float64
    sat_alt: float32  (satellite distance from center-of-earth, in KM)

    Vessel data: 
    v_mmsi: int64
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

    sat_length = len(sat_time)
    if sat_length < 2:
        raise (ValueError, "Satellite track data must have minimum array length 2")

    min_horizon_angle = MIN_HORIZON_ELEVATION/180.0*pi 
    R = 6371.0  # radius of earth, in km

    oldvtime = -1.0     # stores previous vessel AIS time point

    sat_interp_lat = 0.0    # Satellite data interpolated to the AIS time
    sat_interp_long = 0.0   # 
    sat_interp_alt = 0.0    #
    sat_fov_max_angle = 0.0

    # Handle the case when we have AIS data that is before the first sat data
    i=0
    while v_time[i] < sat_time[0]:
        output[i] = False
        i += 1
        
    # Now find the starting index into the satellite data
    sat_idx = _get_index_with_hint(sat_time, v_time[i])

    for i in range(i, v_mmsi.shape[0]):
        # Find the appropriate indices in the satellite data
        vtime = v_time[i]
        if vtime != oldvtime:
            new_idx = _get_index_with_hint(sat_time, vtime, sat_idx)
            if new_idx == -1:
                # the AIS data now exceeds the time range of the
                # satellite data. This generally shouldn't happen
                # but if it does, then we're done with intersection.
                break
            sat_idx = new_idx

            # At this point, sat_idx points to the sat_track time point
            # that's right after the time in v_time.
            assert sat_time[sat_idx] <= vtime < sat_time[sat_idx+1]

            # Interpolate the lat, long, and altitude values.
            
            cur = sat_idx
            prev = sat_idx-1
            scale_factor = (vtime - sat_time[prev]) / (sat_time[cur]-sat_time[prev])
            sat_interp_lat = scale_factor * (sat_lat[cur]-sat_lat[prev]) + sat_lat[prev]
            sat_interp_long = scale_factor * (sat_long[cur]-sat_long[prev]) + sat_long[prev]
            sat_interp_alt = scale_factor * (sat_alt[cur]-sat_alt[prev]) + sat_alt[prev]
            
            sat_fov_max_angle = pi/2 - min_horizon_angle - \
                    asin(R/(sat_interp_alt) * sin(min_horizon_angle+pi/2))

            # Store the time we just did the interpolation computation for.
            # If following vessel AIS times are the same as this one, we can
            # reuse the sat_interp_* values.
            oldvtime = vtime

        angle = haversine_angle(sat_interp_long, sat_interp_lat, v_long[i], v_lat[i])
        output[i] = (angle <= sat_fov_max_angle)


def compute_hits(sat_track: DataFrame, vessel_points: DataFrame, start=0, numrows=None) -> DataFrame:
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
    start_time = time.time()
    if numrows is None:
        end = len(vessel_points)
    else:
        end = start+numrows
    
    hit_mask = np.zeros(end - start, dtype=bool)

    args = (sat_track["date_time"].to_numpy(dtype=float64),  # TODO: ensure conversion to datetime64
            sat_track["lat"].to_numpy(dtype=float64),
            sat_track["long"].to_numpy(dtype=float64),
            sat_track["alt"].to_numpy(dtype=float64),
            vessel_points["MMSI"].to_numpy()[start:end],
            vessel_points["date_time"].to_numpy(dtype=float64)[start:end],   #TODO: ensure conversion to datetime64
            vessel_points["lat"].to_numpy(float64)[start:end],
            vessel_points["long"].to_numpy(float64)[start:end])

    _compute(*args, hit_mask)
    comp_time = time.time()
    res = vessel_points[start:end][hit_mask]
    if PRINT_INFO:
        print("  compute time: %.6f"%(comp_time - start_time), "\t extract time: %.6f"%(time.time() - comp_time))
    return res

    
def compute_hits_parallel(sat: DataFrame, vessels: DataFrame, workers=4) -> DataFrame:
    import dask
    import dask.multiprocessing
    dask.config.set(scheduler="threads", num_workers=workers)
    
    numvessels = len(vessels)
    chunksize = int(numvessels / workers)
    chunk_args = [(i*chunksize, chunksize if i<workers-1 else None) for i in range(workers)]
    delayed_results = []
    for start, numrows in chunk_args:
        delayed_results.append(dask.delayed(compute_hits)(sat, vessels, start=start, numrows=numrows))

    results = dask.compute(*delayed_results)
    return results

