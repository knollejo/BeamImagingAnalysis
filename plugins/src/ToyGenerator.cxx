#include "ToyGenerator.h"
#include <iostream>
#include "TRandom3.h"
#include "TH1.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "RooGaussian.h"
#include "RooAddPdf.h"
#include "RooDataHist.h"
#include "RooArgList.h"
#include "RooArgSet.h"
#include "RooGlobalFunc.h"
#include "RooPlot.h"

ClassImp(ToyGenerator)

ToyGenerator::ToyGenerator(const TF2 &f, TRandom *_r):
    TF2(f), r(_r)
{
    SetVerbose(kFALSE);
}

ToyGenerator::ToyGenerator(const TF2 &f):
    TF2(f)
{
    r = new TRandom3();
    r->SetSeed(0);
    SetVerbose(kFALSE);
}

Double_t ToyGenerator::Integral()
{
    Double_t result = TF2::Integral(-30.0, 30.0, -30.0, 30.0);
    return result;
}

void ToyGenerator::SetResolution(Double_t _resx, Double_t _resy)
{
    resx = _resx;
    if(_resy >= 0.0)
    {
        resy = _resy;
    }
    else
    {
        resy = _resx;
    }
}

void ToyGenerator::GetRandom2(Double_t &xrandom, Double_t &yrandom)
{
    TF2::GetRandom2(xrandom, yrandom);
    xrandom = r->Gaus(xrandom, resx);
    yrandom = r->Gaus(yrandom, resy);
}

TH2F * ToyGenerator::GenerateToys(
    Int_t n, Int_t c, Double_t *pos, Int_t nbins, Int_t &nevents
)
{
    TH2F *hist = new TH2F("hist", "hist", nbins, -10.0, 10.0, nbins, -10.0, 10.0);
    double vtxx, vtxy;
    nevents = 0;
    for(int step=0; step<n; step++)
    {
        SetParameter(c, pos[step]);
        double integral = 80.0*Integral();
        int nEvents = int(r->PoissonD(integral));
        if(verbose)
        {
            std::cout << "<<< Step " << step << ": Generate " << nEvents
                      << " events" << std::endl;
        }
        for(int i=0; i<nEvents; i++)
        {
            GetRandom2(vtxx, vtxy);
            hist->Fill(vtxx, vtxy);
        }
        nevents += nEvents;
    }
    SetParameter(c, 0.0);

    return hist;
}

void ToyGenerator::SetVerbose(Bool_t v)
{
    verbose = v;
}
