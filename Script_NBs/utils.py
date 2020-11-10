import pandas as pd
import numpy as np
import zarr
import os
import re
import glob
import json
import yaml
from matplotlib import pyplot as plt
from matplotlib import rcParams
from astropy.time import Time

# matplotlib para config
rcParams["text.usetex"] = False
rcParams["font.size"] = 15
rcParams["axes.titlepad"] = 10


def init(data_dir=None):
    """Must be called first to specify paths to data

    Args:
        data_dir(str): Path to the diretory hosting the training data.
    """
    # initiate global variables
    global LC_path, LC_zarr, cat_path, train_cat, meta_data, valid_IDs

    # if on sciserver, nothing is passed, then assign path to default
    if data_dir == None:
        data_dir = (
            "/home/idies/workspace/Temporary/ywx649999311/LSST_AGN/Class_Training/Data/"
        )
    
    LC_path = os.path.join(data_dir, "LCs.zarr.zip")
    LC_zarr = zarr.load(LC_path)
    cat_path = os.path.join(data_dir, "AllMasters.parquet")
    meta_data = yaml.safe_load(open(os.path.join(data_dir, "meta.yaml")))
    
    # get train_df and assign to global variable
    train_cat = _get_train_cat()
    valid_IDs = _get_valid_ids()


def _get_valid_ids():
    """Private: Return valide IDs."""
    return train_cat[["train_id", "class"]]


def valid_ids():
    """Return a dataframe of valid IDs together with associated object type."""
    return valid_IDs


def get_classes():
    """Return the classes of objects included in the training set."""
    return meta_data["classes"]


def train2sdss(train_id):
    """Convert from train_id to SDSS objID in run-rerun-camcol-field-obj format"""
    if train_id in train_cat.train_id.values:
        return train_cat[train_cat.train_id == train_id].sdss_objid.values[0]
    else:
        print("Warning: Provided train_id not in training data!")


def sdss2train(objid):
    """Convert from SDSS objID in run-rerun-camcol-field-obj format to train_id"""
    if objid in train_cat.sdss_objid.values:
        return train_cat[train_cat.objid == objid].train_id.values[0]
    else:
        print("Warning: Provided SDSS objID not in training data!")


def get_cat(class_label):
    """Return master catalog given a class label.

    Args:
        class_label (str): Claess label, e.g., s82Qso. 
    """
    assert class_label in meta_data["classes"], "Class not in database!"
    return train_cat[train_cat["class"] == class_label].copy()


def get_qso_cat():
    """Function to retrieve QSO master catalog."""
    return pd.concat([get_cat("s82Qso"), get_cat("highZQso")], ignore_index=True)


def get_var_cat():
    """Function to retrieve non-AGN variables master catalog."""
    return get_cat("s82vStar")


def get_gal_cat():
    """Function to retrieve non-AGN variables master catalog."""

    return get_cat("s82Gal")


def get_train_cat():
    """Return the master catalog of all sources."""
    return train_cat


def _get_train_cat():
    """Load all master catalog from disk."""

    global cat_path, meta_data

    train_int_cols = meta_data["int_cols"]
    train_df = pd.read_parquet(cat_path)
    train_df[train_int_cols] = train_df[train_int_cols].astype("Int64")

    return train_df


def _get_cat_meta():
    """Return column info for the master catalog. """
    return meta_data["master_col_def"]


def qso_cat_meta():
    """Function to display column info for the QSO master catalog"""
    return _get_cat_meta()


def var_cat_meta():
    """Function to display column info for the variable star master catalog"""
    return _get_cat_meta()


def gal_cat_meta():
    """Function to display column info for the galaxy master catalog"""
    return _get_cat_meta()


