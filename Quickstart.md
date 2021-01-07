# Quickstart

Our algorithm works by precomputing a lot of satellite ephemeris.  You can run 
`scripts/sathelpers.py` to generate these yourself, or you can download precomputed satellite ephemeris in HDF5 format from our S3 bucket.

For the purposes of running our "hits" visibility solution, you will need a machine with at least 16GB of RAM and roughly 30GB of storage space. 

To run the full data pipeline as well as exercise some of the EDA tools, you will need 200GB+ of storage space, primarily because of the size of precomputed satellite ephemereis for 20k objects.

## Installation

Step 1. [Download our Data](Download_data.md)

Step 2. Download source code:

  1. Unpack the .zip file of this repo or clone `git@github.com:att-vault/vault.git`
  2. cd `vault`

Step 3. Set up Python environment

  * Download the latest Miniconda from: https://docs.conda.io/en/latest/miniconda.html
  * Install Miniconda
  * logout/re-login to pick up some environment variables

There are two ways to create the environment.

### Using Anaconda-Project

1. `conda install anaconda-project`
2. `anaconda-project run` (to launch the apps) or `anaconda-project run Viewing_AIS` (or another notebook's name) to launch that notebook.

anaconda-project will download the OSS packages needed, activate an appropriate environment, and then launch the indicated command in that environment. On a local system, a tab will then normally open in your web browser for you to use; on a remote system you can use the URL that is printed as a starting point for setting up a tunnel to your local system.

### Using conda 

1. `conda env create -n vault -f anaconda-project.yml`
2. `conda activate vault`

At this point, you can run our solutions scripts in the `scripts/` subdir, or the notebooks by invoking `jupyter notebook <notebook.ipynb>`.

## Running the code

If you downloaded the pre-computed HDF5 data, then you can run a simple validation script of the AIS HDF5 validation:

```
    $ python print_ais_file_info.py "../data/vessel data/Cleaned AIS/ais_2009.h5"
    [../data/vessel data/Cleaned AIS/ais_2009.h5]  17,977,337 data points, 1963 uniq MMSI IDs
        Latitudes: -88.89096069335938 to 87.49750518798828
        Longitutdes: -126.0 to -120.0
        Timestamps: 2008-12-31 23:58:59 to 2009-02-01 00:00:00
```

Now run the hit_finder.py script with a sample input:

```
    $ python hit_finder.py 25544 -s ../data/satellite\ data/index -a ../data/vessel\ data/Cleaned\ AIS --start "2015-01-03" --end "2015-01-08" -o output.csv
    Loaded 3,187,260 points in 0.5275993347167969 seconds
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 3187260 entries, 309064 to 3186559
    Data columns (total 4 columns):
    #   Column     Dtype
    ---  ------     -----
    0   mmsi_id    int64
    1   date_time  datetime64[ns]
    2   lat        float32
    3   lon        float32
    dtypes: datetime64[ns](1), float32(2), int64(1)
    memory usage: 97.3 MB
    None
    Time clipping truncated from 3187260 to 404803 points.
    Using 4 chunks
    compute time: 0.012053 	 extract time: 0.003789
    Found 139,673 hits in  0.047158241271972656 seconds
```

To run a Jupyter notebook to do this:
```
    $ jupyter notebook password
    $ jupyter notebook --ip=0.0.0.0 Viewing_AIS.ipynb
```

This example IPYNB loads data from CSV files.  Depending on the number of Zone files (esp Zone10), this might take a few seconds to parse.

On Cell 11, is the interesting plot to interact with. The others are just step-by-step description of how to build up this plot.

To zoom in & interact with the plot, click the "Wheel zoom" tool in the toolbar on the side of the plot.
Click-and-drag the plot in order to look around.  As you zoom in, finer-grained detail will emerge and fill in.  Depending on the size of the dataset and your machine, this might take a second.

Running through to Cell 19, we are now able to see plots of ships at different times.

## Launching web applications

Some of the .ipynb files include an expression endin gin ".servable()" in the last code cell. These notebooks are set up to be used as standalone apps that can be shared with colleagues or across systems. To launch such an app, run it with `panel serve`:

```
    $ panel serve --port 5006 Viewing_AIS.ipynb
```

If running locally, a browser tab should then open with the app.  If running that command on a remote server, you can make sure the port number that's printed is accessible (e.g. by opening an ssh tunnel), then visit the app from your local browser at the appropriate URL.
