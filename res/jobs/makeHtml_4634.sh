#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
rm -r web/Fill4634
python makeHtml.py navigation res/hist/Fill4634_central.json SG DG TG SupG SupDG -b
python makeHtml.py summary res/hist/Fill4634_central.json SG DG TG SupG SupDG -b
python makeHtml.py plots res/hist/Fill4634_central.json noCorr 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4634_central.json SG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4634_central.json DG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4634_central.json TG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4634_central.json SupG 0 1 2 3 4 v2 -b
python makeHtml.py plots res/hist/Fill4634_central.json SupDG 0 1 2 3 4 v3 -b
