import pandas as pd
import numpy as np
import zarr
import os
import re
from matplotlib import pyplot as plt
from matplotlib import rcParams
from astropy.time import Time

# matplotlib para config
rcParams['text.usetex'] = False
rcParams['font.size'] = 15
rcParams['axes.titlepad'] = 10


def init(qsoP=None, varP=None):
    """Must be called first to specify paths to data

    Args:
        qsoP(str): Path to the QSO training set.
        varP(str): Path to the variable stars training set.
    """

    # initiate global variables
    global qso_id, var_id, df_var_ivz, qso_path, var_path
    global qso_cat, var_cat, train_cat

    # if on sciserver, nothing is passed, then assign path to default
    if qsoP is None:
        qso_path = '/home/idies/workspace/Storage/ywx649999311/AGN_training/Data/qsoV5.zarr.zip'
    else:
        qso_path = qsoP

    if varP is None:
        var_path = '/home/idies/workspace/Storage/ywx649999311/AGN_training/Data/vStarV5.zarr.zip'
    else:
        var_path = varP

    qso_id = zarr.load(qso_path)['catalog']['train_id']
    var_id = zarr.load(var_path)['catalog']['train_id']
    df_var_ivz = pd.DataFrame(
        zarr.load(var_path)['catalog'][['train_id', 'ivz_id']])

    # import catalog to pandas df + made ID types, replace -99 with nan
    qso_cat = pd.DataFrame(zarr.load(qso_path)['catalog'])
    var_cat = pd.DataFrame(zarr.load(var_path)['catalog'])

    r = re.compile('.*(id|ID)')  # regex match to find id columns
    qso_int_cols = list(filter(r.match, qso_cat.columns))
    var_int_cols = list(filter(r.match, var_cat.columns))
    qso_int_cols.extend('lcN')
    var_int_cols.extend('lcN')
    qso_cat[qso_int_cols] = qso_cat[qso_int_cols].astype(
        'Int64').replace(-99, np.nan)
    var_cat[var_int_cols] = var_cat[var_int_cols].astype(
        'Int64').replace(-99, np.nan)

    # get train_df and assign to global variable
    train_cat = _get_train_cat()

# def load_x_id():
#     """Load crts cross_id data to a dataframe. """

#     # load cross_id zarr group and get array keys
#     x_id = zarr.open(qso_path+'/cross_id')
#     keys = list(x_id.keys())


#     # get column name for cross_ids
#     cols = []
#     for key in keys:
#         cols.append(x_id[key].attrs['col_name'])

#     return pd.DataFrame({cols[0]:np.array(x_id[keys[0]]), cols[1]:x_id[keys[1]]})

# call load_x_id to load info to match ID_sdss with crts_id
# x_df = load_x_id()

def valid_ids():
    """Return a dataframe of valid IDs together with associated object type."""

    qso_df = pd.DataFrame({'train_id': qso_id, 'Type': 'AGN'})
    var_df = pd.DataFrame({'train_id': var_id, 'Type': 'non-AGN'})

    return pd.concat([qso_df, var_df], ignore_index=True)

# def crts_qso_ids():
#     """Return a dataframe of QSO IDs (and crts_id) for objects having CRTS light curves"""

#     crts_qso = x_df[~(x_df.crts_id == '-999')].copy().reset_index(drop=True)

#     return crts_qso


def train2sdss(train_id):
    """Convert from train_id to SDSS objID in run-rerun-camcol-field-obj format"""

    if train_id in train_cat.train_id.values:
        return train_cat[train_cat.train_id == train_id].objid.values[0]
    else:
        print('Warning: Provided train_id not in training data!')


def sdss2train(objid):
    """Convert from SDSS objID in run-rerun-camcol-field-obj format to train_id"""

    if objid in train_cat.objid.values:
        return train_cat[train_cat.objid == objid].train_id.values[0]
    else:
        print('Warning: Provided SDSS objID not in training data!')


def get_qso_cat():
    """Function to retrieve QSO master catalog."""

    return qso_cat


def get_var_cat():
    """Function to retrieve non-AGN variables master catalog."""

    return var_cat


def get_train_cat():
    """combine the result of get_qso_cat() and get_var_cat()"""

    return train_cat


def _get_train_cat():
    """Private function: combine the result of get_qso_cat() and get_var_cat()."""

    qso_cat['qlabel'] = 1
    var_cat['qlabel'] = 0

    train_df = pd.concat([qso_cat, var_cat],
                         sort='train_id', ignore_index=True)
    r = re.compile('.*(id|ID)')  # regex match to find id columns
    train_int_cols = list(filter(r.match, train_df.columns))
    train_int_cols.extend(['lcN', 'spec'])
    train_df[train_int_cols] = train_df[train_int_cols].astype('Int64')

    return train_df


