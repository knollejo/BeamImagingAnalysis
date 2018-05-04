#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
rm -r web/Fill5563
python makeHtml.py navigation res/hist/Fill5563_vdm_verytight.json res/hist/Fill5527_vdm_extratight.json noCorr SG -b
python makeHtml.py plots res/hist/Fill5563_vdm_verytight.json res/hist/Fill5527_vdm_extratight.json noCorr 0 1 2 3 -b
python makeHtml.py plots res/hist/Fill5563_vdm_verytight.json res/hist/Fill5527_vdm_extratight.json SG 0 1 2 3 -b
