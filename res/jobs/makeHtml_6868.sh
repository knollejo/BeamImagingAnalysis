#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
rm -r web/Fill6868
python makeHtml.py navigation res/hist/Fill6868_second.json res/hist/Fill6868_first.json noCorr SG DG SupG SupDG -b
python makeHtml.py summary res/hist/Fill6868_second.json res/hist/Fill6868_first.json SG DG SupG SupDG -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_first.json noCorr 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_first.json SG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_first.json DG 0 1 2 3 4 -b
#python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_first.json TG 0 1 2 3 4 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_first.json SupG 0 1 2 3 4 v2 -b
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_first.json SupDG 0 1 2 3 4 v4 -b
mv web/Fill6868/SupDG web/Fill6868/SupDG_v4
python makeHtml.py plots res/hist/Fill6868_second.json res/hist/Fill6868_first.json SupDG 0 1 2 3 4 v3 -b
