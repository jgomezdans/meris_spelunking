#!/bin/bash
# A script to create some VRT files from the Brockmann data
# 
#   Requires gdalbuildvrt!!!
#
# J Gomez-Dans ( UCL & NCEO)

echo The Brockmannator
echo J Gomez-Dans (UCL \& NCEO )
echo
echo Making useful stuff out of NetCDF files
the_dir=$1
cd ${the_dir}
# Remove empty directories, makes things easier
find . -empty -type d -delete

# Define the layers
layers=ndvi sdr_1 sdr_10 sdr_12 sdr_13 sdr_14 sdr_2 sdr_3 sdr_4 sdr_5 sdr_6 sdr_7 sdr_8 sdr_9 sdr_error_1 sdr_error_10 sdr_error_12 sdr_error_13 sdr_error_14 sdr_error_2 sdr_error_3 sdr_error_4 sdr_error_5 sdr_error_6 sdr_error_7 sdr_error_8 sdr_error_9 status sun_azimuth sun_zenith view_azimuth view_zenith

# Loop over all NetCDF files and put the different layers
# in suitably named text files with the full GDAL-specified path

for fich in `find . -type f -iname "*nc"`
do 
    for layer in ${layers}
    do
           echo HDF5:'"'`pwd`/${fich}'"'://${layer} >> /tmp/${layer}.txt
    done
done

# Create the VRT files
for layer in ${layers}
do
    gdalbuildvrt -separate -input_file_list /tmp/${layer}.txt MERIS_2008_${layer}.vrt
done
# Clean up

for layer in ${layers}
do
    \rm -rf /tmp/${layer}.txt
done

