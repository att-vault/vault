# Downloading the Data

These notebooks and scripts expect the underlying data files to be in a `data/` subdirectory of this directory, which by default is a symbolic link to `/data`.

There are two S3 buckets available.

|    |  S3 URI | size |
|----|----|----|
| [Full dataset](http://vault-data-corpus.s3-website.us-east-2.amazonaws.com/) | s3://vault-data-corpus | 66 gb |
| [Minimal dataset](http://vault-data-minimal.s3-website.us-east-2.amazonaws.com/) | s3://vault-data-minimal | 55 gb |

The minimal dataset is all that is required for us to run the "Hit Finder" solution and dashboard, as well as some visualization exploration notebooks.

The full dataset contains input data for some of the ML and ETL notebooks.

# Extracting the data

You will need to copy the files from S3 into your local machine or cloud host, putting them in `/data` if you have access to `/`, or else put the data somewhere in your writable directories and update the `./data` symlink to point to its location. E.g.:

```
> cd /data
> pip install awscli
> aws s3 sync s3://vault-data-minimal . --no-sign-request
```

Note that there are a lot of files involved and downloading is likely to take some time. Downloading to an EC2 instance is typically faster than to a home system.

