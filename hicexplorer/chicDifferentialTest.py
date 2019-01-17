import argparse
import sys
import numpy as np
import hicmatrix.HiCMatrix as hm
from hicexplorer import utilities

from hicexplorer._version import __version__
from .lib import Viewpoint

from scipy.stats import chi2_contingency
from scipy.stats import chi2

import os

import math
import logging
log = logging.getLogger(__name__)


def parse_arguments(args=None):
    parser = argparse.ArgumentParser(add_help=False,
                                     description='Test per line if two samples are differential expressed via chi2 contingency test.')

    parserRequired = parser.add_argument_group('Required arguments')

    parserRequired.add_argument('--interactionFile', '-if',
                                help='path to the interaction files which should be used for differential test.',
                                required=True,
                                nargs=2)

    parserRequired.add_argument('--alpha', '-a',
                           help='Accept all samples to significance level alpha',
                           type=float,
                           default=0.05,
                           required=True)
	parserRequired.add_argument('--outFileName', '-o',
							help='File name to save the test results',
							required=True)
    parserOpt = parser.add_argument_group('Optional arguments')
	parserOpt.add_argument('--useData',
                           help='Type of data used for testing: raw interactions, relative interactions, rbz-score',
                           choices=['raw', 'relative', 'rbz'],
                           default='raw')
    parserOpt.add_argument("--help", "-h", action="help", help="show this help message and exit")

    parserOpt.add_argument('--version', action='version',
                           version='%(prog)s {}'.format(__version__))
    return parser



def readInteractionFile(pInteractionFile, pUseData):

	line_content = []
	data = []
	
	if pUseData == 'raw':
		data_selector_viewpoint = 9
		data_selector_target =  12
	elif pUseData == 'relative':
		data_selector_viewpoint = 7
		data_selector_target =  10
	elif pUseData == 'rbz':
		data_selector_viewpoint = 8
		data_selector_target =  11
    with open(pOutFileName, 'w') as file:
		header_significance_level = file.readline()
		header = file.readline()

		for line in file.readlines():
			_line = line.strip().split('\t')			
			line_content.append(_line)
			data.append([float(_line[data_selector_viewpoint]), float(_line[data_selector_target])])
			
	return header_significance_level, header, line_content, data
    

def chisquare_test(pDataFile1, pDataFile2, pAlpha):
    # pair of accepted/unaccepted and pvalue
    # True is rejection of H0
    # False acceptance of H0
    test_result = []    
    # Find the critical value for alpha confidence level
    critical_value = stats.chi2.ppf(q = 1 - pAlpha, df = 1) 
    for group1, group2 in zip(pDataFile1, pDataFile2):
        chi2, p_value, dof, ex = chi2_contingency([group1,group2], correction=False)
        if chi2 >= critical_value:
			test_result.append((True, p_value))
		else:
			test_result.append((False, p_value))

	return test_result

def writeResult(pOutFileName, pData, pRejected, pHeaderOld, pHeaderNew):
	
    with open(pOutFileName, 'w') as file:
		file.write('# ' + pRejected + ' file for viewpoints: ' + pHeaderNew + '\n')
		file.write(pHeaderOld + '\t' pHeaderOld + '\tp-value')

		for data in pData:
			file.write(data[0] + '\t' + data[1] + '\t' + format(data[2], '10.5f'))


def main(args=None):
    args = parse_arguments().parse_args(args)
    # log.debug('muh')
    
    header_significance_level1, header1, line_content1, data1 = readInteractionFile(args.interactionFile[0], args.useData)
    header_significance_level2, header2, line_content2, data2 = readInteractionFile(args.interactionFile[1], args.useData)

	test_result = chisquare_test(data1, data2, args.alpha)

	rejected_h0 = []
	
	non_rejected_h0 = []
	for i, result in enumerate(test_result):
		if result[0]:
			rejected_h0.append([line_content1[i], line_content2[i], result[1]])
		else:
			non_rejected_h0.append([line_content1[i], line_content2[i], result[1]])


	header_new = args.interactionFile[0]
	header_new += ' '
	header_new += args.interactionFile[1]

	rejected_h0_str = 'Rejected H0 data'

	non_rejected_h0_str = 'Accepted H0 data'

	writeResult('outname_h0.bed', rejected_h0, rejected_h0_str, header1, )
	writeResult('outname_h1.bed', non_rejected_h0, non_rejected_h0_str, header2, )