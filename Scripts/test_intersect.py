""" Test for the intersector code """

import numpy as np
import pandas as pd
import datetime
import time

EARTH_RADIUS = 6371.0  # kilometers

def load_ais(datapath: str):
    """ Returns a dict mapping years (int) to dataframes that have dtype
            mmsi_id               int64
            date_time    datetime64[ns]
            lat                 float32
            lon                 float32
    
    The dataframes are sorted by mmsi_id, and within each id, are sorted
    ascending by time.
    """
    pass


def create_dummy_sat_track():
    from skyfield.sgp4lib import EarthSatellite
    from skyfield.framelib import itrs
    from skyfield import api
    ts = api.load.timescale()

    tle1 = "1 07195U 73086FD  09365.98624744  .00000168  00000-0  31070-3 0  3918\\"
    tle2 = "2 07195 103.2086 165.3351 0336236 191.7936 167.5149 13.40434914746112"

    sat = EarthSatellite(tle1, tle2)
    jds = ts.tt_jd(np.linspace(sat.epoch.tt - 0.5, sat.epoch.tt +0.5, 24*60))
    np_times = pd.Series(jds.utc_datetime()).to_numpy(np.datetime64)
    
    lats, longs, dists = sat.at(jds).frame_latlon(itrs)
    return pd.DataFrame({"date_time": np_times, "lat": lats.degrees, 
        "long": longs.degrees, "alt": dists.km})

df = create_dummy_sat_track()

def create_dummy_data(numsatpoints = 4000, numaispoints=1_000_000):
    # Create a simple West-East satellite track
    sat_time = np.linspace(0, 120, numsatpoints, dtype=np.float64)
    sat_lat = 30.0 * np.ones_like(sat_time)
    sat_long = np.linspace(-110.0, -100.0, numsatpoints)
    sat_alt = np.zeros_like(sat_time) + EARTH_RADIUS + 200

    sat_track = pd.DataFrame({"date_time": sat_time, "lat": sat_lat,
        "long": sat_long, "alt": sat_alt})

    vessel_df = pd.DataFrame({
            "date_time": np.linspace(30, 110, numaispoints, dtype=np.float64),
            "MMSI": np.zeros(numaispoints,dtype=np.int64) + 3456,
            "lat": np.linspace(25.0, 40.0, numaispoints),
            "long": np.linspace(-108.0, -102.0, numaispoints) })

    return sat_track, vessel_df

def check_values(sat, hits):
    # For each value in hits, look up the satellite time and location,
    # and manually do a calculation to compute FOV.
    pass

if __name__ == "__main__":
    import intersect
    from intersect import compute_hits, compute_hits_parallel
    intersect.PRINT_INFO = True

    num_sat = 4000
    num_ais = 10_000_000

    print(f"Satellite track pts: {num_sat:,}; \tAIS points: {num_ais:,}")
    sat, vessels = create_dummy_data(num_sat, num_ais)
    start = time.time()
    hits = compute_hits(sat, vessels) #, start=400000, numrows=100000)
    #hits = compute_hits_parallel(sat, vessels, workers=4)
    delta = time.time() - start
    #print(hits)
    print("Total Wall Clock Time:", delta)
    


