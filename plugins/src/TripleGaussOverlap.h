#ifndef TRIPLEGAUSS_OVERLAP
#define TRIPLEGAUSS_OVERLAP

#include "TF2.h"
#include "RtypesCore.h"

class TripleGaussOverlap : public TF2 {
public:
    TripleGaussOverlap(Double_t factor = 1.0);
    static Double_t calcOverlap(Double_t *x, Double_t *par);
protected:
    static Double_t calcGauss(
        Double_t x, Double_t y, Double_t x0, Double_t y0,
        Double_t xwidth, Double_t ywidth, Double_t rho, Double_t factor=1.0
    );
    Double_t factor;
private:
    ClassDef(TripleGaussOverlap, 1)
};

#endif
