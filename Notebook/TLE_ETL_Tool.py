from datetime import datetime, timedelta
import itertools
import os
import tempfile
import urllib.request
import zipfile

from tables import *

import skyfield
from skyfield.sgp4lib import EarthSatellite


# Structure of the pytables table we are going to create
class TLE(IsDescription):
    epoch     = Float64Col(pos=0)
    norad_id  = Int64Col(pos=1)
    line_one  = StringCol(80, pos=2)
    line_two  = StringCol(80, pos=3)


def read_tles_from_zip(path: str):
    """
    Iterate through the rows in the TLE file inside of a zip file.
    """
    with zipfile.ZipFile(path) as z:
        # Assumes only one file contained inside the zip, ignores OSX detritus
        name = list(filter(lambda fn: "_MACOSX" not in fn, z.namelist()))[0]
        with z.open(name) as flo:
            for _ in itertools.count():
                tle1 = flo.readline().decode().strip()
                if not tle1: break
                tle2 = flo.readline().decode().strip()
                sat = EarthSatellite(tle1, tle2)

                epoch = sat.epoch.utc_datetime().timestamp()
                norad_id = sat.model.satnum

                yield epoch, norad_id, tle1, tle2


def read_to_table(table_node, src_iter, limit=float("inf")):
    """
    Given an iterable (likely consturcted from one of the above) and a table.
    Populate the table with values from the interable.
    """
    
    entry = table_node.row
    
    for i, (epoch, norad_id, tle1, tle2) in enumerate(src_iter):
        entry["epoch"] = epoch
        entry["norad_id"] = norad_id
        entry["line_one"] = tle1
        entry["line_two"] = tle2
        
        entry.append()
            
        if i % 1000 == 0:
            table_node.flush()
            
        if i > limit:
            break
            
    table_node.flush()

def build_indices(table):
    print("Building indices")
    table.cols.epoch.create_index()
    table.cols.norad_id.create_index()


if __name__ == "__main__":
    import argparse

    usage = """
    This is a tool for importing TLE data for the Vault Project.
    It works in 3 phases:
     1. Extract and load the raw TLE data from the AWS bucket. This includes
       * Extracting the epoch and noradID for indexing
       * Accruing them into a large table - `/raw`
     2. These records are then thinned down to the date ranges that overlap
       the AIS tracks - `/reduced`
     3. The records that remain are sorted and indexed on time and noradID - `/sat`
    """

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument(
        "--limit",
        type=int,
        default=1000000000,
        help="Specify the limit to the number of TLE records to load from any one file")

    parser.add_argument(
        "--save_raw",
        default=False,
        action="store_true",
        help="Keep the raw exports (>20GB)")

    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    raw_data_urls = [
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_1of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_2of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_3of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_4of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_5of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_6of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_7of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2004_8of8.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2005.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2006.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2007.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2008.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2009.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2010.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2011.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2012.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2013.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2014.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2015.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2016.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2017.txt.zip",
        "https://afdata.s3-us-gov-west-1.amazonaws.com/Scenario_Data/TLE/tle2018.txt.zip"
    ]

    # Phase 1, get and ingest data
    h5file = open_file(args.output, mode="w", title="TLE Indexable Data")
    raw_tle = h5file.create_table(h5file.root, 'tle_raw', TLE, "Main TLE Listing")

    print("Step 1/3 - Ingesting Raw Data")
    # Process each of the input files in sequence
    for url in raw_data_urls:
        # Download the file from `url` and save it locally under `file_name`:
        with tempfile.NamedTemporaryFile(prefix="tle_", suffix=".zip") as tle_temp:
            print("\tDownloading: {} -> {}".format(url, tle_temp.name))
            urllib.request.urlretrieve(url, tle_temp.name)

            print("\tProcessing: {}".format(tle_temp.name))
            rows_before = raw_tle.nrows
            tle_iter = read_tles_from_zip(tle_temp.name)
            read_to_table(raw_tle, tle_iter, limit=args.limit)
            print("\t\tAdded {} rows".format(raw_tle.nrows - rows_before))
    
    print("Step 2/3 - Clipping to AIS timeframes")

    # AIS Valid date ranges are:
    #2009 2008-12-31 23:58:59 2009-02-01 00:00:00
    #2010 2009-12-29 17:05:00 2010-02-01 01:11:00
    #2011 2010-12-31 23:58:59 2011-01-31 23:58:59
    #2012 2012-01-04 15:59:48 2012-02-01 00:00:03
    #2013 2012-12-31 23:59:58 2013-02-01 00:00:04
    #2014 2013-12-31 23:57:43 2014-02-01 00:00:05
    #2015 2015-01-01 00:00:02 2015-01-31 23:59:59
    #2016 2016-01-01 00:00:01 2016-01-31 23:59:59
    #2017 2017-01-01 00:00:00 2017-01-31 23:59:58

    reduced_tle = h5file.create_table(h5file.root, 'tle_reduced', TLE, "TLE data reduced to match AIS time windows")

    tle_extra = timedelta(weeks=2)
    # We are going to assume we only need TLE's from Dec15 to Feb15
    for year in range(2009, 2018):
        start_dt = datetime(year, 1, 1) - tle_extra
        end_dt = datetime(year, 2, 1) + tle_extra
        condition = "(epoch>={}) & (epoch<={})".format(start_dt.timestamp(), end_dt.timestamp())
        appended = raw_tle.append_where(reduced_tle, condition=condition)
        print("\tYear {}: records: {}".format(year, appended))

    print("Step 3/3 - Creating final sorted index")
    # Create a full index, so the copy operation can sort inline
    reduced_tle.cols.epoch.create_index(kind="full")
    # Create a copy that is CSI on epoch, and also indexed on id
    tle_sorted = reduced_tle.copy(h5file.root, "tle_sorted", sortby="epoch")

    tle_sorted.cols.epoch.create_index(kind="full")
    tle_sorted.cols.norad_id.create_index(kind="full")

    h5file.close()
    print("NOTE: This output file is much larger than needed. Running `ptrepack` will save you some disk-space:")
    print("ptrepack --propindexes " + args.output + ":/tle_sorted" +" repacked.h5" )