def qso_cat_meta():
    """Function to display column info for the master catalog"""

    root = zarr.open(qso_path, mode='r')['catalog']
    return root.attrs.asdict().copy()


def var_cat_meta():
    """Function to display column info for the master catalog"""

    root = zarr.open(var_path, mode='r')['catalog']
    return root.attrs.asdict().copy()


def clip_lc(lc_df):
    '''Clip outliers from LC

    Args:
        lc_df: A dataframe holding the light curve.
    '''

    lc_len = lc_df.shape[0]

    for band in ['u', 'g', 'r', 'i', 'z']:

        # three point median filter
        mag = lc_df['dered_{}'.format(band)].values.copy()
        sigma = np.std(mag)
        med = mag.copy()
        med[1:-2] = [np.median(mag[i-1:i+2]) for i in range(1, lc_len-2)]

        # need to deal with edges of median filter
        med[0] = np.median([mag[-1], mag[0], mag[1]])
        med[-1] = np.median([mag[-2], mag[-1], mag[0]])

        # compute residual
        res = np.abs(mag - med)

        # set clipping thresh hold
        raise_bar = True
        thresh = 3*sigma

        # if remove too much, raise bar until only remove 10%
        while raise_bar:
            ratio = sum(res > thresh)/lc_len
            if ratio < 0.1:
                break
            else:
                thresh += 0.1

        # replace unreliable data with -99
        lc_df['dered_{}'.format(band)].values[res > thresh] = -99

    return lc_df


def get_sdss_qso(train_id, clip=True, datetime=True):
    """Function to retreive sdss qso light curve given the object meta info. Add unred mags.

    Args:
        train_id (int): Unique ID for an object in training sample.
        clip (bool): Indicates whether to run filter removing outliers, default to True.
        datetime (bool): Whether to add datetime column for all bands, default to True.
    """

    # check if id in catalog
    if train_id not in qso_id:
        raise Exception('train_id provided is not valid!')

    # get the catalog row for queried object
    cat_row = qso_cat[qso_cat.train_id == train_id]

    # read from zarr
    lc_df = pd.DataFrame(zarr.load(qso_path)['sdss_lc/{}'.format(train_id)]
                         ).sort_values(by='mjd_u').reset_index(drop=True)

    # add datetime columns
    if datetime:
        for band in ['u', 'g', 'r', 'i', 'z']:

            lc_df['datetime_{}'.format(band)] = Time(lc_df['mjd_{}'.format(band)],
                                                     format='mjd').datetime

    # whether to remove outliers
    if clip:
        lc_df = clip_lc(lc_df)

    return lc_df.replace(-99.0, np.nan)


# def get_crts_qso(ID_sdss):
#     """Function to retreive crts qso light curve given the object meta info. Returns None if not matching light curve.

#     Args:
#         train_id: Unique ID for an object in training sample.
#     """
#     if train_id not in qso_id:
#         raise Exception('train_id provided is not valid!')

#     crts_id = x_df[x_df.train_id == train_id].crts_id.values[0]

#     if (crts_id == '-999'):
#         print ('Not CRTS light curve available!')
#         return pd.DataFrame()
#     else:
#         path = os.path.join(qso_path, 'crts_lc/{}'.format(crts_id))
#         return pd.DataFrame(zarr.load(path))


def get_sdss_var(train_id, clip=True, datetime=True):
    """Function to retreive sdss s82 variables light curve given the object meta info.

    Args:
        train_id (int): Unique ID for an object in training sample.
        clip (bool): Indicates whether to run filter removing outliers, default to True.
        datetime (bool): Whether to add datetime column for all bands, default to True.
    """

    if train_id not in var_id:
        raise Exception('train_id provided is not valid!')

    # get the catalog row for queried object
    cat_row = var_cat[var_cat.train_id == train_id]

    # sort by mjd
    lc_df = pd.DataFrame(zarr.load(var_path)['sdss_lc/{}'.format(train_id)]
                         ).sort_values(by='mjd_u').reset_index(drop=True)

    # add datetime columns
    if datetime:
        for band in ['u', 'g', 'r', 'i', 'z']:

            lc_df['datetime_{}'.format(band)] = Time(lc_df['mjd_{}'.format(band)],
                                                     format='mjd').datetime

    # whether to mask outliers
    if clip:
        lc_df = clip_lc(lc_df)

    return lc_df.replace(-99.0, np.nan)


# def plot_qso(train_id):
#     """Plot all available quasar light curves without merging.

#     Args:
#         train_id: Unique ID for an object in training sample.
#     """

