import math
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt


def preprocessamento(x, ts, fs, fsDown, filtLowpass, filtHighpass, k):
    # Linear interpolation
    dataBlock = linear_interpolation(x)

    # Outlier removal
    dataBlock = mean_outlier_removal(dataBlock, k=k)

    # Linear interpolation
    dataBlock = linear_interpolation(dataBlock)

    # Downsample
    dataBlock, ts1, fs1 = downsample(dataBlock, ts, fs, fsDown)

    # Detrend
    dataBlock -= np.nanmean(dataBlock)

    # HP filter
    dataBlock = highpassFilter(dataBlock, fs1, filtLowpass, 501)

    # LP filter
    dataBlock = lowpassFilter(dataBlock, fs1, filtHighpass, 500)

    return dataBlock, ts1, fs1


def downsample(x, ts, fs, fsDown):
	ratio = math.floor(fs / fsDown)
	ts1 = ts * ratio
	fs1 = math.floor(1 / ts1)
	signalDown = signal.decimate(x, ratio, zero_phase=True)
	return signalDown, ts1, fs1


def lowpassFilter(x, fs, cutoff, order):
	# Calculates filter coefficients
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	coef = signal.firwin(order, normal_cutoff, window='hanning', pass_zero="lowpass")
	signalFilt = signal.lfilter(coef, 1, x)
	return signalFilt


def highpassFilter(x, fs, cutoff, order):
	# Calculates filter coefficients
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	coef = signal.firwin(order, normal_cutoff, window='hanning', pass_zero="highpass")
	signalFilt = signal.lfilter(coef, 1, x)
	return signalFilt


def nan_indexes(nan_array):

	# Get location of nan and not nan values in array as True and False
	nanIndex = np.isnan(nan_array)

	# Get array containing differance values to find consecutive nan numbers
	# Checks for the ocurrance of run of 1's
	nanIndex = np.concatenate(([0], np.equal(nanIndex, True).view(np.int8), [0]))
	nanIndex = np.abs(np.diff(nanIndex))
	nanIndex = np.where(nanIndex == 1)[0]

	return nanIndex


def outlier_removal(outlierArray, k=3):

	# Sets kernel size to be right size and odd
	if len(outlierArray) < 100:
		kernelSize = len(outlierArray) // 10
		if kernelSize % 2 == 0:
			kernelSize += 1
	else:
		kernelSize = 25

	# Calculates median filter and standard deviation
	freqMedianFilter = signal.medfilt(outlierArray, kernel_size=kernelSize)
	freqStdLimit = np.nanstd(outlierArray) * k

	# Saves lower and higher filter limits
	lowerLimit = freqMedianFilter - freqStdLimit
	higherLimit = freqMedianFilter + freqStdLimit

	# Compares limits to data
	freqLowerMask = np.less_equal(outlierArray, lowerLimit)
	freqHigherMask = np.greater_equal(outlierArray, higherLimit)
	freqMask = np.logical_or(freqLowerMask, freqHigherMask)

	# Removes outliers if there's any
	if True in freqMask:
		outlierLocation = np.where(freqMask == True)
		for i in outlierLocation[0]:
			outlierArray[i] = np.nan

	return outlierArray

########################### NIGERIA EXPERIMENT ########################### 

def mean_outlier_removal(outlierArray, k=3):

	# Calculates mean and standard deviation
	freqMean = np.nanmean(outlierArray)
	freqStdLimit = np.nanstd(outlierArray) * k

	# Saves lower and higher filter limits
	lowerLimit = freqMean - freqStdLimit
	higherLimit = freqMean + freqStdLimit

	# Compares limits to data
	freqLowerMask = np.less_equal(outlierArray, lowerLimit)
	freqHigherMask = np.greater_equal(outlierArray, higherLimit)
	freqMask = np.logical_or(freqLowerMask, freqHigherMask)

	# Removes outliers if there's any
	if True in freqMask:
		outlierLocation = np.where(freqMask == True)
		for i in outlierLocation[0]:
			outlierArray[i] = np.nan

	return outlierArray


def find_nan_run(inputArray, run_max=10):
	# Gets array of position of nan values
	nanIndex = nan_indexes(inputArray)

	# Checks indexes of run ocurrances and compare to threshold
	runIndex = 0

	while runIndex < len(nanIndex):
		runSize = nanIndex[runIndex + 1] - nanIndex[runIndex]
		if runSize >= run_max:
			#raise NameError(f"Sequence of {runSize} missing values. That's too many!")
			raise NameError('Muitos dados faltantes em seguida')
		runIndex += 2

	return False


def linear_interpolation(inputArray):
	# Get location of nan and not nan values in array as True and False
	nanLocation = np.isnan(inputArray)
	numberLocation = np.logical_not(nanLocation)

	# Linear interpolation at nan indexes
	inputArray[nanLocation] = np.interp(nanLocation.nonzero()[0],
										numberLocation.nonzero()[0],
										inputArray[~nanLocation])

	return inputArray


def correct_length(data, batch):
    # Corrects length of frequency list
    if len(data) % batch != 0:
        exactMult = np.floor(len(data) / batch)
        exactLen = int(exactMult * batch)
        lenDiff = len(data) - exactLen
        data = data[:-lenDiff]
    return data


def butterworth(data, cutoff, order, fs, kind="lowpass"):
    # highpass filter
    nyq = fs * 0.5

    cutoff = cutoff / nyq

    sos = signal.butter(order, cutoff, btype=kind, output="sos")

    filtrada = signal.sosfilt(sos, data)

    return filtrada


def nan_to_none(x):
	# Replace NaN with None for JSON
	x = x.tolist()
	for i in range(0, len(x)):
		if str(x[i]) == "nan":
			x[i] = None

		# for y in range(0, len(x[i])):
		# 	if str(x[i][y]) == "nan":
		# 		x[i][y] = None

	return x