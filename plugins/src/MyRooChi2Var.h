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

#ifndef MY_ROO_CHI2_VAR
#define MY_ROO_CHI2_VAR

#include "RooChi2Var.h"
#include "RooAbsOptTestStatistic.h"
#include "RooCmdArg.h"
#include "RooDataHist.h"
#include "RooAbsPdf.h"

class MyRooChi2Var : public RooChi2Var {
public:
    MyRooChi2Var(
        const char *name, const char* title, RooAbsReal& func, RooDataHist& data,
        const RooCmdArg& arg1, const RooCmdArg& arg2=RooCmdArg::none(),
        const RooCmdArg& arg3=RooCmdArg::none(), const RooCmdArg& arg4=RooCmdArg::none(),
        const RooCmdArg& arg5=RooCmdArg::none(), const RooCmdArg& arg6=RooCmdArg::none(),
        const RooCmdArg& arg7=RooCmdArg::none(), const RooCmdArg& arg8=RooCmdArg::none(),
        const RooCmdArg& arg9=RooCmdArg::none()
    );
    MyRooChi2Var(
        const char *name, const char* title, RooAbsPdf& pdf, RooDataHist& data,
        const RooCmdArg& arg1, const RooCmdArg& arg2=RooCmdArg::none(),
        const RooCmdArg& arg3=RooCmdArg::none(), const RooCmdArg& arg4=RooCmdArg::none(),
        const RooCmdArg& arg5=RooCmdArg::none(), const RooCmdArg& arg6=RooCmdArg::none(),
        const RooCmdArg& arg7=RooCmdArg::none(), const RooCmdArg& arg8=RooCmdArg::none(),
        const RooCmdArg& arg9=RooCmdArg::none()
    );
    MyRooChi2Var(
        const char *name, const char *title, RooAbsPdf& pdf, RooDataHist& data,
        Bool_t extended=kFALSE, const char* rangeName=0, const char* addCoefRangeName=0,
        Int_t nCPU=1, RooFit::MPSplit interleave=RooFit::BulkPartition, Bool_t verbose=kTRUE,
        Bool_t splitCutRange=kTRUE, RooDataHist::ErrorType etype=RooDataHist::SumW2
    );
    MyRooChi2Var(
        const char *name, const char *title, RooAbsReal& func, RooDataHist& data,
        const RooArgSet& projDeps, FuncMode funcMode, const char* rangeName=0, const char* addCoefRangeName=0,
        Int_t nCPU=1, RooFit::MPSplit interleave=RooFit::BulkPartition, Bool_t verbose=kTRUE,
        Bool_t splitCutRange=kTRUE, RooDataHist::ErrorType etype=RooDataHist::SumW2
    );
    MyRooChi2Var(const MyRooChi2Var& other, const char* name=0);
    virtual TObject* clone(const char* newname) const {
        return new MyRooChi2Var(*this, newname);
    }
    virtual RooAbsTestStatistic* create(
        const char *name, const char *title, RooAbsReal& pdf, RooAbsData& dhist,
        const RooArgSet& projDeps, const char* rangeName=0, const char* addCoefRangeName=0,
        Int_t nCPU=1, RooFit::MPSplit interleave=RooFit::BulkPartition, Bool_t verbose=kTRUE,
        Bool_t splitCutRange=kTRUE, Bool_t = kFALSE
    )
    {
        return new MyRooChi2Var(
            name, title, (RooAbsPdf&)pdf, (RooDataHist&)dhist, projDeps,
            _funcMode, rangeName, addCoefRangeName, nCPU, interleave, verbose,
            splitCutRange, _etype
        );
    }
    virtual ~MyRooChi2Var();
protected:
    virtual Double_t evaluatePartition(
        Int_t firstEvent, Int_t lastEvent, Int_t stepSize
    ) const;
private:
    ClassDef(MyRooChi2Var, 1)
};

#endif
