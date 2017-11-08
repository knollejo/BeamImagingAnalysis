#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
rm -r web/Fill4954
python makeHtml.py navigation res/hist/Fill4954_*.json noCorr SG DG TG SupG SupDG -b
python makeHtml.py summary res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json SG DG TG SupG SupDG -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json noCorr 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json SG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json DG 0 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json DG 1 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json DG 2 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json DG 3 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json DG 4 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json TG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json SupG 0 1 2 3 4 v2 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json SupDG 0 v3 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json SupDG 1 v3 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json SupDG 2 v3 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json SupDG 3 v3 -b
python makeHtml.py plots res/hist/Fill4954_central.json res/hist/Fill4954_vdm.json res/hist/Fill4954_prompt_reco.json res/hist/Fill4954_loose_selection.json res/hist/Fill4954_tight_selection.json res/hist/Fill4954_transverse_drift_v1.json res/hist/Fill4954_transverse_drift_v2.json SupDG 4 v3 -b
