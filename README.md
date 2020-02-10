# LSST AGN Classification Training Set

Here we present the training set that is being constructed at Drexel
University. This repository hosts the scripts needed to access the
training data and some notebooks demonstrating how to explore the
training set. This repository is public; however, we are primarily hosting the training data on SciServer.org,
which DOES require an account. Putting the scripts
and notebooks on GitHub is to make it easier for others to play
with our training data offline.

Regarding SciServer.org, we are aware that it is NOT identical to the
future LSST Science Platform, but we think that SciServer is a good
place to share data and code among the LSST AGN Science Collaboration.
In addition, SciServer provides free computing resource and also
supports the Jupyter environment. Please do not hesitate to suggest
alternative solutions.

The training data (both static catalog data and light curves) are
stored in `zarr` files, which stores data in chunks and thus enables
parallel read/write. There are many good features of zarr to mention,
and using zarr as the backend storage is only an experiment to enable
faster data I/O. To minimize the learning curve, some functions are
provided to help explore and access the catalog and light curves.

### Setup
The first step is to create an account on SciServer, the instructions
on how to register an account on SciServer are provided in
[sciserver.pdf](Setup/sciserver.pdf). 

Next you would need to get your
computing environment ready. The instructions for setting up the
necessary compute environment are provided in
[Setup.ipynb](Setup/Setup.ipynb).

### Exploring the Training Set
Once you complete the setup process, you can start exploring our training data from the notebook [Get_started.ipynb](Script_NBs/Get_started.ipynb).

**Note:** The `utils.py` in the Script_NBs folder must be kept in the same directory as the Get_started.ipynb is in order for the convenience functions to work properly.

### The Training Set
The training set consists of two catalogs, a quasar catalog (~25k
sources) and a non-AGN variables catalog (~25k sources), and the
associated light curves. All quasars have spectroscopic confirmation
(from SDSS I/II, BOSS and eBOSS), but not every source in the non-AGN
catalog is guaranteed to be non-AGN (needs spectroscopic
confirmation). However, the non-AGN variables catalog is constructed by removing
sources that have been confirmed to be AGNs from the SDSS DR7
variables catalog ([Ivezic et
al. 2007](http://faculty.washington.edu/ivezic/sdss/catalogs/S82variables.html)). Below
we list the tasks that we have completed and those that we plan to work on.



#### Finished:
- Compiled a catalog of quasars and a catalog of non-AGN (not 100% pure) variables using SDSS DR7 and DR14
- Collected SDSS light curves for objects found above (SDSS photometry + DCR)
- Merged in available SpIES (~90 degree^2) MIR detections for objects in the QSO and non-AGN variables catalogs
- Merged in Gaia DR2 proper motion measurement for for objects in the QSO and non-AGN variables catalogs
- Wrote functions to perform simple light curve merging (gri)

#### To do:
- [ ] Clean up the non-AGN sample (remove contaminated AGNs if possible)
- [ ] Fit DHO model to merged light curves (crts + other surveys)
- [x] Get colors (best-fit mags) for all sources in the two catalogs using casjobs
- [ ] Get corresponding CRTS light curves (DR3) for all sources