#     sdss_lc = get_sdss_qso(train_id)
#     crts_lc = get_crts_qso(ID_sdss)

#     # create fig
#     fig = plt.figure(figsize=(12,8))

#     # matplotlib para config
#     rcParams['text.usetex'] = False
#     rcParams['font.size'] = 15

#     # plot sdss lc
#     bands = ['u', 'g', 'r', 'i', 'z']
#     mjd_temp = 'mjd_{}'
#     mag_temp = '{}'
#     err_temp = '{}_err'

#     for band in bands:
#         # bad observations has mag of -99
#         mag = sdss_lc[mag_temp.format(band)]
#         mjd = sdss_lc[mjd_temp.format(band)][mag > 0]
#         err = sdss_lc[err_temp.format(band)][mag > 0]
#         mag = mag[mag > 0]

#         plt.errorbar(mjd, mag, err, fmt='.', label='sdss {} band'.format(band))

#     if len(crts_lc) == 0:
#         pass
#     else:
#         mag = crts_lc['mag']
#         mjd = crts_lc['mjd']
#         err = crts_lc['magErr']
#         plt.errorbar(mjd, mag, err, fmt='.', label='CRTS')

#     plt.title('Light curve for object {}'.format(ID_sdss))
#     plt.xlabel('MJD')
#     plt.ylabel('Magnitude')
#     plt.legend()


def plot_sdss_qso(train_id, bands=['u', 'g', 'r', 'i', 'z'], clip=True):
    """Plot SDSS quasar light curves without merging.

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

    sdss_lc = get_sdss_qso(train_id, clip)
    x = []
    y = []
    err = []
    mjd_temp = 'mjd_{}'
    mag_temp = 'dered_{}'
    err_temp = 'psfmagerr_{}'

    for band in bands:
        # bad observations has been replaced with np.nan in get functions
        x.append(sdss_lc[mjd_temp.format(band)].values)
        y.append(sdss_lc[mag_temp.format(band)].values)
        err.append(sdss_lc[err_temp.format(band)].values)

    return bands, x, y, err


def plot_var(train_id, bands=['u', 'g', 'r', 'i', 'z'], clip=True):
    """Plot SDSS non-AGN varialbes light curves without merging.

    Args:
        train_id (int): Unique ID for an object in training sample.
        bands (list): A list specifying light curves in which bands to plot.
        clip (bool): Indicates whether to run filter removing outliers, default to True.

    Return:
        bands (list): A list specifying the band filters in which to plot the light curves.
        x (list): A list of numpy arrays of mjd for observations in each band.
        y (list): A list of numpy arrays of magnitude in each band (dered mags)
        err (list): A list of numpy arrays of magnitude errors in each band
    """

    sdss_lc = get_sdss_var(train_id, clip)
    x = []
    y = []
    err = []
    mjd_temp = 'mjd_{}'
    mag_temp = 'dered_{}'
    err_temp = 'psfmagerr_{}'

    for band in bands:
        # bad observations has been replaced with np.nan in get functions
        x.append(sdss_lc[mjd_temp.format(band)].values)
        y.append(sdss_lc[mag_temp.format(band)].values)
        err.append(sdss_lc[err_temp.format(band)].values)

    return bands, x, y, err


def plot_merge_gri(train_id, how=np.nanmedian, clip=True):
    """Plot merged light curves (AGN or non-AGNs) using SDSS g, r, i bands.

    Args:
        train_id (int): Unique ID for an object in training sample.
        how: Normalization method, np.nanmean or np.nanmedian, default to np.median
        clip (bool): Indicates whether to run filter removing outliers, default to True.

    Return:
        bands (list): A list specifying the band filters in which to plot the light curves.
        x (list): A list of numpy arrays of mjd for observations in each band.
        y (list): A list of numpy arrays of magnitude in each band (dered mags)
        err (list): A list of numpy arrays of magnitude errors in each band
    """

    if train_id in qso_id:
        sdss_lc = get_sdss_qso(train_id, clip=clip)
    elif train_id in var_id:
        sdss_lc = get_sdss_var(train_id, clip=clip)
    else:
        print('Requested object not in catalog!')
        return None

    bands = ['g', 'r', 'i']
    x = []
    y = []
    err = []
    mjd_temp = 'mjd_{}'
    mag_temp = 'dered_{}'
    err_temp = 'psfmagerr_{}'

    for band in bands:
        # bad observations has been replaced with np.nan in get functions
        mean_mag = how(sdss_lc[mag_temp.format(band)].values)
        x.append(sdss_lc[mjd_temp.format(band)].values)
        y.append(sdss_lc[mag_temp.format(band)].values - mean_mag)
        err.append(sdss_lc[err_temp.format(band)].values)

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
