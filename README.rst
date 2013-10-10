=================
MERIS spelunking
=================

:Info: Some scripts for extracing and playing around with MERIS data
:Author: J Gomez-Dans <j.gomez-dans@ucl.ac.uk>
:Date: 10.10.2013
:Description: README file

Creating the Virtual datasets
================================

Rather than using the NetCDF files as they are, we will produce what are called 
*virtual datasets* (i.e., file pointers to the individual data layers). That is
a convenient form of working with and accessing stacks of data conveniently. The
Virtual format is a GDAL-only format, but if you need the data in e.g. GeoTIFF, 
you can use ``gdal_convert`` to convert it to whatever format you like.

The creation of the VRT files is simple, and it just assumes that the NetCDF files
are all under a directory, and that in that directory (or directories below), only
files related to a single tile are stored. The command is as follows:

    create_vrt_brockmann.sh <top_level_directory>
    
This will create a number of different VRT files in the directory specified in
``<top_level_directory>``. You can check the files by using ``gdalinfo --stats``
on one or two of them (this will take a while).

You will also need to create a ``doys_bands.txt`` file, a file that has two columns
and as many rows as layers are in the VRTs. Each row contains the year and DoY of
that particular layer.

Extracting the data
====================

Once the VRT files have been put together, you can extract times series of BRF 
for individual pixels using the script ``extract_pixels_MCD45_brockmann.py``.
The script requires a number of options, that you can list with

    extract_pixels_MCD45_brockmann.py --help
    
Here's a simple example that is working now:

     ./extract_pixels_MCD45_brockmann.py \
     -b /data/netapp_4/ucfajlg/MERIS/SS05_Angola_Brockmann/h19v10/2008/MCD64A1/MCD64A1.A2008214.h19v10.005.2009044220220.tif \
     -m 214 -M 243 -d /data/netapp_4/ucfajlg/MERIS/SS05_Angola_Brockmann/h19v10/2008/ -o . \
     -D /data/netapp_4/ucfajlg/MERIS/SS05_Angola_Brockmann/h19v10/2008/doys_bands.txt -N 10000
     
where the options are:

``-b <filename>``

    This is the complete path to the MCD45 or MCD64 file, already reprojected and made to match the MERIS tile.
    
``-m <doy_min>``

    The minimum Day of Burn to be considered

``-M <doy_min>``

    The maximum Day of Burn to be considered

``-d <data_dir>``

    The working directory, where all VRT files are
    
``-o <output_dir>``

    Where the ``tar.gz`` file will be created
    
``-D doys_bands``

    Where the bands doys file is stored.
    
``-N <num_pixels>``

    The number of timeseries with fires to extract
    
This command produces a log in a file called ``MERIS_extract_brdf.log``. Check that file for more information if anything works,
or indeed, if it doesn't!

    

