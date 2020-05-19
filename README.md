# LSST AGN Classification/Photo-z estimation Training Set

Here we present the training set that is being constructed at Drexel
University. This repository hosts the scripts needed to access the
training data and some notebooks demonstrating how to explore the
training set. This repository is public; 
however, we are primarily hosting the training data on SciServer.org,
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
Once you complete the setup process, you can start exploring our training data 
from the notebook [Getting_started.ipynb](Script_NBs/00_Getting_started.ipynb).

**NOTE:** The `utils.py` in the Script_NBs folder must be kept in the same directory 
as the Getting_started.ipynb (or any other notebooks/scripts from which you want to access 
the training data), in order for the convenience functions to work properly.

### The Training Set
The training set consists of three catalogs, a quasar catalog (~25k
sources), a non-AGN variables catalog (~25k sources) and a galaxy catalog (~110k sources), 
and the associated light curves. All quasars have spectroscopic confirmation
(from SDSS I/II, BOSS and eBOSS), but not every source in the non-AGN
catalog is guaranteed to be non-AGN (needs spectroscopic
confirmation). However, the non-AGN variables catalog is constructed by removing
sources that have been confirmed to be AGNs from the SDSS DR7
variables catalog ([Ivezic et
al. 2007](http://faculty.washington.edu/ivezic/sdss/catalogs/S82variables.html)). Below
we list the tasks that we have completed and those that we plan to work on.



#### Finished:
- Compiled a catalog of quasars, a catalog of galaxy and a catalog of non-AGN (not 100% pure) 
  variables using SDSS DR7 and DR14
- Collected SDSS light curves for objects found above (SDSS photometry + DCR)
- Merged in available SpIES (~90 degree^2) MIR detections for all objects
- Merged in Gaia DR2 proper motion measurement for for all objects (if matched)
- Merged in GALEX nuv and fuv photometry for all objects (if matched)
- Wrote a module containing convenience functions to access and explore the training data

#### To do:
- [ ] Clean up the non-AGN sample (remove contaminated AGNs if possible)
- [ ] Fit DRW/DHO model to merged light curves (crts + other surveys)
- [x] Get colors (best-fit mags) for all sources in the two catalogs using casjobs
- [ ] Get corresponding CRTS/PTF/ZTF light curves for all sources
