#include "TripleGaussOverlap.h"
#include "TMath.h"

ClassImp(TripleGaussOverlap)

TripleGaussOverlap::TripleGaussOverlap(Double_t factor):
    TF2("TripleGaussOverlap", calcOverlap, -30.0, 30.0, -30.0, 30.0, 27)
{
    SetParameter(26, factor);
}

Double_t TripleGaussOverlap::calcOverlap(Double_t *x, Double_t *par)
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
    double w1N = par[10];
    double w2N = par[11];
    double xWidthM1 = par[12];
    double yWidthM1 = par[13];
    double xWidthM2 = par[14];
    double yWidthM2 = par[15];
    double rhoM1 = par[16];
    double rhoM2 = par[17];
    double w1M = par[18];
    double w2M = par[19];
    double xWidthW1 = par[20];
    double yWidthW1 = par[21];
    double xWidthW2 = par[22];
    double yWidthW2 = par[23];
    double rhoW1 = par[24];
    double rhoW2 = par[25];
    double factor = par[26];

    double beamN1 = calcGauss(xx, yy, x01, y01, xWidthN1, yWidthN1, rhoN1, factor);
    double beamM1 = calcGauss(xx, yy, x01, y01, xWidthM1, yWidthM1, rhoM1, factor);
    double beamW1 = calcGauss(xx, yy, x01, y01, xWidthW1, yWidthW1, rhoW1, factor);
    double beamN2 = calcGauss(xx, yy, x02, y02, xWidthN2, yWidthN2, rhoN2, factor);
    double beamM2 = calcGauss(xx, yy, x02, y02, xWidthM2, yWidthM2, rhoM2, factor);
    double beamW2 = calcGauss(xx, yy, x02, y02, xWidthW2, yWidthW2, rhoW2, factor);
    return (w1N*beamN1+w1M*beamM1+(1.0-w1N-w1M)*beamW1)*(w2N*beamN2+w2M*beamM2+(1.0-w2N-w2M)*beamW2);
}

Double_t TripleGaussOverlap::calcGauss(
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
