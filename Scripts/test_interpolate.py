
from interpolate_ais import interpolate_track
import numpy as np
import pandas as pd
dt64 = np.datetime64

def make_track(start, stop, dt, numpoints = 20, start_time=dt64("2014-10-01T09:00:00", "s")):
    """ 
    start, stop are tuples (lat, lon)
    dt is in seconds
    """
    times = np.arange(start_time, start_time+dt, np.timedelta64(dt//numpoints), dtype="<M8[s]")
    
    start = np.array(start, dtype=np.float64)
    stop = np.array(stop, dtype=np.float64)
    dlat = (stop[0] - start[0]) / numpoints
    dlon = (stop[1] - start[1]) / numpoints
    
    lats = np.arange(numpoints) * dlat + start[0]
    lons = np.arange(numpoints) * dlon + start[1]

    MMSI = np.empty(len(times), dtype=int)
    MMSI.fill(12345)
    
    return pd.DataFrame({"mmsi_id": MMSI, "date_time": times, "lat": lats, "lon": lons})

def test1():
    df = make_track((0,0), (10, 10), dt=100*60, numpoints=10)
    print("*** original track ***")
    print(df)
    idf = interpolate_track(df, maxdt=150)
    print("*** interpolated track ***")
    print(idf)

if __name__ == "__main__":
    test1()
