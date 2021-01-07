# Install gnu-parallel
conda config --add channels conda-forge
conda install parallel

# Run the parallel index build
parallel -a norad_id_active.txt python sathelpers.py --noradID {}