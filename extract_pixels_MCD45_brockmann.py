#!/usr/bin/env python
"""
A script to extract time series of MERIS BRDF data to a compressed tarball.
Requires a number of things:

* a MCD45/MCD64 GDAL-readable dataset with the same projection & size as the MERIS data
* MERIS data in VRT format
* a doy file for meris data, indicating what DoY is associated with each band in the stack

"""
import os
import logging
from StringIO import StringIO
import tarfile

import gdal
import numpy as np

__author__ = "J Gomez-Dans (NCEO&UCL)"
__copyright__ = "(c) 2013"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "J Gomez-Dans"
__email__ = "j.gomez-dans@ucl.ac.uk"
__status__ = "Development"

def do_command_line ():
    import argparse
    
    parser = argparse.ArgumentParser( description= ("Extract MERIS data\n" + \
        "By %s" % __author__) )
    parser.add_argument ('-b', '--burn', action="store", \
            type=str, help="The reprojected & warped MCD45 or MCD64 file", \
             dest="burn_file" )
    parser.add_argument ('-m', '--dob_min', action="store", \
            type=int, help="Minimum day of burn to consider", \
             dest="dob_min" )
    parser.add_argument ('-M', '--dob_max', action="store", \
            type=int, help="Maximum day of burn to consider", \
             dest="dob_max" )
    parser.add_argument ('-d', '--directory', action="store", \
            type=str, help="Directory where VRT files are stored", \
             dest="directory" )
    parser.add_argument ('-o', '--output', action="store", \
            type=str, help="Directory where output tarball will be stored", \
             dest="output" )
    
    parser.add_argument ('-D', '--doy_file', action="store", \
            type=str, help="File with DoY information (typically doys_bands.txt)", \
             dest="doy_file" )
    
    parser.add_argument ('-N', '--n_pxls', action="store", default=5000,\
            type=int, help="# of pixels to extract (Default 5000)", \
             dest="n_pixels" )
    
    
    
    args = vars(parser.parse_args())
    return ( args['burn_file'], args['dob_min'], args['dob_max'], args['directory'], \
            args['output'], args['doy_file'], args['n_pixels'])

def test_files ( burn_file, dob_min, dob_max, directory, output_dir, doy_file ):
    if os.path.exists ( burn_file ):
        g = gdal.Open ( burn_file )
        if g is None:
            logging.error ( "burn file %s is incorrect & cannot be read by GDAL!" % burn_file )
            raise IOError, "burn file %s is incorrect & cannot be read by GDAL!" % burn_file
    else:
        logging.error ( "burn file %s is not present on file system!" % burn_file )
        raise IOError, "burn file %s is not present on file system!" % burn_file
    
    if dob_min > dob_max:
        logging.error ( "dob_min (%d) MUST be less or equal to dob_max (%d)!" % ( dob_min, dob_max ) )
        raise ValueError, "dob_min (%d) MUST be less or equal to dob_max (%d)!" % ( dob_min, dob_max )
    if not os.path.exists ( doy_file ):
        logging.error (  "The doy file %s does not exist" % doy_file )
        raise IOError, "The doy file %s does not exist" % doy_file
    
    bands = [ "MERIS_2008_sdr_%d.vrt"%i \
            for i in [ 1,2,3,4,5,6,7,8,9,10,12,13,14] ]
    bands_u = [ "MERIS_2008_sdr_error_%d.vrt"%i \
            for i in [ 1,2,3,4,5,6,7,8,9,10,12,13,14] ]
    all_files = [ "MERIS_2008_sun_azimuth.vrt", \
            "MERIS_2008_sun_zenith.vrt", "MERIS_2008_view_azimuth.vrt", \
            "MERIS_2008_view_zenith.vrt", "MERIS_2008_status.vrt" ] + \
             bands + bands_u 
    for fich in all_files:
        fname = os.path.join ( directory, fich )
        if os.path.exists ( fname ):
            g = gdal.Open ( fname )
            if g is None:
                logging.error ( "VRT file %s is corrupt!" % fname )
                raise IOError, "VRT file %s is corrupt!" % fname
        else:
            logging.error ("VRT file %s does not exist!" % fname)
            raise IOError, "VRT file %s does not exist!" % fname
    logging.info ( "Command-line options appear to be sensible...")    
    return True
            
            



