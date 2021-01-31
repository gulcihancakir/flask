import base64
import gc
import io
from collections import defaultdict
from io import BytesIO
from pathlib import Path
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import wfdb
from keras.utils import to_categorical
from matplotlib.ticker import MaxNLocator
from neurodsp.utils import create_times
from numpy import argmax
from sklearn import preprocessing
from sklearn.metrics import confusion_matrix
from tensorflow import keras

global figure
global figure2
global figure3

# read_file =[]
# read_file2=[]

global read_file
global read_file2

def predict_and_plot_sstaging(data_path, data_file):
    print("I am here",os.getcwd())
    model = keras.models.load_model('model')

    data_path = Path(data_path)
    record = data_file

    annotation_dict = defaultdict(lambda: 5, {
        '1': 0,
        '2': 1,
        '3': 2,
        '4': 2,
        'R': 3
    })

    classes = defaultdict(lambda: '6', {
        '1000': '1',
        '0100': '2',
        '0010': '3',
        '0001': '4',
        '0000': '5'
    })

    class_count = defaultdict(lambda: 0, {
        '1000': 0,
        '0100': 0,
        '0010': 0,
        '0001': 0,
        '0000': 0
    })

    annsamp = wfdb.rdann(str(data_path / record),
                         extension='st', summarize_labels=True)

    signal = wfdb.rdrecord(str(data_path / record), channels=[2])
    physical_signal = signal.p_signal
    physical_signal = preprocessing.scale(physical_signal)

    number_annotations = len(annsamp.aux_note)

    starting_index = int((len(physical_signal) / 7500) -
                         number_annotations)*7500
    physical_signal = physical_signal[starting_index:]
    inputs = np.split(physical_signal, number_annotations)
    annots = list()
    target = [[0]*4 for _ in range(number_annotations)]

    for annotation_index in range(number_annotations):

        labels = annsamp.aux_note[annotation_index].split(' ')
        labels = [_l.strip('\x00') if type(_l) == str else str(_l)
                  for _l in labels]
        for label in labels:
            if annotation_dict[label] != 5:
                target[annotation_index][annotation_dict[label]] = 1

        event_class = ''.join([str(v) for v in target[annotation_index]])
        event_class = classes[event_class]

        annots.append(event_class)
    annots_c = to_categorical(annots)
    inputs = np.array(inputs)
    y_pred = model.predict(inputs)

    y_pred_c = y_pred.argmax(axis=1)

    y_pred_c = y_pred_c.tolist()

    S1 = 0
    S2 = 0
    S3 = 0
    R = 0
    W = 0
    for i in y_pred_c:
        if i == 1:
            S1 += 1
        elif i == 2:
            S2 += 1
        elif i == 3:
            S3 += 1
        elif i == 4:
            R += 1
        else:
            W += 1
    annots = np.array(annots).astype(np.int)

    annotation_dict1 = defaultdict(
        lambda: 5, {
            'S1': 1,
            'S2': 2,
            'S3': 3,
            'R': 4,
            'W': 5
        }
    )

    matplotlib.rcParams['agg.path.chunksize'] = 10000

    fig, ax = plt.subplots(figsize=(50, 20))
    plt.rcParams["axes.linewidth"] = 3
    plt.xticks(fontsize=50)
    plt.yticks(fontsize=50)
    plt.title('Hypno Çizimi',fontsize=50)

    plt.tick_params(axis='both', pad=30)
    plt.yticks(range(1, len(annotation_dict1.keys())+1),
               annotation_dict1.keys())

    plt.plot(y_pred_c, color='blue', linewidth=5)

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    global figure
    figure = base64.b64encode(figfile.getvalue()).decode('ascii')
    plt.savefig(record+"_hypno.png", format='png')

    plt.clf()
    plt.cla()
    gc.collect()

    fs = 250

    times = create_times(len(physical_signal)/fs, fs)

    plt.rcParams['axes.linewidth'] = 5
    plt.rcParams["figure.figsize"] = (40, 50)
    plt.title('Epoch Çizimi',fontsize=50)

    plt.tick_params(axis='both', pad=45)

    plt.xticks(fontsize=50)
    plt.yticks(fontsize=50)

    # plt.xlabel('time (s)', fontsize=100, labelpad=50)
    # plt.ylabel('Voltage (mV)', fontsize=100, labelpad=50)

    plt.gca().yaxis.set_major_locator(MaxNLocator(prune='lower'))

    plt.plot(times, physical_signal, linewidth=6)

    figfile1 = BytesIO()
    plt.savefig(figfile1, format='png')
    figfile1.seek(0)
    global figure2
    figure2 = base64.b64encode(figfile1.getvalue()).decode('ascii')
    plt.savefig(record + "_epochs.png", format='png')

    plt.clf()
    plt.cla()
    gc.collect()

    total = len(annots)
    eq = 0
    for i in range(len(annots)):
        if annots[i] == y_pred_c[i]:
            eq += 1

    f = open(data_file + ".txt", "w")
    f.write("Toplam uyku süresi:" + str(total/2) + " dakika\n")
    f.write("S1:" + str(S1) + " dakika\n")
    f.write("S2:" + str(S2) + " dakika\n")
    f.write("S3:" + str(S3) + " dakika\n")
    f.write("R:" + str(R) + " dakika\n")
    f.write("W:" + str(W) + " dakika\n")
    f.close()
    global read_file
    read = open(data_file +".txt")
    read_file=read.readlines()
       

    
    ss_labels = ["S1", "S2", "S3", "R", "W"]
    ss_values = [S1, S2, S3, R, W]
    ss_explode = (0, 0, 0.1, 0, 0)

    fig1, ax1 = plt.subplots(figsize=(40, 30))

    ax1.pie(ss_values, explode=ss_explode, labels=ss_labels, autopct='%1.1f%%',
            shadow=False, startangle=90, textprops={'fontsize': 60})
    ax1.axis('equal')
    figfile2 = BytesIO()
    plt.savefig(figfile2, format='png')
    figfile2.seek(0)
    global figure3
    figure3 = base64.b64encode(figfile2.getvalue()).decode('ascii')
    plt.savefig(record + "_pie.png", format='png')

    plt.clf()
    plt.cla()
    gc.collect()


