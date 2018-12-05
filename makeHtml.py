from json import dump, load
from math import isnan
from os import mkdir
from os.path import exists
from re import match
from shutil import copyfile
from sys import argv

from ROOT import gDirectory, TF1, TH1F

from lib.io import RootFile
from lib.plot.residual import CombinedResidualPlot, ResidualPlot
from lib.plot.summary import ChiSquareSummary, CorrectionSummary
from lib.shape.dg import DoubleGaussFit, SuperGaussFit
from lib.shape.sg import SingleGauss, SingleGaussUncorrelated
from lib.shape.tg import SuperDoubleGaussFit, TripleGaussFit

result_fields = (
    'overlapIntegral', 'overlapDiff', 'randomized ovDiff', 'chiSq', 'd.o.f.',
    'chiSq/dof', 'neg.log.lik.', 'time of fit', 'time of simulation',
    'time of residuals', 'time of randomization', 'scaling'
)

summary_fields = (
    ('chiSq/dof', '%1$.4f'),
    ('overlapDiff', '%1$.3f&#37;<br />&plusmn;%2$.3f&#37;')
)

longnames = {
    'SG': 'Single Gauss', 'DG': 'Double Gauss', 'TG': 'TripleGauss',
    'SupG': 'Super Gauss', 'SupDG': 'Super Double Gauss',
    'noCorr': 'Uncorrelated'
}

v3 = True
v4 = False

colors = (1, 46, 8, 9, 42, 38, 30)

def get_result(result, f, model):
    try:
        if match('^overlapIntegral$', result):
            val = f.get('overlap_true').GetVal()
            err = f.get('overlap_rms').GetVal()
            if val < 0.0:
                hist = TH1F('thisoverlap', '', 1000, 0.0, 1.0)
                f.Get('corrTree').Draw('overlapTrue>>thisoverlap', '', 'goff')
                val = hist.GetMean()
                err = hist.GetRMS()
            return '{:.3e}<br />&plusmn;{:.3e}'.format(val, err)
        elif match('^overlapDiff$', result):
            try:
                hist = f.get('overlap_diff')
            except NameError:
                f.Get('corrTree').Draw('overlapDiff>>hnew', '', 'goff')
                val = gDirectory.Get('hnew').GetMean()
                mini, maxi = val-0.5, val+0.5
                hist = TH1F('myoverlap', '', 1000, mini, maxi)
                f.Get('corrTree').Draw('overlapDiff>>myoverlap', '', 'goff')
            val = hist.GetMean()*100.0
            err = hist.GetRMS()*100.0
            return '{:.3f}&#37;<br />&plusmn;{:.3f}&#37;'.format(val, err)
        elif match('^randomized ovDiff$', result):
            hist = TH1F('myoverlap', '', 1000, -0.5, 0.5)
            f.Get('rndmzd_corrTree').Draw('overlapDiff>>myoverlap', '', 'goff')
            val = hist.GetMean()*100.0
            err = hist.GetRMS()*100.0
            return '{:.3f}&#37;<br />&plusmn;{:.3f}&#37;'.format(val, err)
        elif match('^chiSq$', result):
            val = (
                f.get('chisqX1').GetVal() + f.get('chisqX2').GetVal()
                + f.get('chisqY1').GetVal() + f.get('chisqY2').GetVal()
            )
            return '{:.0f}'.format(val)
        elif match('^d.o.f.$', result):
            val = (
                f.get('dofX1').GetVal() + f.get('dofX2').GetVal()
                + f.get('dofY1').GetVal() + f.get('dofY2').GetVal()
            )
            return '{:.0f}'.format(val)
        elif match('chiSq/dof', result):
            val = (
                f.get('chisqX1').GetVal() + f.get('chisqX2').GetVal()
                + f.get('chisqY1').GetVal() + f.get('chisqY2').GetVal()
            ) / (
                f.get('dofX1').GetVal() + f.get('dofX2').GetVal()
                + f.get('dofY1').GetVal() + f.get('dofY2').GetVal()
                - model.dof()
            )
            return '{:.4f}'.format(val)
        elif match('^time of fit$', result):
            return f.get('timestamp').GetTitle()
        elif match('^time of simulation$', result):
            return f.get('corrTimestamp').GetTitle()
        elif match('^time of residuals$', result):
            return f.get('resTimestamp').GetTitle()
        elif match('^time of randomization$', result):
            return f.get('rndmzdTimestamp').GetTitle()
        elif match('^neg.log.lik.$', result):
            val = f.get('fitResult').minNll()
            return '{:e}'.format(val)
        elif match('^scaling$', result):
            val = f.get('scaling').GetVal()*1.0e4
            return '1={:.2f}&micro;m'.format(val)
        else:
            raise NameError()
    except NameError:
        return ''
    except TypeError:
        return ''

