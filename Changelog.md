## 2020-10-26
### Data Updates
- Added high redshift QSOs provided by Feige Wang.
- Cross-matched with UKIDSS Y, J, H, K photometry, data provided by Matthew Temple.
- Added `s82LSST` column in the master catalog to indicate whether a source is in the extended 'Stripe 82' area defined in the [Data_Stat.md](./Data_Stat.md).
- Added `s82SDSS` column in the master catalog to indicate whether a source is in the original SDSS 'Stripe 82' region.

### API Updates
- Now, all master catalog are in one file. The same for all light curves.
- Added `meta.yaml` to store meta data
- Since master catalog are in one big table. `qso_cat_meta()`, `vstar_cat_meta()` and `gal_cat_meta()` will return the same information. 
- Since there are more than just qso and variable stars in the training set, it will be recommended to use filter the big master catalog to get the desired class of data (or the `get_cat()` function with the class name as the only argument), instead of using `get_qso_cat()`, `get_vstar_cat()` and `get_gal_cat()`. However, they will still work for backward compatibility. 
- Added `get_classes()` function to return unique source classes (e.g., s82Qso). 
- `get_qso_cat()` will now return both `s82Qso` and `highZQso` sources. To get just SDSS DR16 sources, use `get_cat('s82Qso')`.