def clip_lc(lc_df):
    """Clip outliers from LC

    Args:
        lc_df: A dataframe holding the light curve.
    """

    lc_len = lc_df.shape[0]

    for band in ["u", "g", "r", "i", "z"]:

        # three point median filter
        mag = lc_df["dered_{}".format(band)].values.copy()
        sigma = np.std(mag)
        med = mag.copy()
        med[1:-2] = [np.median(mag[i - 1 : i + 2]) for i in range(1, lc_len - 2)]

        # need to deal with edges of median filter
        med[0] = np.median([mag[-1], mag[0], mag[1]])
        med[-1] = np.median([mag[-2], mag[-1], mag[0]])

        # compute residual
        res = np.abs(mag - med)

        # set clipping thresh hold
        raise_bar = True
        thresh = 3 * sigma

        # if remove too much, raise bar until only remove 10%
        while raise_bar:
            ratio = sum(res > thresh) / lc_len
            if ratio < 0.1:
                break
            else:
                thresh += 0.1

        # replace unreliable data with -99
        lc_df["dered_{}".format(band)].values[res > thresh] = -99

    return lc_df


def get_sdss_lc(train_id, clip=True, datetime=True):
    """Function to retreive sdss light curve given the object train_id

    Args:
        train_id (int): Unique ID for an object in training sample.
        clip (bool): Indicates whether to run filter removing outliers, default to True.
        datetime (bool): Whether to add datetime column for all bands, default to True.
    
    Raises:
        Exception: If train_id is not valid.
    """

    if train_id not in valid_IDs.train_id.values:
        raise Exception("train_id provided is not valid!")

    lc_df = (
        pd.DataFrame(LC_zarr[f"sdss_lc/{train_id}"])
        .sort_values(by="mjd_u")
        .reset_index(drop=True)
    )

    # add datetime columns
    if datetime:
        for band in ["u", "g", "r", "i", "z"]:
            lc_df["datetime_{}".format(band)] = Time(
                lc_df["mjd_{}".format(band)], format="mjd"
            ).datetime

    # whether to remove outliers
    if clip:
        lc_df = clip_lc(lc_df)

    return lc_df.replace(-99.0, np.nan)


def get_sdss_qso(train_id, clip=True, datetime=True):
    """Function to retreive sdss qso light curve given the object meta info.

    Args:
        train_id (int): Unique ID for an object in training sample.
        clip (bool): Indicates whether to run filter removing outliers, default to True.
        datetime (bool): Whether to add datetime column for all bands, default to True.
    """
    # check if id in catalog
    if train_id not in valid_IDs.train_id.values:
        raise Exception("train_id provided is not valid!")

    lc = get_sdss_lc(train_id, clip, datetime)
    return lc


def get_sdss_var(train_id, clip=True, datetime=True):
    """Function to retreive sdss s82 variables light curve given the object meta info.

    Args:
        train_id (int): Unique ID for an object in training sample.
        clip (bool): Indicates whether to run filter removing outliers, default to True.
        datetime (bool): Whether to add datetime column for all bands, default to True.
    """
    if train_id not in valid_IDs.train_id.values:
        raise Exception("train_id provided is not valid!")

    lc = get_sdss_lc(train_id, clip, datetime)
    return lc


def get_sdss_gal(train_id, clip=True, datetime=True):
    """Function to retreive sdss s82 galaxy light curve given the object meta info.

    Args:
        train_id (int): Unique ID for an object in training sample.
        clip (bool): Indicates whether to run filter removing outliers, default to True.
        datetime (bool): Whether to add datetime column for all bands, default to True.
    """
    if train_id not in valid_IDs.train_id.values:
        raise Exception("train_id provided is not valid!")

    lc = get_sdss_lc(train_id, clip, datetime)
    return lc


