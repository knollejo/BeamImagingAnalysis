#include "SingleGaussOverlap.h"
#include "TMath.h"

ClassImp(SingleGaussOverlap)

SingleGaussOverlap::SingleGaussOverlap(Double_t factor):
    TF2("SingleGaussOverlap", calcOverlap, -30.0, 30.0, -30.0, 30.0, 11)
{
    SetParameter(10, factor);
}

Double_t SingleGaussOverlap::calcOverlap(Double_t *x, Double_t *par)
{
    double xx = x[0];
    double yy = x[1];
    double x01 = par[0];
    double y01 = par[1];
    double x02 = par[2];
    double y02 = par[3];
    double xWidthN1 = par[4];
    double yWidthN1 = par[5];
    double xWidthN2 = par[6];
    double yWidthN2 = par[7];
    double rhoN1 = par[8];
    double rhoN2 = par[9];
    double factor = par[10];

    double beamN1 = calcGauss(xx, yy, x01, y01, xWidthN1, yWidthN1, rhoN1, factor);
    double beamN2 = calcGauss(xx, yy, x02, y02, xWidthN2, yWidthN2, rhoN2, factor);
    return beamN1 * beamN2;
}

Double_t SingleGaussOverlap::calcGauss(
    Double_t x, Double_t y, Double_t x0, Double_t y0,
    Double_t xwidth, Double_t ywidth, Double_t rho, Double_t factor
)
{
    double xx = (x-x0)/xwidth;
    double yy = (y-y0)/ywidth;
    double norm = 2.0*TMath::Pi()*TMath::Sqrt(1.0-TMath::Power(rho, 2))*TMath::Abs(xwidth*ywidth);
    double argu = -0.5/(1.0-TMath::Power(rho, 2))*(TMath::Power(xx, 2)+TMath::Power(yy, 2)+-2.0*rho*xx*yy);
    return factor/norm*TMath::Exp(argu);
}
