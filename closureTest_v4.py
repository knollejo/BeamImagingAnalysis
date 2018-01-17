from os.path import exists
from sys import argv

from closureTest_v2 import do_closureTest
from lib.shape.dg import DoubleGaussFit
from lib.shape.tg import SuperDoubleGaussFit, SuperDoubleGaussToy

def main():
    toymodel = SuperDoubleGaussToy()
    toymodel.factor = 100.0
    fitmodel = SuperDoubleGaussFit()
    fitmodel.factor = 100.0
    tempmodel = DoubleGaussFit()
    tempmodel.factor = 100.0
    if len(argv) < 2 or not argv[1]:
        raise RuntimeError('Specify 1st argument: Output name.')
    name = argv[1]
    if len(argv) < 3 or not argv[2]:
        raise RuntimeError('Specify 2nd argument: Vertex resolution.')
    try:
        vtxres = float(argv[2])
    except ValueError:
        raise RuntimeError('Specify 2nd argument: Vertex resolution.')
    if len(argv) < 4 or not argv[3] or not exists(argv[3]):
        raise RuntimeError('Specify 3rd argument: JSON config file.')
    jsonfile = argv[3]
    if len(argv) >= 5 and argv[4]:
        try:
            n = int(argv[4])
        except ValueError:
            raise RuntimeError('Optional 4th argument: Number of iterations.')
    else:
        n = 1

    def ateachtoy(toymodel, rand, json):
        toymodel.load_json(json, rand)
        return toymodel.overlap_func()
    eachtoy = (lambda j: lambda toy, rand: ateachtoy(toy, rand, j))(jsonfile)

    do_closureTest(
        name, toymodel, tempmodel, fitmodel, vtxres, n=n, eachtoy=eachtoy
    )

if __name__ == '__main__':
    main()