def get_parameter(par, f):
    try:
        val = f.get('final/{0}'.format(par)).GetVal()
        err = f.get('final/{0}_error'.format(par)).GetVal()
        scaling = f.get('scaling').GetVal()*1.0e4
    except NameError:
        return ''
    if match('^[xy]Width[NMW][12]$', par) or match('^[xy]0[12][12]$', par):
        return '{0:.2f}&micro;m<br />&plusmn;{1:.2f}&micro;m' \
               .format(val*scaling, err*scaling)
    elif match('^rho[NMW][12]$', par):
        return '{0:.3f}<br />&plusmn;{1:.3f}'.format(val, err)
    elif match('^w[12][NMW]$', par):
        return '{0:.3f}&#37;<br />&plusmn;{1:.3f}&#37;' \
               .format(val*100.0, err*100.0)
    elif match('^[xy]VtxRes$', par):
        return '{0:.3f}&micro;m'.format(val*scaling)
    else:
        return '{0}<br />&plusmn;{1}'.format(val, err)

def get_fitpar(par, f):
    try:
        val = f.get('final/{0}'.format(par)).GetVal()
    except NameError:
        return ''
    return '{0:.3f}'.format(val)

def get_summary(summary, f, model):
    try:
        if match('^chiSq/dof$', summary):
            val = (
                f.get('chisqX1').GetVal() + f.get('chisqX2').GetVal()
                + f.get('chisqY1').GetVal() + f.get('chisqY2').GetVal()
            ) / (
                f.get('dofX1').GetVal() + f.get('dofX2').GetVal()
                + f.get('dofY1').GetVal() + f.get('dofY2').GetVal()
                - model.dof()
            )
            err = 0.0
            return (val, err)
        elif match('^overlapDiff$', summary):
            try:
                hist = f.get('overlap_diff')
            except NameError:
                hist = TH1F('myoverlap', '', 1000, -0.5, 0.5)
                f.Get('corrTree').Draw('overlapDiff>>myoverlap', '', 'goff')
            val = hist.GetMean()*100.0
            err = hist.GetRMS()*100.0
            return (val, err)
        else:
            raise NameError()
    except NameError:
        return (float('nan'), float('nan'))

