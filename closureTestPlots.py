from array import array
from itertools import product
from sys import argv

from ROOT import (
    gStyle, TF1, TFile, TGraphErrors, TH1F, TH2F, TLegend, TMarker, TMultiGraph
)

from lib.io import BareRootFile
from lib.plot.plot import SingleHistBase

wip = True
colors = (46, 8, 9, 42, 38, 30)

def closureTest_plots(filename):
    f = BareRootFile(filename)
    tree = f.Get('closureTest')

    gStyle.SetStatX(0.9)
    gStyle.SetStatY(0.9)
    gStyle.SetStatW(0.2)
    gStyle.SetStatH(0.14)

    hist1 = TH1F('hist1', '', 55, 0.9, 2.0)
    hist2 = TH1F('hist2', '', 55, 0.9, 2.0)
    condition = (
        'fit_overlapDiff>=0 && temp_overlapDiff>=0 && '
        'fit_chisq/fit_dof<=2 && temp_chisq/temp_dof<=2'
    )
    tree.Draw('temp_chisq/temp_dof>>hist1', condition)
    tree.Draw('fit_chisq/fit_dof>>hist2', condition)
    for i, hist in [(0, hist1), (1, hist2)]:
        hist.SetLineColor(colors[i])
        hist.SetLineWidth(3)
    maxi = max(hist1.GetMaximum(), hist2.GetMaximum()) * 1.1
    plot = SingleHistBase(
        hist1, 'hist_numberPerChisq', fill=None, workinprogress=wip
    )
    gStyle.SetOptStat(10)
    plot._xtitle = '#chi^{2}/d.o.f.'
    plot._ytitle = 'number of toys'
    plot.yrange(0.0, maxi)
    leg = TLegend(0.65, 0.75, 0.89, 0.85)
    leg.SetBorderSize(0)
    leg.AddEntry(hist1, 'DG fit', 'L')
    leg.AddEntry(hist2, 'SupDG fit', 'L')
    plot.draw()
    hist2.Draw('SAMEH')
    leg.Draw()
    plot.save_pdf()
    plot.Close()

    hist3 = TH2F('hist3', '', 31, -0.05, 3.05, 31, -0.05, 3.05)
    tree.Draw('100*temp_overlapDiff:100*fit_overlapDiff>>hist3', condition)
    one = TF1('one', 'x', -10.0, 10.0)
    one.SetLineColor(1)
    plot = SingleHistBase(
        hist3, 'correctionDGvsSupDG', fill=None, workinprogress=wip
    )
    plot.add(one)
    plot._drawoption = 'BOX'
    plot._xtitle = 'correction [%] from SupDG fit'
    plot._ytitle = 'correction [%] from DG fit'
    plot._above = True
    plot.draw()
    plot.save_pdf()
    plot.Close()

    hist4 = TH2F('hist4', '', 22, 0.95, 1.5, 22, 0.95, 1.5)
    tree.Draw('temp_chisq/temp_dof:fit_chisq/fit_dof>>hist4', condition)
    plot = SingleHistBase(
        hist4, 'chisqDGvsSupDG', fill=None, workinprogress=wip
    )
    plot.add(one)
    plot._drawoption = 'BOX'
    plot._xtitle = '#chi^{2}/d.o.f. of SupDG fit'
    plot._ytitle = '#chi^{2}/d.o.f. of DG fit'
    plot._above = True
    plot.draw()
    plot.save_pdf()
    plot.Close()

    gStyle.SetStatX(0.9)
    gStyle.SetStatY(0.83)
    gStyle.SetStatW(0.3)
    gStyle.SetStatH(0.08)

    #bins_csq = [(0.0, 1.1), (1.1, 1.3), (1.3, 1.6), (1.6, 2.0)]
    #bins_cor = [(0.0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 2.5)]
    #bins_csq = [(1.07, 1.13), (1.06, 1.11), (1.3, 1.5), (1.08, 1.17), (1.1, 1.2)]
    #bins_cor = [(0.3, 0.8), (0.9, 1.2), (0.1, 0.5), (0.4, 0.7), (0.3, 1.1)]
    bins_csq = [(0.99, 1.06), (0.98, 1.07), (0.99, 1.10), (1.02, 1.06), (1.00, 1.06), (1.00, 1.04)]
    bins_cor = [(0.9, 1.9), (0.4, 1.6), (0.6, 1.5), (0.6, 1.9), (1.0, 1.3), (0.3, 1.5)]

    means = {mod: [
        [0.0 for __ in bins_cor] for __ in bins_csq
    ] for mod in ('DG', 'SupDG')}
    meane = {mod: [
        [0.0 for __ in bins_cor] for __ in bins_csq
    ] for mod in ('DG', 'SupDG')}
    rmses = {mod: [
        [0.0 for __ in bins_cor] for __ in bins_csq
    ] for mod in ('DG', 'SupDG')}
    rmser = {mod: [
        [0.0 for __ in bins_cor] for __ in bins_csq
    ] for mod in ('DG', 'SupDG')}

    #for i, (csq_lo, csq_hi) in enumerate(bins_csq):
    #    for j, (cor_lo, cor_hi) in enumerate(bins_cor):
    for i, ((csq_lo, csq_hi), (cor_lo, cor_hi)) in enumerate(zip(bins_csq, bins_cor)):
            j = i
            name = 'hist_{{0}}_{0}csq{1}_{2}cor{3}' \
                   .format(csq_lo, csq_hi, cor_lo, cor_hi)
            fields = '100*({0}_overlapDiff-toy_overlapDiff)>>hist'
            condition = (
                '100*{{0}}_overlapDiff>={0} && 100*{{0}}_overlapDiff<{1} && '
                '{{0}}_chisq/{{0}}_dof>={2} && {{0}}_chisq/{{0}}_dof<{3} && '
                'fit_overlapDiff>=0 && temp_overlapDiff>=0 && '
                'fit_chisq/fit_dof<=2 && temp_chisq/temp_dof<=2'
            ).format(cor_lo, cor_hi, csq_lo, csq_hi)
            xtitle = 'correction [%] from {0} fit #minus true correction [%]'
            line1 = '{0} < correction < {1}'.format(cor_lo, cor_hi)
            line2 = '{0} < #chi^{{2}}/d.o.f. < {1}'.format(csq_lo, csq_hi)
            gStyle.SetOptStat(2210)
            for prefix, modname in (('temp', 'DG'), ('fit', 'SupDG')):
                hist = TH1F('hist', '', 41, -2.05, 2.05)
                hist.StatOverflows()
                tree.Draw(fields.format(prefix), condition.format(prefix))
                plot = SingleHistBase(
                    hist, name.format(modname), fill=None, workinprogress=wip
                )
                gStyle.SetOptStat(2210)
                plot._xtitle = xtitle.format(modname)
                plot._ytitle = 'number of toys'
                plot.xrange(-2.05, 2.05)
                plot.yrange(0.0, plot._graph.GetMaximum()*1.2)
                pave = plot.add_pave(0.6, 0.83, 0.9, 0.9, border=True)
                pave(line1)
                pave(line2)
                plot.draw()
                plot.save_pdf()
                means[modname][i][j] = plot._graph.GetMean()
                meane[modname][i][j] = plot._graph.GetMeanError()
                rmses[modname][i][j] = plot._graph.GetRMS()
                rmser[modname][i][j] = plot._graph.GetRMSError()
                plot.Close()

    multi = TMultiGraph('multi', '')
    for k, modname in enumerate(('DG', 'SupDG')):
        for i, (csq_lo, csq_hi) in enumerate(bins_csq):
            xval = array('d', [j-0.35+k*0.4+i*0.1 for j in range(len(bins_cor))])
            xerr = array('d', [0.0]*len(bins_cor))
            yval = array('d', means[modname][i])
            yerr = array('d', rmses[modname][i])
            graph = TGraphErrors(len(bins_cor), xval, yval, xerr, yerr)
            graph.SetName('graph{0}{1}'.format(k, i))
            graph.SetMarkerStyle(22+k)
            graph.SetMarkerColor(colors[i])
            graph.SetLineColor(colors[i])
            multi.Add(graph)
    minvalues = [
        means[mod][i][j]-rmses[mod][i][j] for j in range(len(bins_cor))
        for i in range(len(bins_csq)) for mod in ('DG', 'SupDG')
    ]
    maxvalues = [
        means[mod][i][j]+rmses[mod][i][j] for j in range(len(bins_cor))
        for i in range(len(bins_csq)) for mod in ('DG', 'SupDG')
    ]
    mini, maxi = min(minvalues), max(maxvalues)
    mini, maxi = mini-0.1*(maxi-mini), maxi+0.3*(maxi-mini)
    hist = TH2F(
        'axishist', '', len(bins_cor), -0.5, len(bins_cor)-0.5, 100, mini, maxi
    )
    for j, (cor_lo, cor_hi) in enumerate(bins_cor):
        hist.GetXaxis().SetBinLabel(
            j+1, '{0}% #minus {1}%'.format(cor_lo, cor_hi)
        )
    leg1 = TLegend(0.53, 0.78, 0.63, 0.86)
    leg1.SetBorderSize(0)
    dgmarker = TMarker(0.0, 0.0, 22)
    supdgmarker = TMarker(0.0, 0.0, 23)
    leg1.AddEntry(dgmarker, 'DG', 'P')
    leg1.AddEntry(supdgmarker, 'SupDG', 'P')
    leg2 = TLegend(0.65, 0.75, 0.89, 0.89)
    leg2.SetBorderSize(0)
    csqmarker = TMarker(0.0, 0.0, 1)
    for i, (csq_lo, csq_hi) in enumerate(bins_csq):
        title = '{0} < #chi^{{2}}/d.o.f. < {1}'.format(csq_lo, csq_hi)
        entry = leg2.AddEntry(csqmarker, title, 'L')
        entry.SetMarkerColor(colors[i])
        entry.SetLineColor(colors[i])
    zero = TF1('zero', '0.0', -1.0, 10.0)
    zero.SetLineColor(1)
    zero.SetLineStyle(2)
    plot = SingleHistBase(
        hist, name='differenceDoubleDifferential', fill=None, workinprogress=wip
    )
    plot._xtitle = 'correction from fit'
    plot._ytitle = 'correction [%] from fit #minus true correction [%]'
    plot.xrange(-0.5, len(bins_cor)-0.5)
    plot.yrange(mini, maxi)
    plot._drawoption = 'AXIS'
    plot.draw()
    plot.xaxis().SetNdivisions(len(bins_cor), False)
    plot.xaxis().SetLabelSize(0.03)
    zero.Draw('SAME')
    multi.Draw('P')
    leg1.Draw()
    leg2.Draw()
    plot.save_pdf()
    plot.Close()

    bcid = (41, 281, 872, 1783, 2063)
    DGcor1 = array('d', [0.809, 0.392, 0.846, 0.731, 0.497])
    DGerr1 = array('d', [0.548, 0.567, 0.984, 0.984, 1.018])
    DGcor2 = array('d', [1.145, 0.799, 1.58, 1.465, 1.281])
    DGerr2 = array('d', [0.432, 0.395, 0.656, 0.656, 0.649])
    DGxval = array('d', [j-0.1 for j in range(5)])
    SupDGcor1 = array('d', [0.823, 0.761, 1.458, 0.986, 1.012])
    SupDGerr1 = array('d', [0.513, 0.513, 0.499, 0.513, 0.499])
    SupDGcor2 = array('d', [0.978, 0.916, 1.532, 1.141, 1.086])
    SupDGerr2 = array('d', [0.489, 0.489, 0.493, 0.489, 0.493])
    SupDGxval = array('d', [j+0.1 for j in range(5)])
    xerr = array('d', [0.0]*5)

    for fill, values in [
        (4266, {
            'DGcor': [1.021, 1.057, 0.968, 1.084, 1.114],
            'DGerr': [(e**2+0.74**2)**0.5 for e in (0.118, 0.124, 0.119, 0.117, 0.119)],
            'SupDGcor': [1.402, 1.411, 1.164, 1.549, 1.589],
            'SupDGerr': [(e**2+0.45**2)**0.5 for e in (0.106, 0.110, 0.108, 0.106, 0.115)],
            'bcids': [51, 771, 1631, 2211, 2674]
        }),
        (4954, {
            'DGcor': [0.799, 0.398, 0.845, 0.724, 0.502],
            'DGerr': [(e**2+0.79**2)**0.5 for e in (0.137, 0.124, 0.122, 0.130, 0.116)],
            'SupDGcor': [0.794, 0.694, 1.642, 0.983, 0.993],
            'SupDGerr': [(e**2+0.50**2)**0.5 for e in (0.126, 0.112, 0.186, 0.102, 0.144)],
            'bcids': [41, 281, 872, 1783, 2063]
        }),
        (4937, {
            'DGcor': [0.649, 0.494, 0.575, 0.527, 0.602],
            'DGerr': [(e**2+0.85**2)**0.5 for e in (0.127, 0.115, 0.120, 0.125)],
            'SupDGcor': [0.377, 0.611, 1.137, 0.453, 1.840],
            'SupDGerr': [(e**2+0.56**2)**0.5 for e in (0.100, 0.105, 0.288, 0.161, 0.207)],
            'bcids': [81, 875, 1610, 1690, 1730]
        }),
        (6016, {
            'DGcor': [0.146, 0.394, 0.377, 0.488, 0.184],
            'DGerr': [(e**2+1.15**2)**0.5 for e in (0.110, 0.114, 0.118, 0.123, 0.109)],
            'SupDGcor': [0.760, 0.953, 1.048 , 0.847, 0.373],
            'SupDGerr': [(e**2+0.79**2)**0.5 for e in (0.219, 0.094, 0.189, 0.098, 0.169)],
            'bcids': [41, 281, 872, 1783, 2063]
        })
    ]:
        bcid = values['bcids']
        DGcor = array('d', values['DGcor'])
        DGerr = array('d', values['DGerr'])
        DGxvl = array('d', [j-0.1 for j in range(len(bcid))])
        SupDGcor = array('d', values['SupDGcor'])
        SupDGerr = array('d', values['SupDGerr'])
        SupDGxvl = array('d', [j+0.1 for j in range(len(bcid))])
        xerr = array('d', [0.0]*len(bcid))
        maxi = max(
            max([v+e for v,e in zip(DGcor, DGerr)]),
            max([v+e for v,e in zip(SupDGcor, SupDGerr)])
        )
        mini = min(
            min([v-e for v,e in zip(DGcor, DGerr)]),
            min([v-e for v,e in zip(SupDGcor, SupDGerr)])
        )
        maxi, mini = maxi+0.2*(maxi-mini), mini-0.1*(maxi-mini)

        graphDG = TGraphErrors(len(bcid), DGxvl, DGcor, xerr, DGerr)
        graphDG.SetName('graphDG')
        graphSupDG = TGraphErrors(len(bcid), SupDGxvl, SupDGcor, xerr, SupDGerr)
        graphSupDG.SetName('graphSupDG')
        multi = TMultiGraph('multi', '')
        for i, graph in [
            (0, graphDG), (1, graphSupDG)
        ]:
            graph.SetMarkerStyle(22+i)
            graph.SetMarkerColor(colors[i])
            graph.SetLineColor(colors[i])
            multi.Add(graph)
        leg = TLegend(0.15, 0.80, 0.5, 0.83)
        leg.SetNColumns(2)
        leg.SetBorderSize(0)
        leg.AddEntry(graphDG, 'DG fit', 'PL')
        leg.AddEntry(graphSupDG, 'SupDG fit', 'PL')
        axishist = TH2F(
            'axishist', '', len(bcid), -0.5, len(bcid)-0.5, 100, mini, maxi
        )
        for i, bx in enumerate(bcid):
            axishist.GetXaxis().SetBinLabel(i+1, '{0}'.format(bx))

        plot = SingleHistBase(
            axishist, name='Fill{0}biased'.format(fill), fill=fill,
            workinprogress=wip
        )
        plot._xtitle = 'BCID'
        plot._ytitle = 'correction [%] from fit'
        plot.xrange(-0.5, len(bcid)-0.5)
        plot.yrange(mini, maxi)
        plot._drawoption = 'AXIS'
        plot.draw()
        plot.xaxis().SetNdivisions(len(bcid), False)
        plot.xaxis().SetLabelSize(0.03)
        multi.Draw('P')
        leg.Draw()
        plot.save_pdf()
        plot.Close()

        print
        print 'Fill', fill
        for bx, cor, err in zip(bcid, SupDGcor, SupDGerr):
            print 'BCID {0}:\t{1:.2f} +- {2:.2f}'.format(bx, cor, err)
        print

    # for mod in ('DG', 'SupDG'):
    #     for i in range(len(bins_csq)):
    #         for j in range(len(bins_cor)):
    #             print mod, '{0}-{1}'.format(bins_csq[i][0], bins_csq[i][1]),
    #             print '{0}-{1}'.format(bins_cor[j][0], bins_cor[j][1]),
    #             print means[mod][i][j], meane[mod][i][j],
    #             print rmses[mod][i][j], rmser[mod][i][j]

def main():
    closureTest_plots(argv[1])

if __name__ == '__main__':
    main()