def predict_and_plot_sdisease(data_path, data_file):

    model = keras.models.load_model('model2')

    data_path = Path(data_path)
    record = data_file

    ca = 0
    oa = 0
    ha = 0
    na = 0

    annsamp = wfdb.rdann(str(data_path / record),
                         extension='st', summarize_labels=True)

    signal = wfdb.rdrecord(str(data_path / record), channels=[2])
    physical_signal = signal.p_signal
    physical_signal = preprocessing.scale(physical_signal)

    number_annotations = len(annsamp.aux_note)

    starting_index = int((len(physical_signal) / 7500) -
                         number_annotations)*7500
    physical_signal = physical_signal[starting_index:]
    inputs = np.split(physical_signal, number_annotations)

    annots = list()

    for annotation_index in range(number_annotations):

        labels = annsamp.aux_note[annotation_index].split(' ')
        labels = [_l.strip('\x00') if type(_l) == str else str(_l)
                  for _l in labels]

        if "CA" in labels or "CAA" in labels:
            annots.append("0")
            ca += 1
        elif "X" in labels or "OA" in labels:
            annots.append("1")
            oa += 1
        elif "H" in labels or "HA" in labels:
            annots.append("2")
            ha += 1
        else:
            annots.append("3")
            na += 1

    annots_c = to_categorical(annots)

    inputs = np.array(inputs)
    y_pred = model.predict(inputs)

    y_pred_c = y_pred.argmax(axis=1)

    y_pred_c = y_pred_c.tolist()

    annots = np.array(annots).astype(np.int)

    annotation_dict1 = defaultdict(
        lambda: 3, {
            'CA': 0,
            'OA': 1,
            'HA': 2,
            'NA': 3,
        }
    )

    total = len(annots)
    eq = 0
    for i in range(len(annots)):
        if annots[i] == y_pred_c[i]:
            eq += 1
    sd_CA = 0
    sd_OA = 0
    sd_HA = 0
    sd_NA = 0

    for i in y_pred_c:
        if i == 0:
            sd_CA += 1
        elif i == 1:
            sd_OA += 1
        elif i == 2:
            sd_HA = 1
        else:
            sd_NA = 1

    sd_AHI = round((sd_CA+sd_OA+sd_HA)/(total/(2*60)), 2)
    sd_AI = round((sd_CA+sd_OA)/(total/(2*60)), 2)

    f = open(data_file + "_d.txt", "w")
    f.write("CA:" + str(sd_CA) + "\n")
    f.write("OSA:" + str(sd_OA) + "\n")
    f.write("HA:" + str(sd_HA) + "\n")
    f.write("AHI:" + str(sd_AHI) + "\n")
    f.write("AI:" + str(sd_AI) + "\n")
    if sd_AHI > 5 and sd_AI <= 20:
        f.write("Hafif Apnea olabilirsiniz. Doktorunuza başvurun.\n")
    elif sd_AHI > 20 and sd_AI <= 40:
        f.write("Orta Apnea olabilirsiniz. Doktorunuza başvurun.\n")
    elif sd_AHI > 40:
        f.write("Ağır Apnea olabilirsiniz. Doktorunuza başvurun.\n")
    f.close()
    global read_file2
    read2 = open(data_file +"_d.txt")
    read_file2=read2.readlines()
# record_list = wfdb.get_record_list('slpdb')
# for r in record_list:
#     predict_and_plot("temp", r)
#     print(r)