def make_plots(names, bcid, models, fill, version=1, wip=False):
    prefix = names[0][:names[0].index('_')]
    names = [name[len(prefix)+1:] for name in names]
    # if version > 1:
    #     modadd = '_v{0}'.format(version)
    # else:
    #     modadd = ''
    modadd = ''
    for mod in models:
        path = 'web/{0}/{1}{2}'.format(prefix, mod.name(), modadd)
        if not exists(path):
            mkdir(path)
        path = 'web/{0}/{1}{2}/bcid{3}'.format(prefix, mod.name(), modadd, bcid)
        if not exists(path):
            mkdir(path)
        json = {
            'headline': prefix,
            'modelname': {
                'SG': 'Single Gauss', 'DG': 'Double Gauss',
                'TG': 'Triple Gauss', 'SupG': 'Super Gauss',
                'SupDG': 'Super Double Gauss', 'noCorr': 'Uncorrelated'
            }[mod.name()],
            'names': names,
            'resultFields': result_fields,
            'physicsFields': tuple(mod.physics_parameters),
            'fitFields': tuple(mod.fit_parameters),
            'results': {f: {} for f in result_fields},
            'physics': {f: {} for f in mod.physics_parameters},
            'fits': {f: {} for f in mod.fit_parameters}
        }
        for name in names:
            if version in (3, 4):
                extra = '_best'
            else:
                extra = ''
            filename = 'BeamImaging_v{0}_{1}_{2}{3}_{4}_bcid{5}'.format(
                version, prefix, name, extra, mod.name(), bcid
            )
            with RootFile(filename) as f:
                for fld in result_fields:
                    json['results'][fld][name] = get_result(fld, f, mod)
                for fld in mod.physics_parameters:
                    json['physics'][fld][name] = get_parameter(fld, f)
                for fld in mod.fit_parameters:
                    json['fits'][fld][name] = get_fitpar(fld, f)
                reshists = [(
                    f.Get('residualHist{0}'.format(c)),
                    f.Get('dataHist{0}'.format(c)),
                    f.Get('modelHist{0}'.format(c))
                ) for c in ('X1', 'Y1', 'X2', 'Y2')]
                for hres, hdat, hmod in reshists:
                    hres.SetDirectory(0)
                    hdat.SetDirectory(0)
                    hmod.SetDirectory(0)
                chisq = [
                    f.get('chisq{0}'.format(c)).GetVal()
                    / f.get('dof{0}'.format(c)).GetVal()
                    for c in ('X1', 'Y1', 'X2', 'Y2')
                ]
            for (hres, hdat, hmod), csq in zip(reshists, chisq):
                c = hres.GetName()[-2:]
                plot = ResidualPlot(hres, fill=fill, workinprogress=wip)
                pave = plot.add_pave(0.61, 0.79, 0.88, 0.88)
                pave('Scan {0}, BCID {1}'.format(c, bcid))
                pave('{0} fit'.format(json['modelname']))
                pave('#chi^{{2}}/d.o.f. = {0:.4f}'.format(csq))
                plotname = '{0}_res_{1}_{2}_bcid{3}_{4}'.format(
                    prefix, name, mod.name(), bcid, c
                )
                plot.draw()
                plot.SaveAs('{0}/{1}.png'.format(path, plotname))
                plot.SaveAs('{0}/{1}.pdf'.format(path, plotname))
                plot.Close()
                plot = CombinedResidualPlot(
                    hdat, hmod, nbins=50,
                    maxr=0.012 if fill in (5527, 5563) else 0.04,
                    fill=fill, workinprogress=wip
                )
                plot._y1range = (-1.9, 1.9)
                plot._y2range = (-0.59, 0.59)
                pave = plot.add_pave(0.61, 0.815, 0.88, 0.88)
                pave('Scan {0}, BCID {1}'.format(c, bcid))
                pave('{0} fit'.format(json['modelname']))
                plotname = '{0}_comb_{1}_{2}_bcid{3}_{4}'.format(
                    prefix, name, mod.name(), bcid, c
                )
                plot.SetName(plotname)
                plot._above = True
                plot.draw()
                zero = TF1('zero', '0.0', -1.6, 1.6)
                zero.SetLineColor(1)
                zero.SetLineWidth(1)
                zero.SetLineStyle(3)
                plot.cd(1)
                zero.Draw('SAME')
                plot.cd(2)
                zero.Draw('SAME')
                plot.cd()
                plot.SaveAs('{0}/{1}.png'.format(path, plotname))
                plot.SaveAs('{0}/{1}.pdf'.format(path, plotname))
                plot.Close()
        with open('{0}/data.json'.format(path), 'w') as f:
            dump(json, f, dump)

def make_summary(names, bcids, models, fill, wip=True):
    prefix = names[0][:names[0].index('_')]
    names = [name[len(prefix)+1:] for name in names]
    bcids = sorted(set(bcids[0]).intersection(*bcids))
    path = 'web/{0}/summary'.format(prefix)
    if not exists('web'):
        mkdir('web')
    if not exists('web/{0}'.format(prefix)):
        mkdir('web/{0}'.format(prefix))
    if not exists(path):
        mkdir(path)
    json = {
        'headline': prefix,
        'models': [m.name() for m in models],
        'bcids': bcids,
        'names': names,
        'summaryFields': [s[0] for s in summary_fields],
        'summaryFormat': [s[1] for s in summary_fields],
        'summaries': {s[0]: {
            name: [[None for c in bcids] for m in models] for name in names
        } for s in summary_fields}
    }
    for name in names:
        for i, mod in enumerate(models):
            for j, bcid in enumerate(bcids):
                filename = 'BeamImaging_{{0}}_{0}_{1}{{1}}_{2}_bcid{3}'.format(
                    prefix, name, mod.name(), bcid
                )
                versions = ['v1']
                # if mod.name() in ('DG', 'TG', 'SupG'):
                if mod.name().startswith('Sup'):
                    # versions.append('v2')
                    versions = ['v2']
                if v3 and mod.name() == 'SupDG':
                    # versions.append('v3')
                    versions = ['v3']
                elif v4 and mod.name() == 'SupDG':
                    versions = ['v4']
                bestchisq = 1.0e9
                for version in versions:
                    if version in ('v3', 'v4'):
                        extra = '_best'
                    else:
                        extra = ''
                    with RootFile(filename.format(version, extra)) as f:
                        csq = get_summary('chiSq/dof', f, mod)[0]
                        if isnan(csq) or csq > bestchisq:
                            continue
                        for fld, __ in summary_fields:
                            json['summaries'][fld][name][i][j] = get_summary(
                                fld, f, mod
                            )
        corrections = json['summaries']['overlapDiff'][name]
        plot = CorrectionSummary(
            [m.name() for m in models], bcids, corrections, fill=fill,
            workinprogress=wip
        )
        plotname = '{0}_corr_{1}'.format(prefix, name)
        plot.colors = (colors[i] for i in range(len(models)))
        plot.create_legend([longnames[m.name()] for m in models])
        plot.draw()
        plot.SaveAs('{0}/{1}.png'.format(path, plotname))
        plot.SaveAs('{0}/{1}.pdf'.format(path, plotname))
        plot.Close()
        chisqs = json['summaries']['chiSq/dof'][name]
        plot = ChiSquareSummary(
            [m.name() for m in models], bcids, chisqs, fill=fill,
            workinprogress=wip
        )
        plotname = '{0}_chisq_{1}'.format(prefix, name)
        plot.colors = (colors[i] for i in range(len(models)))
        plot.create_legend([longnames[m.name()] for m in models])
        plot.draw()
        plot.SaveAs('{0}/{1}.png'.format(path, plotname))
        plot.SaveAs('{0}/{1}.pdf'.format(path, plotname))
        plot.Close()
    with open('{0}/data.json'.format(path), 'w') as f:
        dump(json, f, dump)

