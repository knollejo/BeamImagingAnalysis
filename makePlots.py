from os import mkdir
from os.path import exists
from sys import argv

from lib.io import RootFile
from lib.plot.residual import RadialResidualPlot, ResidualPlot

wip=True

def make_plots(prefix, filename):
    mytoy = filename.find('myToy')
    toyno = filename[mytoy+5: filename.find('_', mytoy)]
    with RootFile(filename) as f:
        for step, modelname in [('temp', 'DG'), ('fit', 'SupDG')]:
            reshists = [(
                f.Get('{0}_residualHist{1}'.format(step, c)),
                f.Get('{0}_dataHist{1}'.format(step, c)),
                f.Get('{0}_modelHist{1}'.format(step, c))
            ) for c in ('X1', 'Y1', 'X2', 'Y2')]
            chisq = [
                f.get_val('{0}_chisq{1}'.format(step, c))
                / f.get_val('{0}_dof{1}'.format(step, c))
                for c in ('X1', 'Y1', 'X2', 'Y2')
            ]
            for (hres, hdat, hmod), csq in zip(reshists, chisq):
                c = hres.GetName()[-2:]
                plot = ResidualPlot(hres, fill=None, workinprogress=wip)
                pave = plot.add_pave(0.66, 0.79, 0.88, 0.88)
                pave('SupDG toy #{0}'.format(toyno))
                pave('{0} fit'.format(modelname))
                pave('#chi^{{2}}/d.o.f. = {0:.4f}'.format(csq))
                plotname = 'res_{0}_myToy{1}_{2}_{3}'.format(
                    prefix, toyno, modelname, c
                )
                plot._xtitle = 'x [a.u.]'
                plot._ytitle = 'y [a.u.]'
                plot.draw()
                plot.SaveAs('output/{0}.png'.format(plotname))
                plot.Close()
                plot = RadialResidualPlot(
                    hdat, hmod, nbins=50, maxr=8, fill=None,
                    workinprogress=wip
                )
                plot.yrange(-2.5, 2.5)
                plot.add_zeroline()
                pave = plot.add_pave(0.66, 0.79, 0.88, 0.88)
                pave('SupDG toy #{0}'.format(toyno))
                pave('{0} fit'.format(modelname))
                pave('#chi^{{2}}_{{rad}} = {0:.4f}'.format(plot.chisq()))
                plotname = 'radres_{0}_myToy{1}_{2}_{3}'.format(
                    prefix, toyno, modelname, c
                )
                plot.draw()
                plot.SaveAs('output/{0}.png'.format(plotname))
                plot.Close()

def main():
    if len(argv) < 2 or not argv[1]:
        raise RuntimeError('Specify first argument: Prefix for output files.')
    if len(argv) < 3 or not argv[2] or not exists(argv[2]):
        raise RuntimeError('Specify at least one results file.')
    if not exists('output'):
        mkdir('output')
    for filename in argv[2:]:
        if not filename or not exists(filename):
            break
        make_plots(argv[1], filename)

if __name__ == '__main__':
    main()
