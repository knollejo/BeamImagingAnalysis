#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
rm -r web/Fill6868
python makeHtml.py navigation res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json noCorr SG DG TG SupG SupDG -b
python makeHtml.py summary res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json SG DG TG SupG SupDG -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json noCorr 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json SG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json DG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json TG 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json SupG 0 1 2 3 4 v2 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json SupDG 0 1 2 3 4 v4 -b
mv web/Fill6868/SupDG web/Fill6868/SupDG_v4
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_rereco_second.json res/hist/Fill6868_rereco_second_verytight.json res/hist/Fill6868_rereco_second_drift1.json res/hist/Fill6868_rereco_second_drift2.json SupDG 0 1 2 3 4 v3 -b
