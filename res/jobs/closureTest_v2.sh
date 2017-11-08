#!/bin/bash
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
python closureTest_v2.py $2 $3 $4 $5 $6
