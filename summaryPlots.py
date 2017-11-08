from array import array

from ROOT import TGraphErrors, TH2F, TLegend, TMultiGraph

from lib.plot.plot import SingleHistBase

wip = True
colors = (46, 8, 9, 42, 38, 30)

def summary_plots():
    for fill, nameadd, values in [
        (4266, '', {
            'bcids': [51, 771, 1631, 2211, 2674],
            'variants': ['central', 'prompt', 'tight'],
            'central_val': [1.402, 1.411, 1.164, 1.549, 1.589],
            'central_err': [0.462, 0.463, 0.463, 0.462, 0.464],
            'prompt_val': [1.365, 0.636, 1.251, 1.428, 1.419],
            'prompt_err': [0.463, 0.471, 0.463, 0.464, 0.464],
            'tight_val': [1.267, 1.100, 1.042, 1.082, 1.047],
            'tight_err': [0.460, 0.460, 0.460, 0.459, 0.460]
        }),
        (4954, '', {
            'bcids': [41, 281, 872, 1783, 2063],
            'variants': ['central', 'prompt', 'tight', 'VdM'],
            'central_val': [0.794, 0.694, 1.642, 0.983, 0.993],
            'central_err': [0.516, 0.512, 0.533, 0.510, 0.520],
            'VdM_val': [0.776, 0.604, -1.000, 0.429, 1.591],
            'VdM_err': [0.515, 0.509, 0.000, 0.509, 0.516],
            'prompt_val': [0.912, 0.687, 1.046, 1.039, 1.835],
            'prompt_err': [0.516, 0.512, 0.520, 0.511, 0.532],
            'tight_val': [0.361, 0.939, 1.116, 0.666, 1.421],
            'tight_err': [0.515, 0.547, 0.639, 0.547, 0.533]
        }),
        (4954, '_drift', {
            'bcids': [41, 281, 872, 1783, 2063],
            'variants': ['central', 'drift1', 'drift2'],
            'central_val': [0.794, 0.694, 1.642, 0.983, 0.993],
            'central_err': [0.516, 0.512, 0.533, 0.510, 0.520],
            'drift1_val': [0.765, 0.907, 1.421, 0.926, 0.735],
            'drift1_err': [0.515, 0.510, 0.530, 0.512, 0.530],
            'drift2_val': [0.713, 0.718, 1.509, 0.856, 0.854],
            'drift2_err': [0.872, 0.513, 0.536, 0.510, 0.564]
        }),
        (4266, '_drift', {
            'bcids': [51, 771, 1631, 2211, 2674],
            'variants': ['central', 'drift1', 'drift2'],
            'central_val': [1.402, 1.411, 1.164, 1.549, 1.589],
            'central_err': [0.462, 0.463, 0.463, 0.462, 0.464],
            'drift1_val': [1.445, 1.163, 0.913, 1.272, 1.335],
            'drift1_err': [0.462, 0.464, 0.462, 0.462, 0.463],
            'drift2_val': [1.095, 0.810, 0.864, 1.279, 1.436],
            'drift2_err': [0.463, 0.463, 0.463, 0.463, 0.463]
        })
    ]:
        bcids = values['bcids']
        variants = values['variants']
        yval = {
            var: array('d', values['{0}_val'.format(var)]) for var in variants
        }
        yerr = {
            var: array('d', values['{0}_err'.format(var)]) for var in variants
        }
        xerr = array('d', [0.0]*len(bcids))
        maxi = max([max([
            v+e for v,e in zip(yval[var], yerr[var]) if v>0
        ]) for var in variants])
        mini = min([min([
            v-e for v,e in zip(yval[var], yerr[var]) if v>0
        ]) for var in variants])
        maxi, mini = maxi+0.2*(maxi-mini), mini-0.1*(maxi-mini)
        multi = TMultiGraph('multi', '')
        graphs = []
        for i, var in enumerate(variants):
            xval = array('d', [
                j-0.25+i*0.5/len(variants) for j in range(len(bcids))
            ])
            graph = TGraphErrors(len(bcids), xval, yval[var], xerr, yerr[var])
            graph.SetName(var)
            graph.SetMarkerStyle(20+i)
            graph.SetMarkerColor(colors[i])
            graph.SetLineColor(colors[i])
            multi.Add(graph)
            graphs.append(graph)
        leg = TLegend(0.15, 0.80, 0.85, 0.83)
        leg.SetNColumns(len(variants))
        leg.SetBorderSize(0)
        for var, graph in zip(variants, graphs):
            leg.AddEntry(graph, var, 'PL')
        axishist = TH2F(
            'axishist', '', len(bcids), -0.5, len(bcids)-0.5, 100, mini, maxi
        )
        for i, bx in enumerate(bcids):
            axishist.GetXaxis().SetBinLabel(i+1, '{0}'.format(bx))
        plot = SingleHistBase(
            axishist, name='Fill{0}summary{1}'.format(fill, nameadd), fill=fill,
            workinprogress=wip
        )
        plot._xtitle = 'BCID'
        plot._ytitle = 'correction [%] from fit'
        plot.xrange(-0.5, len(bcids)-0.5)
        plot.yrange(mini, maxi)
        plot._drawoption = 'AXIS'
        plot.draw()
        plot.xaxis().SetNdivisions(len(bcids), False)
        plot.xaxis().SetLabelSize(0.03)
        multi.Draw('P')
        leg.Draw()
        plot.save_pdf()
        plot.Close()

def main():
    summary_plots()

if __name__ == '__main__':
    main()