def plot_sdss_lc(train_id, bands=["u", "g", "r", "i", "z"], clip=True):
    """Plot SDSS light curves without merging.

    Args:
        train_id (int): Unique ID for an object in training sample.
        bands (list): Optional, a list specifying light curves in which bands to plot.
        clip (bool): Optional, indicates whether to run filter removing outliers, default to True.

    Return:
        bands (list): A list specifying the band filters in which to plot the light curves.
        x (list): A list of numpy arrays of mjd for observations in each band.
        y (list): A list of numpy arrays of magnitude in each band (dered mags)
        err (list): A list of numpy arrays of magnitude errors in each band
    """

    sdss_lc = get_sdss_lc(train_id, clip, datetime=False)

    x = []
    y = []
    err = []
    mjd_temp = "mjd_{}"
    mag_temp = "dered_{}"
    err_temp = "psfmagerr_{}"

    for band in bands:
        # bad observations has been replaced with np.nan in get functions
        x.append(sdss_lc[mjd_temp.format(band)].values)
        y.append(sdss_lc[mag_temp.format(band)].values)
        err.append(sdss_lc[err_temp.format(band)].values)

    return bands, x, y, err


def plot_merged_lc(train_id, bands, how=np.nanmedian, clip=True):
    """Plot merged light curves using SDSS any number of bands.

    Args:
        train_id (int): Unique ID for an object in training sample.
        bands(list): A list specifies what bands to include to make the merged light curve
        how: Normalization method, np.nanmean or np.nanmedian, default to np.median
        clip (bool): Indicates whether to run filter removing outliers, default to True.

    Return:
        bands (list): A list specifying the band filters in which to plot the light curves.
        x (list): A list of numpy arrays of mjd for observations in each band.
        y (list): A list of numpy arrays of magnitude in each band (dered mags)
        err (list): A list of numpy arrays of magnitude errors in each band
    """

    bands, x, y, err = plot_sdss_lc(train_id, bands, clip)

    for idx, band in enumerate(bands):
        mean_mag = how(y[idx])
        y[idx] = y[idx] - mean_mag

    return bands, x, y, err


# def plot_sdss_crts(ID_sdss, sdss_band=None, how=np.median):
#     """Plot merged light curves (AGN or non-AGNs) using one SDSS band and CRTS V band.

#     Args:
#         train_id: Unique ID for an object in training sample.
#         sdss_band(char): SDSS passband (u, g, r, i, z)
#         how: Normalization method, np.mean or np.median
#     """

#     if sdss_band is None:
#         print ('Need to specify SDSS band for merging with CRTS')
#         return None

#     if ID_sdss in qso_id:
#         sdss_lc = get_sdss_qso(ID_sdss)
#         crts_lc = get_crts_qso(ID_sdss)
#     else:
#         print ('Requested object not in catalog!')
#         return None

#     # create fig
#     fig = plt.figure(figsize=(12,8))

#     # matplotlib para config
#     rcParams['text.usetex'] = False
#     rcParams['font.size'] = 15

#     # plot sdss lc
#     mjd_temp = 'mjd_{}'
#     mag_temp = '{}'
#     err_temp = '{}_err'

#     # bad observations has mag of -99
#     mag = sdss_lc[mag_temp.format(sdss_band)]
#     mjd = sdss_lc[mjd_temp.format(sdss_band)][mag > 0]
#     err = sdss_lc[err_temp.format(sdss_band)][mag > 0]
#     mag = mag[mag > 0]
#     mag = mag - how(mag) # subtract median or mean
#     plt.errorbar(mjd, mag, err, fmt='.', label='sdss {} band'.format(sdss_band))

#     if len(crts_lc) == 0:
#         pass
#     else:
#         mag = crts_lc['mag']
#         mag = mag - how(mag) # subtract median or mean
#         mjd = crts_lc['mjd']
#         err = crts_lc['magErr']
#         plt.errorbar(mjd, mag, err, fmt='.', label='CRTS')

#     plt.title('Merged (Normalized) Light curve for object {} in SDSS {} band and CRTS V band'.format(ID_sdss, sdss_band))
#     plt.xlabel('MJD')
#     plt.ylabel('Magnitude')
#     plt.legend()
