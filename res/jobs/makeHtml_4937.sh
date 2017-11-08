#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
rm -r web/Fill4937
python makeHtml.py navigation res/hist/Fill4937_central.json DG SupDG -b
python makeHtml.py summary res/hist/Fill4937_central.json DG SupDG -b
python makeHtml.py plots res/hist/Fill4937_central.json DG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4937_central.json SupDG 0 1 2 3 4 v3 -b
