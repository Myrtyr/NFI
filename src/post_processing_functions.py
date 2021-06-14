from src.classes import *
import numpy as np
from src import reading_functions as rf
from collections import Counter
import pandas as pd


def pixels_to_peaks(unet_output: np.ndarray, threshold: float, left_offset: int):
    result = unet_output > threshold
    allele_list = []
    for dye in range(result.shape[1]-1):
        # -1 so we don't iterate over size std
        current = result[:, dye]
        index_start = 0
        while index_start != len(current) - 1:
            alleles = {}
            # find next True
            while current[index_start] == False and index_start < len(current) - 1:
                index_start += 1
            index_end = index_start
            # find corresponding end True
            while current[index_end] == True and index_end < len(current) - 1:
                allele = allele_map[index_end+left_offset, dye]
                prob = unet_output[index_end,dye]
                if allele in alleles:
                    alleles[allele] *= prob
                else:
                    alleles[allele] = prob
                index_end += 1

            if index_end - index_start < 5:
                index_start = index_end
            else:
                # TODO: add a peak splitter of some kind?
                # print(unet_output[index_start:index_end, dye])
                # possible_alleles = allele_map[index_start+left_offset:index_end+left_offset, dye]
                # print(possible_alleles)
                alleles[None] = 0
                decision = max(alleles.items(), key=lambda x: x[1])
                allele_list.append(decision[0])
                # TODO: may need probabilities later
                index_start = index_end
    return allele_list


def check_correct_alleles_first(alleles_present: List, unet_output: np.ndarray, left_offset: int):
    unet_output_augmented = unet_output.copy()
    alleles_detected = []
    for locus_allele in alleles_present:
        locus_name, allele_name = locus_allele.split("_")
        allele = locus_dict[locus_name].alleles[allele_name]
        dye_index = allele.dye.plot_index - 1
        index_left = round((allele.mid-allele.left)*10) - left_offset
        index_right = round((allele.mid+allele.right)*10) - left_offset
        prob = 1
        for subprob in unet_output[index_left:index_right, dye_index]:
            prob *= subprob
        if prob > 0.5:
            alleles_detected.append(locus_allele)
            unet_output_augmented[index_left-15:index_right+15, dye_index] = 0
    return alleles_detected, unet_output_augmented

# def peak_metric(unet_output, left_offset):
#     peak_list = print_all_peaks("1A2")
#     for key_locus in locus_dict:
#         locus = locus_dict[key_locus]  # get locus class object
#         alleles = locus.alleles
#         for key_allele in alleles:
#             allele = alleles[key_allele]
#             start = -left_offset + round(10*(allele.mid-allele.left))
#             stop = -left_offset + round(10*(allele.mid+allele.right))
#             kansop = np.average(unet_output[start:stop,locus.index])
#             if kansop > 0.5:
#                 print(key_locus, key_allele, kansop, (str(key_locus+"_"+key_allele) in peak_list))
#     # go over all alleles
#     # check probability of there being a peak
#     # either do or don't call peak
#     # I am afraid there will be too many positively identified bins
#     pass


def list_all_peaks(mix_name: str):
    person_mix = rf.make_person_mixture(mix_name)
    peak_list = []
    # iterate through persons in mix
    for person in person_mix.persons:
        # iterate over their alleles
        for locus_allele in person.alleles:
            if locus_allele not in peak_list:
                peak_list.append(locus_allele)
    return peak_list


def F1_score(alleles_present: List, alleles_detected: List):
    """Calculates F1-score of result of U-net"""
    positives = set(alleles_detected)
    truth = set(alleles_present)
    TP = len(positives & truth)
    FP = len(positives - truth)
    FN = len(truth - positives)
    precision = TP/(TP+FP)
    recall = TP/(TP+FN)
    return 2*(precision*recall)/(precision+recall)


def result_dataframe(score_list, name_list):
    dict = {"name": name_list, "score": score_list}
    df = pd.DataFrame(dict)
    df.to_csv("scores_network.csv")
    return df


