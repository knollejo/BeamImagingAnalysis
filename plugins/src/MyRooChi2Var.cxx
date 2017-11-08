/*****************************************************************************
 * Project: RooFit                                                           *
 * Package: RooFitCore                                                       *
 * Authors:                                                                  *
 *   WV, Wouter Verkerke, UC Santa Barbara, verkerke@slac.stanford.edu       *
 *   DK, David Kirkby,    UC Irvine,         dkirkby@uci.edu                 *
 *                                                                           *
 * Copyright (c) 2000-2005, Regents of the University of California          *
 *                          and Stanford University. All rights reserved.    *
 *                                                                           *
 * Redistribution and use in source and binary forms,                        *
 * with or without modification, are permitted according to the terms        *
 * listed in LICENSE (http://roofit.sourceforge.net/license.txt)             *
 *                                                                           *
 * Edited by Joscha Knolle in 2017                                           *
 *****************************************************************************/

#include "RooFit.h"
#include "MyRooChi2Var.h"
#include "RooDataHist.h"
#include "RooAbsPdf.h"
#include "RooCmdConfig.h"
#include "RooMsgService.h"
#include "Riostream.h"
#include "RooRealVar.h"
#include "RooAbsDataStore.h"
#include "RooAddition.h"

using namespace std;

ClassImp(MyRooChi2Var)

MyRooChi2Var::MyRooChi2Var(
    const char *name, const char* title, RooAbsReal& func, RooDataHist& data,
    const RooCmdArg& arg1, const RooCmdArg& arg2,const RooCmdArg& arg3,
    const RooCmdArg& arg4, const RooCmdArg& arg5,const RooCmdArg& arg6,
    const RooCmdArg& arg7, const RooCmdArg& arg8,const RooCmdArg& arg9
):
    RooChi2Var(
        name, title, func, data, arg1, arg2, arg3,
        arg4, arg5, arg6, arg7, arg8, arg9
    )
{}

MyRooChi2Var::MyRooChi2Var(
    const char *name, const char* title, RooAbsPdf& pdf, RooDataHist& data,
    const RooCmdArg& arg1, const RooCmdArg& arg2,const RooCmdArg& arg3,
    const RooCmdArg& arg4, const RooCmdArg& arg5,const RooCmdArg& arg6,
    const RooCmdArg& arg7, const RooCmdArg& arg8,const RooCmdArg& arg9
):
    RooChi2Var(
        name, title, pdf, data, arg1, arg2, arg3,
        arg4, arg5, arg6, arg7, arg8, arg9
    )
{}

MyRooChi2Var::MyRooChi2Var(
    const char *name, const char *title, RooAbsPdf& pdf, RooDataHist& data,
    Bool_t extended, const char* rangeName, const char* addCoefRangeName,
    Int_t nCPU, RooFit::MPSplit interleave, Bool_t verbose,
    Bool_t splitCutRange, RooDataHist::ErrorType etype
):
    RooChi2Var(
        name, title, pdf, data, extended, rangeName, addCoefRangeName,
        nCPU, interleave, verbose, splitCutRange, etype
    )
{}

MyRooChi2Var::MyRooChi2Var(
    const char *name, const char *title, RooAbsReal& func, RooDataHist& data,
    const RooArgSet& projDeps, FuncMode funcMode, const char* rangeName,
    const char* addCoefRangeName, Int_t nCPU, RooFit::MPSplit interleave,
    Bool_t verbose, Bool_t splitCutRange, RooDataHist::ErrorType etype
):
    RooChi2Var(
        name, title, func, data, projDeps, funcMode, rangeName,
        addCoefRangeName, nCPU, interleave, verbose, splitCutRange, etype
    )
{}

MyRooChi2Var::MyRooChi2Var(const MyRooChi2Var& other, const char* name):
    RooChi2Var(other, name)
{}

MyRooChi2Var::~MyRooChi2Var()
{}

Double_t MyRooChi2Var::evaluatePartition(
    Int_t firstEvent, Int_t lastEvent, Int_t stepSize
) const
{
    Int_t i;
    Double_t result(0), carry(0);

    _dataClone->store()->recalculateCache(_projDeps, firstEvent, lastEvent, stepSize, kFALSE);

    Double_t normFactor(1);
    switch (_funcMode)
    {
        case Function:
            normFactor = 1;
            break;
        case Pdf:
            normFactor = _dataClone->sumEntries();
            break;
        case ExtendedPdf:
            normFactor = ((RooAbsPdf*)_funcClone)->expectedEvents(_dataClone->get());
            break;
    }

    RooDataHist* hdata = (RooDataHist*) _dataClone;
    for(i=firstEvent; i<lastEvent; i+=stepSize)
    {
        hdata->get(i);
        if (!hdata->valid())
            continue;

        const Double_t nData = hdata->weight();
        const Double_t nPdf = _funcClone->getVal(_normSet) * normFactor * hdata->binVolume();
        const Double_t eExt = nPdf-nData;

        Double_t eInt;
        if(_etype != RooAbsData::Expected)
        {
            Double_t eIntLo, eIntHi;
            hdata->weightError(eIntLo, eIntHi, _etype);
            eInt = (eExt>0) ? eIntHi : eIntLo;
        }
        else
        {
            eInt = sqrt(nPdf);
        }

        if (0.0 == nData * nData)
            continue;
        if (0.0 == eInt * eInt && 0.0 == nData * nData && 0.0 == nPdf * nPdf)
            continue;
        if (0.0 == eInt * eInt)
        {
            coutE(Eval) << "RooChi2Var::RooChi2Var(" << GetName()
                        << ") INFINITY ERROR: bin " << i
                        << " has zero error" << endl;
            return 0.0;
        }

        Double_t term = eExt*eExt/(eInt*eInt);
        Double_t y = term - carry;
        Double_t t = result + y;
        carry = (t - result) - y;
        result = t;
    }

    _evalCarry = carry;
    return result;
}
