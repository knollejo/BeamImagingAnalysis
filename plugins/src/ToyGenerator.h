#ifndef TOY_GENERATOR
#define TOY_GENERATOR

#include "TF2.h"
#include "TRandom.h"
#include "RtypesCore.h"
#include "TH2F.h"

class ToyGenerator : public TF2 {
public:
    ToyGenerator(): TF2() {};
    ToyGenerator(const TF2 &f);
    ToyGenerator(const TF2 &f, TRandom *_r);
    Double_t Integral();
    void SetResolution(Double_t _resx, Double_t _resy=-1.0);
    void GetRandom2(Double_t &xrandom, Double_t &yrandom);
    TH2F *GenerateToys(
        Int_t n, Int_t c, Double_t *pos, Int_t nbins, Int_t &nevents
    );
    void SetVerbose(Bool_t v=kTRUE);
protected:
    TRandom *r;
    Double_t resx, resy;
    Bool_t verbose;
private:
    ClassDef(ToyGenerator, 1)
};

#endif
