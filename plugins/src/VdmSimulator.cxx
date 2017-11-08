#include "VdmSimulator.h"
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
#include "RooCurve.h"
#include "RooAbsReal.h"

ClassImp(VdmSimulator)

VdmSimulator::VdmSimulator(const TF2 &f, TRandom *_r):
    TF2(f), r(_r)
{
    SetVerbose(kFALSE);
    SetParametrized(kTRUE);
    SetDefaultRanges();
}

VdmSimulator::VdmSimulator(const TF2 &f):
    TF2(f)
{
    r = new TRandom3();
    r->SetSeed(0);
    SetVerbose(kFALSE);
    SetParametrized(kTRUE);
    SetDefaultRanges();
}

Double_t VdmSimulator::Integral()
{
    Double_t result = TF2::Integral(-30.0, 30.0, -30.0, 30.0);
    //if(result < 1.0e-4) {
    //    result = TF2::Integral(-30.0, 30.0, -30.0, 30.0, 1.0e-12);
    //}
    return result;
}

RooFitResult * VdmSimulator::SimulateScan(
    Int_t n, Int_t c1, Int_t c2, Double_t *pos1, Double_t *pos2,
    Double_t &peak, Double_t &area, Double_t &chisq, Double_t &nevents
){
    TH1F *hist = new TH1F("hist", "hist", n, -0.5, (n-1)+0.5);
    for(int step=0; step<n; step++)
    {
        SetParameter(c1, pos1[step]);
        SetParameter(c2, pos2[step]);
        double integral = 800*Integral();
        double count = r->Poisson(integral);
        hist->SetBinContent(step+1, count);
        if(verbose)
        {
            std::cout << "<<< Scan step " << step << " with count " << count
                      << std::endl;
        }
    }
    SetParameter(c1, 0.0);
    SetParameter(c2, 0.0);
    nevents = hist->Integral();

    RooRealVar nscan("nscan", "nscanpt", -0.5, (n-1)+0.5);
    nscan.setBins(n);
    RooRealVar mu1("mu1", "mean 1", mu1_low, mu1_high);
    RooRealVar mu2("mu2", "mean 2", mu2_low, mu2_high);
    RooRealVar sigma1("sigma1", "sigma 1", sigma1_low, sigma1_high);
    RooAbsReal *sigma2;
    if(parametrized)
    {
        RooRealVar sigmaDiff("sigmaDiff", "sigma difference", sigmaDiff_low, sigmaDiff_high);
        sigma2 = new RooFormulaVar("sigma2", "sigma1+sigmaDiff", RooArgList(sigma1, sigmaDiff));
    }
    else
    {
        sigma2 = new RooRealVar("sigma2", "sigma 2", sigma2_low, sigma2_high);
    }
    RooGaussian gauss1("gauss1", "Gaussian 1", nscan, mu1, sigma1);
    RooGaussian gauss2("gauss2", "Gaussian 2", nscan, mu2, *sigma2);
    RooRealVar c("const", "c", const_low, const_high);
    RooAddPdf dg("dg", "double Gaussian", RooArgList(gauss1, gauss2), c);
    RooDataHist data("data", "simulated VdM data", RooArgSet(nscan), hist);
    RooFitResult *res = dg.fitTo(data, RooFit::Save());

    RooPlot *vtxframe = nscan.frame();
    data.plotOn(vtxframe);
    dg.plotOn(vtxframe, RooFit::Name("fit"));
    chisq = vtxframe->chiSquare();
    RooCurve *fit = (RooCurve*)vtxframe->findObject("fit");
    peak = 0.0;
    for(int i=0; i<1000*n; i++)
    {
        double val = fit->Eval(-0.5+0.001*i);
        if(val > peak)
            peak = val;
    }
    area = fit->Integral();

    delete hist;
    return res;
}

void VdmSimulator::SetVerbose(Bool_t v)
{
    verbose = v;
}

void VdmSimulator::SetParametrized(Bool_t p)
{
    parametrized = p;
}

void VdmSimulator::SetDefaultRanges()
{
    mu1_low = 8.0;
    mu1_high = 16.0;
    mu2_low = 8.0;
    mu2_high = 16.0;
    sigma1_low = 1.0;
    sigma1_high = 4.0;
    sigma2_low = 2.0;
    sigma2_high = 5.0;
    sigmaDiff_low = 0.001;
    sigmaDiff_high = 4.0;
    const_low = 0.0;
    const_high = 1.0;
}
