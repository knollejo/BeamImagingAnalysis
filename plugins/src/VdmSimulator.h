#ifndef VDM_SIMULATOR
#define VDM_SIMULATOR

#include "TF2.h"
#include "TRandom.h"
#include "RtypesCore.h"
#include "RooFitResult.h"

class VdmSimulator : public TF2 {
public:
    VdmSimulator(): TF2() {};
    VdmSimulator(const TF2 &f);
    VdmSimulator(const TF2 &f, TRandom *_r);
    Double_t Integral();
    RooFitResult * SimulateScan(
        Int_t n, Int_t c1, Int_t c2, Double_t *pos1, Double_t *pos2,
        Double_t &peak, Double_t &area, Double_t &chisq, Double_t &nevents
    );
    void SetVerbose(Bool_t v=kTRUE);
    void SetParametrized(Bool_t p=kTRUE);
    Double_t mu1_low, mu1_high, mu2_low, mu2_high, sigma1_low, sigma1_high,
        sigma2_low, sigma2_high, sigmaDiff_low, sigmaDiff_high,
        const_low, const_high;
    void SetDefaultRanges();
protected:
    TRandom *r;
    Bool_t verbose;
    Bool_t parametrized;
private:
    ClassDef(VdmSimulator, 2)
};

#endif
