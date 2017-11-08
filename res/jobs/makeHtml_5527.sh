#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
rm -r web/Fill5527
python makeHtml.py navigation res/hist/Fill5527_vdm_central.json res/hist/Fill5527_vdm_plus_lsc.json res/hist/Fill5527_vdm_minus_lsc.json SG DG TG SupG SupDG -b
python makeHtml.py summary res/hist/Fill5527_vdm_central.json res/hist/Fill5527_vdm_plus_lsc.json res/hist/Fill5527_vdm_minus_lsc.json SG DG TG SupG SupDG -b
python makeHtml.py plots res/hist/Fill5527_vdm_central.json res/hist/Fill5527_vdm_plus_lsc.json res/hist/Fill5527_vdm_minus_lsc.json SG 0 1 2 3 -b
python makeHtml.py plots res/hist/Fill5527_vdm_central.json res/hist/Fill5527_vdm_plus_lsc.json res/hist/Fill5527_vdm_minus_lsc.json DG 0 1 2 3 -b
python makeHtml.py plots res/hist/Fill5527_vdm_central.json res/hist/Fill5527_vdm_plus_lsc.json res/hist/Fill5527_vdm_minus_lsc.json TG 0 1 2 3 -b
python makeHtml.py plots res/hist/Fill5527_vdm_central.json res/hist/Fill5527_vdm_plus_lsc.json res/hist/Fill5527_vdm_minus_lsc.json SupG 0 1 2 3 v2 -b
python makeHtml.py plots res/hist/Fill5527_vdm_central.json res/hist/Fill5527_vdm_plus_lsc.json res/hist/Fill5527_vdm_minus_lsc.json SupDG 0 1 2 3 v3 -b
