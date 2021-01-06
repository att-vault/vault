"""
Creates interpolated AIS pings for ships.

As part of the workflow, this should be run on the ais_*.h5 files to generate
derived ais_*.interp.h5 files.

The reason we need to generate synthetic points is because the visibility 
algorithm in intersect.py is fundamentally a point-visibility problem, and
it's indexed on time.

If a ship "goes dark" but shows up again, without having strayed too far
from its previous location, then we assume it's the same contiguous
"track" and we can fill in the gap with some synthetic points.
If the gap in space is too large, then we cannot make any assumptions
about what happened to the ship in between.
"""

from math import atan2, cos, pi, sin, sqrt
import numpy as np
import pandas as pd
from numba import njit, jit

# If set to True, then dumps out debug timing info etc.
PRINT_INFO = False

@njit(fastmath=True)
def haversine_dist(lon1, lat1, lon2, lat2):
    """ haversine distance between two points, returned in km
    """
    # convert decimal degrees to radians 
    dlon = (lon2 - lon1) / 180.0 * pi
    dlat = (lat2 - lat1) / 180.0 * pi

    # haversine formula 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 

    R = 6371.0 # Radius of earth in kilometers
    return c * R
    
def interpolate_track(vessels: pd.DataFrame, maxdist=200, maxdt=300):
    """ Returns a new dataframe with interpolated points for the vessel.
    
    Inputs
    ------
    vessels: dataframe with columns ["mmsi_id", "date_time", "lat", "long"];

    maxdist: maximum distance in kilometers between two succesive points,
        beyond which we will not try to insert more interpolated points
    maxdt: maximum temporal gap between interpolated points, in seconds

    Returns:
    A new dataframe of the same schema as **vessels**.  Time will be in 
    seconds.
    """

    # convert to seconds b/c that's the units of maxdt
    times = vessels["date_time"].to_numpy(dtype="<M8[s]").astype("int64")

    outrows = []
    for i, row in enumerate(vessels.itertuples(index=False)):
        
        outrows.append(row)  # always include the input point

        if i == len(vessels)-1:
            break
        if row[0] != vessels.iloc[i+1][0]:
            # started a new MMSI_id
            continue
        
        if (times[i+1] - times[i] > maxdt):
            lat2, lon2 = vessels.iloc[i+1][2:]
            lat, lon = row[2:]
            dist = haversine_dist(lon, lat, lon2, lat2)
            
            if dist > maxdist:
                continue

            # Find an average velocity that get the ship to point2 within
            # the alloted time.  Then, make new points every maxdt seconds
            # Note, we do not do any kind of feasibility exclusion on whether
            # this is a reasonable speed for a vessel.
            numsegments = int(np.ceil((times[i+1] - times[i]) / maxdt))
            dlat = (lat2 - lat) / numsegments
            dlon = (lon2 - lon) / numsegments
            dt = (times[i+1] - times[i]) / numsegments
            outrows.extend((row[0], np.datetime64(int(dt*j+times[i]),"s"), dlat*j+lat, dlon*j+lon)
                            for j in range(1,numsegments))
    
    return pd.DataFrame(outrows).astype({"mmsi_id":np.int64, "date_time":np.datetime64,
                    "lat":np.float32, "lon":np.float32})


def main():
    import os, sys, time
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the input HDF5-formatted AIS file", type=str)
    parser.add_argument("-i", "--interval", help="the approximate time gap, in seconds,"
                        " between interpolated points", default=300, type=int)
    parser.add_argument("-d", "--distance", help="the maximum range, in km, between"
                        "successive points, in which we will perform interpolation",
                        default=200, type=int)
    parser.add_argument("-c", "--complevel", help="compression level of output HDF5",
                        default=3, type=int)
    parser.add_argument("-o", "--output", help="the output filename. defaults to INPUT.interp.h5")
    args = parser.parse_args()

    filename = args.filename
    if not os.path.exists(filename):
        print("Cannot find", filename)
        sys.exit()

    if args.output:
        outfile = args.output
    else:
        base, ext = os.path.splitext(filename)
        outfile = os.path.join(base+".interp.h5")
    
    if os.path.exists(outfile):
        # append timestamp
        outfile = outfile + str(int(time.time()))

    print("Reading", filename, "; output into", outfile)
    df = pd.read_hdf(filename)
    start_time = time.time()
    idf = interpolate_track(df, args.distance, args.interval)
    end_time = time.time()
    print(f"Interpolation of {len(df)} points took", end_time-start_time, "seconds")
    idf.to_hdf(outfile, "interp_data", complevel=args.complevel)
    print(f"Wrote {len(idf)} interpolated points to", outfile)

if __name__ == "__main__":
    main()
