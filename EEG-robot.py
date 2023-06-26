import tensorflow as tf
import pylsl
import numpy as np
from pylsl import StreamInlet, resolve_stream # first resolve an EEG # stream on the lab network
from nltk import flatten
from spectral_analysis import dsp

import socket     # Wifi Xbee is using raw feed, hence a raw socket protocol

connect_to_xbee = True

if connect_to_xbee == True:
    # Network initiation
    ip='192.168.178.215'               #Enter IP of your Xbee
    p=9750                             #Enter the port number for your Xbee
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  #Initialize socket object
    s.connect((ip,p))                         #Connect to the Xbee
    print("Connected to: ", ip, " ", p)


confidence_threshold = 0.60                                      # default in Edge Impulse is 0.6


def move(dir):
    if dir == "L":
        control = "0"
    elif dir == "R":
        control = "1"
    elif dir == "-":
        control = "2"
    
    # print(control)
    if connect_to_xbee == True:
        s.send(control.encode())
        s.send(dir.encode())


def features(raw_data):

    implementation_version = 4 # 4 is latest versions
    draw_graphs = False # For testing from script, disable graphing to improve speed

    # raw_data = ""
    # raw_data = np.array([float(item.strip()) for item in raw_data.split(',')])
    raw_data = np.array(raw_data)
    # print("Amount of features: ", len(raw_data))
    # print(raw_data)

    axes = ['TP9', 'AF7', 'AF8', 'TP10'] # Axes names.  Can be any labels, but the length naturally must match the number of channels in raw data
    sampling_freq = 250 # Sampling frequency of the data.  Ignored for images

    # Below here are parameters that are specific to the spectral analysis DSP block. These are set to the defaults
    scale_axes = 1 # Scale your data if desired
    input_decimation_ratio = 1 # Decimation ratio.  See /spectral_analysis/paramters.json:31 for valid ratios
    filter_type = 'none' # Filter type.  String : low, high, or none
    filter_cutoff = 0 # Cutoff frequency if filtering is chosen.  Ignored if filter_type is 'none'
    filter_order = 0 # Filter order.  Ignored if filter_type is 'none'.  2, 4, 6, or 8 is valid otherwise
    analysis_type = 'FFT' # Analysis type.  String : FFT, wavelet

    # The following parameters only apply to FFT analysis type.  Even if you choose wavelet analysis, these parameters still need dummy values
    fft_length = 64 # Size of FFT to perform.  Should be power of 2 >-= 16 and <= 4096

    # Deprecated parameters.  Only applies to version 1, maintained for backwards compatibility
    spectral_peaks_count = 0 # Deprecated parameter.  Only applies to version 1, maintained for backwards compatibility
    spectral_peaks_threshold = 0 # Deprecated parameter.  Only applies to version 1, maintained for backwards compatibility
    spectral_power_edges = "0" # Deprecated parameter.  Only applies to version 1, maintained for backwards compatibility

    # Current FFT parameters
    do_log = True # Take the log of the spectral powers from the FFT frames
    do_fft_overlap = True # Overlap FFT frames by 50%.  If false, no overlap
    extra_low_freq = False # This will decimate the input window by 10 and perform another FFT on the decimated window.
                        # This is useful to extract low frequency data.  The features will be appended to the normal FFT features

    # These parameters only apply to Wavelet analysis type.  Even if you choose FFT analysis, these parameters still need dummy values
    wavelet_level = 2 # Level of wavelet decomposition
    wavelet = "rbio3.1" # Wavelet kernel to use

    output = dsp.generate_features(implementation_version, draw_graphs, raw_data, axes, sampling_freq, scale_axes, input_decimation_ratio,
                        filter_type, filter_cutoff, filter_order, analysis_type, fft_length, spectral_peaks_count,
                        spectral_peaks_threshold, spectral_power_edges, do_log, do_fft_overlap,
                        wavelet_level, wavelet, extra_low_freq)

    # Return dictionary, as defined in code
        # return {
        #     'features': List of output features
        #     'graphs': Dictionary of graphs
        #     'labels': Names of the features
        #     'fft_used': Array showing which FFT sizes were used.  Helpful for optimzing embedded DSP code
        #     'output_config': information useful for correctly configuring the learn block in Studio
        # }

    # print (output)
    # print(f'Processed features are: ')
    # print('Feature name, value')
    # idx = 0
    # for axis in axes:
    # #    print(f'\nFeatures for axis: {axis}')
    #     for label in output['labels']:
    # #        print(f'{label: <40}: {output["features"][idx]}')
    #         print(f'{output["features"][idx]}')
    #         idx += 1
    # print (output["features"])
    return output["features"]


# Load the TensorFlow Lite model
model_path = "ei-muse-eeg-robot-blinks-classifier-tensorflow-lite-float32-model (1).lite"
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print()
print(input_details)
print()
print(output_details)

# Connect to the LSL stream
streams = resolve_stream('type', 'EEG') # create a new inlet to read # from the stream
inlet = pylsl.stream_inlet(streams[0])

nr_samples = 1

while True:

    back_nr = left_nr = right_nr = blink_nr = uncertain_nr = 0

    for iter in range (nr_samples):
        all_samples = []
        for i in range (2000 // 4):
            sample, timestamp = inlet.pull_sample()
            sample.pop()
            all_samples.append(sample)

        all_samples = flatten(all_samples)                                          # ...and flattening them
        all_samples = features(all_samples)
        # print(all_samples)

        input_samples = np.array(all_samples, dtype=np.float32)
        input_samples = np.expand_dims(input_samples, axis=0)

        interpreter.set_tensor(input_details[0]['index'], input_samples)            # input_details[0]['index'] = the index which accepts the input
        interpreter.invoke()                                                        # run the inference

        output_data = interpreter.get_tensor(output_details[0]['index'])            # output_details[0]['index'] = the index which provides the input
        # print(output_data)
        # print(f"Inference output: {output_data[0][1]:.3f} {output_data[0][0]:.3f} {output_data[0][2]:.3f}")


        background  = output_data[0][0]
        deep        = output_data[0][1]
        shallow     = output_data[0][2]

        if shallow >= confidence_threshold:
            move("L")
        elif deep >= confidence_threshold:
            move("R")
        else:
            move("-")


        # background  = output_data[0][0]
        # blink       = output_data[0][1]
        # left        = output_data[0][2]
        # right       = output_data[0][3]

        # if left >= confidence_threshold:
        #     left_nr += 1
        # elif right >= confidence_threshold:
        #     right_nr += 1
        # elif background >= confidence_threshold:
        #     back_nr += 1
        # elif blink >= confidence_threshold:
        #     blink_nr += 1
        # else:
        #     uncertain_nr += 1
    
#    print(f"L: {left_nr:.4f}  B: {back_nr:.4f}  R: {right_nr:.4f}  Uncertain: {uncertain_nr:.4f}   Sum: {left_nr+right_nr+back_nr:.1f}")       
#    print(f"Deep: {deep:.8f}  Background: {background:.8f}  Shallow: {shallow:.8f}")       
    print(f"Left: {shallow:.8f}  Background: {background:.8f}  Right: {deep:.8f}")       
 