def make_navigation(names, bcids, models, fill):
    prefix = names[0][:names[0].index('_')]
    names = [name[len(prefix)+1:] for name in names]
    bcids = sorted(set(bcids[0]).intersection(*bcids))
    path = 'web/{0}'.format(prefix)
    if not exists('web'):
        mkdir('web')
    if not exists(path):
        mkdir(path)
    for filename in ('index', 'navigation', 'page', 'summary'):
        copyfile(
            'res/html/{0}.php'.format(filename),
            '{0}/{1}.php'.format(path, filename)
        )
    json = {
        'headline': prefix,
        'models': [[longnames[m.name()], m.name()] for m in models],
        'bcids': bcids
    }
    # for m in models:
    #     if m.name() not in ['SupG', 'SupDG']:
    #         continue
    #     json['models'].append([
    #         '{0} (2)'.format(longnames[m.name()]), '{0}_v2'.format(m.name())
    #     ])
    #     if v3 and m.name() == 'SupDG':
    #         json['models'].append([
    #             '{0} (3)'.format(longnames[m.name()]), '{0}_v3'.format(m.name())
    #         ])
    with open('{0}/nav.json'.format(path), 'w') as f:
        dump(json, f, indent=4)

fitmodels = ('noCorr', 'SG', 'DG', 'TG', 'SupG', 'SupDG')

def main():
    if len(argv) < 2 or not argv[1] or not argv[1] in (
        'navigation', 'plots', 'summary'
    ):
        raise RuntimeError(
            'Specify first argument: Create navigation, summary or plots.'
        )
    if len(argv) < 3 or not argv[2] or not exists(argv[2]):
        raise RuntimeError('Specify second arguments: JSON config files.')
    configs = []
    for i, filename in enumerate(argv[2:], start=2):
        if not filename or not exists(filename):
            break
        with open(filename) as f:
            configs.append(load(f))
    else:
        raise RuntimeError(
            'Specify third arguments: Fit models ({0}).' \
            .format(', '.join(fitmodels))
        )
    if not argv[i] or argv[i] not in fitmodels:
        raise RuntimeError(
            'Specify third arguments: Fit models ({0}).' \
            .format(', '.join(fitmodels))
        )
    models = []
    for j, model in enumerate(argv[i:], start=i):
        if model not in fitmodels:
            break
        models.append(model)
    names = [config['name'] for config in configs]
    models = [{
        'SG': SingleGauss, 'DG': DoubleGaussFit, 'TG': TripleGaussFit,
        'SupG': SuperGaussFit, 'SupDG': SuperDoubleGaussFit,
        'noCorr': SingleGaussUncorrelated
    }[model] for model in models]
    fill = configs[0]['fill']
    if argv[1] in ('navigation', 'summary'):
        bcids = [config['bcids'] for config in configs]
        if argv[1] == 'navigation':
            make_navigation(names, bcids, models, fill)
        else:
            make_summary(names, bcids, models, fill)
    else:
        bcids = []
        while (
            len(argv)>j and argv[j] and argv[j].isdigit() and
            int(argv[j]) in range(len(configs[0]['bcids']))
        ):
            bcids.append(configs[0]['bcids'][int(argv[j])])
            j += 1
        if len(bcids) == 0:
            msg = 'Specify last argument: BCID (0...{0})'.format(len(bcids)-1)
            raise RuntimeError(msg)
        if(
            len(argv)>j and argv[j] and argv[j][0] == 'v' and
            argv[j][1:].isdigit()
        ):
            version = int(argv[j][1:])
        else:
            version = 1
        for bcid in bcids:
            make_plots(names, bcid, models, fill, version=version)

if __name__ == '__main__':
    main()
