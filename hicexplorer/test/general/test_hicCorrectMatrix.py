import warnings
warnings.simplefilter(action="ignore", category=RuntimeWarning)
warnings.simplefilter(action="ignore", category=PendingDeprecationWarning)
from hicexplorer import hicCorrectMatrix
from hicmatrix import HiCMatrix as hm
from tempfile import NamedTemporaryFile
import os
import numpy.testing as nt
from matplotlib.testing.compare import compare_images


ROOT = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "test_data/")


def test_correct_matrix_ICE():
    outfile = NamedTemporaryFile(suffix='.ICE.h5', delete=False)
    outfile.close()

    args = "correct --matrix {} --correctionMethod ICE --chromosomes "\
           "chrUextra chr3LHet --iterNum 500  --outFileName {} "\
           "--filterThreshold -1.5 5.0".format(ROOT + "small_test_matrix.h5",
                                               outfile.name).split()
    hicCorrectMatrix.main(args)

    test = hm.hiCMatrix(
        ROOT + "hicCorrectMatrix/small_test_matrix_ICEcorrected_chrUextra_chr3LHet.h5")
    new = hm.hiCMatrix(outfile.name)
    nt.assert_equal(test.matrix.data, new.matrix.data)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)

    os.unlink(outfile.name)


def test_correct_matrix_KR_H5():
    outfile = NamedTemporaryFile(suffix='.KR.h5', delete=False)
    outfile.close()

    args = "correct --matrix {} --correctionMethod KR --chromosomes "\
           "chrUextra chr3LHet --outFileName {} ".format(ROOT + "small_"
                                                         "test_matrix.h5",
                                                         outfile.name).split()
    hicCorrectMatrix.main(args)

    test = hm.hiCMatrix(
        ROOT + "hicCorrectMatrix/small_test_matrix_KRcorrected_chrUextra_chr3LHet.h5")
    new = hm.hiCMatrix(outfile.name)
    nt.assert_almost_equal(test.matrix.data, new.matrix.data, decimal=5)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)

    os.unlink(outfile.name)


def test_correct_matrix_KR_cool():
    outfile = NamedTemporaryFile(suffix='_KR.cool', delete=False)
    outfile.close()

    args = "correct --matrix {} --correctionMethod KR "\
           "--outFileName {} ".format(ROOT + "small_test_matrix.cool",
                                      outfile.name).split()
    hicCorrectMatrix.main(args)

    test = hm.hiCMatrix(ROOT + "hicCorrectMatrix/kr_full.cool")
    new = hm.hiCMatrix(outfile.name)
    nt.assert_almost_equal(test.matrix.data, new.matrix.data, decimal=5)
    # nt.assert_almost_equal(test.correction_factors, new.correction_factors, decimal=5)

    nt.assert_equal(test.cut_intervals, new.cut_intervals)

    os.unlink(outfile.name)


def test_correct_matrix_KR_partial_cool():
    outfile = NamedTemporaryFile(suffix='_KR.cool', delete=False)
    outfile.close()

    args = "correct --matrix {} --correctionMethod KR --chromosomes "\
           "chrUextra chr3LHet  --outFileName {} ".format(ROOT + "small_test_matrix.cool",
                                                          outfile.name).split()
    hicCorrectMatrix.main(args)

    test = hm.hiCMatrix(ROOT + "hicCorrectMatrix/kr_partial.cool")
    new = hm.hiCMatrix(outfile.name)
    nt.assert_almost_equal(test.matrix.data, new.matrix.data, decimal=5)
    nt.assert_equal(test.cut_intervals, new.cut_intervals)

    os.unlink(outfile.name)


def test_correct_matrix_diagnostic_plot():
    outfile = NamedTemporaryFile(
        suffix='.png', prefix='hicexplorer_test', delete=False)

    args = "diagnostic_plot --matrix {} --chromosomes chrUextra chr3LHet " \
        " --plotName {}".format(ROOT + "small_test_matrix.h5",
                                outfile.name).split()
    hicCorrectMatrix.main(args)

    res = compare_images(ROOT + "hicCorrectMatrix" +
                         '/diagnostic_plot.png', outfile.name, tol=40)
    assert res is None, res
    os.remove(outfile.name)
