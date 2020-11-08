import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks


# GLOBAL VARIABLES
# list of colors as they appear in (sized) data files
color_list = ['FL-6C', 'JOE-6C', 'TMR-6C', 'CXR-6C', 'TOM-6C', 'WEN-6C']
# dict of color names to colors to be plotted
color_dict = {'FL-6C': 'b', 'JOE-6C': 'g', 'TMR-6C': 'y', 'CXR-6C': 'r', 'WEN-6C': 'k', 'TOM-6C': 'm'}


def plot_data(data, titles):
    """"Plots all data per color for entire lists"""
    # take one off since last pocon is mainly empty?
    for i in range(len(titles)-1):
        plt.figure()
        for j in range(6):
            plt.plot(data[:, 6*i+j], label=str(color_list[j]))
        plt.legend()
        plt.title(titles[i])
        plt.show()
    return None


def plot_6C(data, titles):
    """"Plots one combined plot of all 6 colors of one hid file"""
    for j in range(len(titles)-1):
        plt.figure()
        plt.suptitle(titles[j])
        for i in range(6):
            plt.subplot(6, 1, i + 1)
            plt.plot(data[:, 6 * j + i])
            plt.title(color_list[i % 6])
        plt.show()
    return None


def plot_raw_vs_sized(data_raw, data_sized, titles):
    """Currently broken, probably won't use anymore, so not fixin't"""
    difference = len(data_raw)-len(data_sized)
    data_raw_short = data_raw[difference::, :]
    counter = 0
    for i in range(len(titles)-1):
        for j in range(6):
            plt.figure()
            plt.plot(data_raw_short[:, 6 * i + j])
            plt.plot(data_sized[:, 6 * i + j])
            title = str(titles[i]) + "_color_" + str(color_list[j])
            plt.title(title)
            plt.show()
        counter += 1
    return None


def plot_compare(name, alleles, heights, allele_dict, dye_dict, comparison):
    """uses both the analysts identified peaks and sized data \
    for comparison to plot both in one image"""
    for j in range(6):
        plt.figure()
        plt.title(str('filename: '+name+', dye: ' + str(color_list[j])))
        plt.xlim([50, 500])
        current_plot = comparison[:, j]
        plt.plot(np.linspace(0, len(current_plot)/10, len(current_plot)), comparison[:, j])
        plt.ylim([-50, max(current_plot[1000:])*1.5])
        for i in range(len(alleles)):
            # use dye_dict to plot correct color
            locus, allele = alleles[i].split("_")
            dye = dye_dict[locus]
            color = str(color_dict[dye])
            if dye == color_list[j]:
                plt.plot([allele_dict[locus][allele]], [heights[i]], str(color + "*"))  # add colour
        plt.show()
    pass


def plot_sizestd_peaks(sizestd):
    """The goal of this function was to determine the factor needed \
    for resizing the sized data to base pairs\
    Input is one size standard array, output was a plot"""
    peaks, rest = find_peaks(sizestd, distance=200)
    plt.figure()
    plt.plot(sizestd)
    print(peaks)
    plt.plot(peaks, sizestd[peaks], "*")
    plt.show()
    return None


def plot_actual(name, actual_dict, allele_dict, dye_dict, comparison):
    """uses both the theoretical actual relative peaks and \
    sized data for comparison to plot both in one image"""

    for j in range(6):
        plt.figure()
        plt.title(str('filename: '+name+', dye: ' + str(color_list[j])))
        plt.xlim([50, 500])
        plt.ylim([-50, 20000])
        current_plot = comparison[:, j]
        plt.plot(np.linspace(0, len(current_plot)/10, len(current_plot)), comparison[:, j])
        for locus, value in actual_dict.items():
            for allele, rel_perc in value.items():
                # ######MIGHT WANT TO USE FILTER FUNCTION###############TO ITERATE DICT####
                # use dye_dict to plot correct color
                dye = dye_dict[locus]
                if rel_perc != 0 and dye == color_list[j]:
                    color = color_dict[dye]
                    print(rel_perc)
                    #######RELATIVE PERCENTAGES ARE LARGER THAN 1!!
                    plt.plot([allele_dict[locus][allele]], [rel_perc*4000], str(color + "*"))  # add colour
        plt.show()
    pass
