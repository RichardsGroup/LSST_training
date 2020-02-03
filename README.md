# LSST AGN Classification Training Set
Here we present the training set that is being constructed at Drexel University. This repository hosts the scripts needed to access the training data and some notebooks demonstrating how to explore the training set. We primarily hosting the training data on SciServer, which DO requires an account. Thus, the purpose of putting the scripts and notebooks on GitHub as well is to make it easier for folks to play with our training data offline.

Regarding SciServer, we are aware that it is NOT identical to the future LSST Science Platform, but we think that SciServer is a good place to share data and code among the AGN SC to encourage collaborations at this moment, plus SciServer provides free computing resource and also adopts Jupyter environment. Please do not hesitate to suggest alternative solutions.

The training data (both catalog and light curves) are stored in zarr files, which stores data in chunks and thus enables parallel read/write. There are many good features of zarr to mention, and using zarr as the backend storage is only an experiment to enable faster data I/O. To minimize the learning curve, I wrote some functions to easily explore and access the catalog and light curves.

### Get Started
To start playing with our training set, please begin with the notebook [Get_started.ipynb](./Script_NBs/Get_started.ipynb).

### The Training Set
The training set consists of two catalogs, a quasar catalog (~25k sources) and a non-AGN variables catalog (~25k sources), and the associated light curves. All quasars have spectroscopic confirmations (from SDSS I/II, BOSS and eBOSS), but not every source in the non-AGN catalog is guaranteed to be non-AGN (needs spectroscopic confirmation). The non-AGN variables catalog is constructed by remove sources that have been confirmed to be AGNs from the SDSS DR7 variables catalog ([Ivezic et al. 2007](http://faculty.washington.edu/ivezic/sdss/catalogs/S82variables.html)). Below we list the tasks that we have completed and those that we have planned to work on. 



#### Finished:
- Compliled a catalog of quasars and a catalog of non-AGN (not 100% pure) variables using SDSS DR7 and DR14
- Collected SDSS light curves for objects found above (SDSS photometry + DCR)
- Merged in available SpIES (~90 degree^2) MIR detections for objects in the QSO and non-AGN variables catalogs
- Merged in Gaia DR2 proper motion measurement for for objects in the QSO and non-AGN variables catalogs
- Write functions to perform simple light curve merging (gri)

#### To do:
- [ ] Clean up the non-AGN sample (remove contaminated AGNs if possible)
- [ ] Fit DHO model to merged light curves (crts + other surveys)
- [x] Get colors (best-fit mags) for all sources in the two catalogs using casjob
- [ ] Get corresponding CRTS light curves (DR3) for all sources
