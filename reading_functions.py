import pandas as pd
import xml.etree.ElementTree as et
from GLOBALS import *

def txt_read_data(filename):
    """ Function to read data files\
    Returns a list of sample names, colors, \
    and the data itself as matrix."""
    textfile = open(filename, "r")
    texts = textfile.read()
    texts = texts.split("\n")
    # lines 1 and 2 are not interesting
    titles = texts[2].split('\t')                       # get titles of files
    titles = [item for item in titles if item != '']    # remove empty entries after splitting
    colors = texts[3].split('\t')                       # get names of colors
    data = np.zeros((len(texts[4:]), len(colors)))
    counter = 0
    for elt in texts[4:]:
        new = np.array(elt.split('\t'))
        new[new == ''] = 0
        data[counter, :] = new
        counter += 1
    return titles, colors, data


def txt_read_data_old(filename):
    """ Outdated: Function to read data files using readline"""
    textfile = open(filename, "r")
    textfile.readline()             # first two lines are not important
    textfile.readline()
    names = textfile.readline()     # names are separated by multiple tabs
    names = names.split("\t")
    names[:] = [item for item in names if item != '']   # remove empty entries (between two \t's)
    colors = textfile.readline()
    colors = colors.split("\t")
    colors[:] = [item for item in colors if item != '']
    data = []           # fill with data
    for i in range(5000):
        line = textfile.readline()
        splitted = line.split("\t")
        splitted[:] = [int(item) for item in splitted if (item != '' and item != '\n')]
        data.append(np.array(splitted))
    data = np.array(data)
    return names, colors, data

# def xml_read_bins(filename: str) -> Locus:
def xml_read_bins(filename: str):
    """Read xml file for bins of each allele, \
    returns dictionary of horizontal values"""
    BLUE = Dye('FL-6C', 'b', 1)
    GREEN = Dye('JOE-6C', 'g', 2)
    YELLOW = Dye('TMR-6C', 'y', 3)
    RED = Dye('CXR-6C', 'r', 4)
    PURPLE = Dye('TOM-6C', 'm', 5)
    LADDER = Dye('WEN-6C', 'k', 6)

    thetreefile = et.parse(filename)
    root = thetreefile.getroot()
    locusList = []
    for locus in root[5]:
        name = locus.find('MarkerTitle').text
        temp_dict = {1: BLUE, 2: GREEN, 3: YELLOW, 4: RED, 5: LADDER, 6: PURPLE}
        dye = int(locus.find('DyeIndex').text)
        lower = float(locus.find('LowerBoundary').text)
        upper = float(locus.find('UpperBoundary').text)
        newLocus = Locus([], name, temp_dict[dye], lower, upper)
        for allele in locus.findall('Allele'):
            name = allele.get('Label')
            mid = float(allele.get('Size'))
            left = float(allele.get('Left_Binning'))
            right = float(allele.get('Right_Binning'))
            newAllele = Allele(name, mid, left, right)
            newLocus.alleles.append(newAllele)
        locusList.append(newLocus)
    return locusList


def csv_read_actual(filename, goalname, allele_peaks):
    """Read csv file of actual alleles of donors
     combines with info in word file for relative peak heights (/1)
     returns dictionary of all alleles, with nonzero values is present"""
    # goalname can be 1A2 for example

    donor_peaks = pd.read_csv(filename, dtype = str, delimiter = ";")
    donor_set, mixture_type, number_of_donors = goalname
    # check if names match, otherwise donorset is different and output makes no sense
    if filename[-5] != donor_set:
        print("Filename "+filename+" does not match "+donor_set)
        return None


    # mixture_type decides which row of matrix to use
    # number_of_donors decides which column in totals
    letter_to_number = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
    current = letter_to_number[mixture_type]
    parts = picograms[current]
    total = total_picograms[current, int(number_of_donors)-2]
    # initialize column/donor
    donor = 0
    # intialize comparison variable
    sample = donor_peaks["SampleName"][0]
    for index, row in donor_peaks.iterrows():
        if row[0] != sample:
            donor += 1
        if donor >= int(number_of_donors):
            # break if amount of donors is reached
            break
        sample = row[0]
        allele_peaks[row[1]][row[2]] += parts[donor]/total/2  # Allele 1
        allele_peaks[row[1]][row[3]] += parts[donor]/total/2  # Allele 2
    return allele_peaks


def csv_read_analyst(filename):
    """"Read csv file of identified alleles\
    returns list of alleles and corresponding peaks
    allele list is nested list per sample"""
    # I can use output of xml_read_bins to find colors of alleles
    # there may be more than one sample in one file
    results = pd.read_csv(filename)
    name = results['Sample Name'][0]    # to start iteration
    allele_lists = []                   # initialize big lists
    height_lists = []
    allele_list = []                    # initialize small lists
    height_list = []
    for index, row in results.iterrows():
        # iterate over all rows, because each row contains
        # the peaks for one locus
        if name != row[0]:                      # then start new sample
            allele_lists.append(allele_list)    # store current sample data
            height_lists.append(height_list)
            allele_list = []                    # empty lists
            height_list = []
        name = row[0]                           # then set name to current sample name
        for i in range(2, 12):
            # go over the 10 possible locations of peak identification
            if str(row[i]) == row[i]:
                # append value only if non-empty
                # empty entries are converted to (float-type) NaN's by pandas
                # so str(row[i]) == row[i] filters out empty entries
                allele_list.append(row[1]+"_"+row[i])
                # heights are 10 indices further than
                # their corresponding allele names
                height_list.append(row[i+10])
    allele_lists.append(allele_list)
    height_lists.append(height_list)
    return allele_lists, height_lists