def extract_pixels ( burn_file, dob_min, dob_max, directory, output_dir, doy_file, n_pixels=5000 ):
    logging.info ( "Reading burns file %s" % burn_file )
    g = gdal.Open( burn_file )
    mcd45 = g.ReadAsArray()
    logging.info ( "Done!")
    mask = np.logical_and ( mcd45 >= dob_min, mcd45 <= dob_max )
    logging.info ("Masking...")
    
    bands = [ "MERIS_2008_sdr_%d.vrt"%i \
            for i in [ 1,2,3,4,5,6,7,8,9,10,12,13,14] ]
    bands_u = [ "MERIS_2008_sdr_error_%d.vrt"%i \
            for i in [ 1,2,3,4,5,6,7,8,9,10,12,13,14] ]
    all_files = [ "MERIS_2008_sun_azimuth.vrt", \
            "MERIS_2008_sun_zenith.vrt", "MERIS_2008_view_azimuth.vrt", \
            "MERIS_2008_view_zenith.vrt", "MERIS_2008_status.vrt" ] + \
             bands + bands_u 
    oot = {}
    for fich in all_files:
        fname = os.path.join ( directory, fich )
        logging.info ( "Reading layers stored in %s" % fname )
        g = gdal.Open ( fname )
        
        a = g.ReadAsArray()
    #    buf = g.ReadRaster(this_X, this_Y, nx_valid, ny_valid, \
    #                buf_xsize=nx_valid, buf_ysize=ny_valid,  \
    #               band_list= the_bands )
    #
    #    a = np.frombuffer(buf, dtype=np.int16).reshape(( len(the_bands), ny_valid, nx_valid))
        oot[fich] = a[:, mask ]
    ( ry, rx ) = np.nonzero ( mask )
    i = np.arange(mask.sum())
    np.random.shuffle ( i )
    isx = i[ :n_pixels ]
    the_doys = np.loadtxt( doy_file )
    output_order = all_files # all_files[17:21] + all_files[21:] + all_files[:17]
    output_mult= [ 1. for x in all_files ]
    logging.info ("All data read & pre-processed")


    tarfile_out = tarfile.open (os.path.join ( output_dir, "BRDF_MERIS_files.tar.gz"), 'w:gz' )
    logging.info ("Saving output to %s" % os.path.join ( output_dir, "BRDF_MERIS_files.tar.gz"))
    for aquel,este in enumerate(isx):
        DoB = mcd45[mask][este]
        this_i, this_j = ry[este], rx[este]
        X = np.c_[[oot[k][:,este]*output_mult[j] \
                for j, k in enumerate(output_order)] ]
        XX = np.c_[the_doys, X.T]
        s = StringIO()
        #np.savetxt ('txtfiles/MERIS_BRDF_Angola_2008_DoB_%03d.dat' % DoB, XX, delimiter="\t" )


        np.savetxt( s, XX, delimiter="\t" )
        s.seek(0)
        
        tarinfo = tarfile.TarInfo('MERIS_BRDF_Angola_2008_DoB_%03d_ry%04d_rx%04d.dat' % ( DoB, this_i, this_j ) )
        tarinfo.size = s.len 
        tarfile_out.addfile ( tarinfo, s )
        logging.info( "Added file %d/5000 (%s)" % ( aquel, 'MERIS_BRDF_Angola_2008_DoB_%03d_ry%04d_rx%04d.dat' % ( DoB, this_i, this_j ) ) )
    tarfile_out.close()
    logging.info ("All quite on the western front")

if __name__ == "__main__":
    
    logging.basicConfig ( filename='MERIS_extract_brdf.log', \
        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', \
        filemode='w', level=logging.DEBUG )

    burn_file, dob_min, dob_max, directory, output_dir, doy_file, n_pixels = do_command_line()
    test_files ( burn_file, dob_min, dob_max, directory, output_dir, doy_file )
    extract_pixels ( burn_file, dob_min, dob_max, directory, output_dir, doy_file, n_pixels=n_pixels )
