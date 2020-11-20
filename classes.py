from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np


@dataclass
class Dye:
    """ Class for fluorescent dyes of genetic analyzer."""
    name: str           # example: 'FL-6C'
    plot_color: str     # example: 'b'
    plot_index: int     # index of which of 6 subplots when all dyes\
                        # are plotted in the same image


@dataclass
class Allele:
    """Class for each allele that can be identified."""
    name: str       # example: 'X' or '17'
    mid: float      # horizontal position, example: '87.32'
    left: float     # left side of bin from mid (0.4 or 0.5)
    right: float    # right side of bin from mid (0.4 or 0.5)
    # locus: "Locus"    # note: left_binning is not always equal to right_binning


@dataclass
class Locus:
    """Class for locus, stores Alleles per locus in dict."""
    alleles: Dict[str, Allele]      # example of entry: '18': Allele()
    name: str                       # example: 'AMEL'
    dye: Dye                        #
    lower: float                    # lower boundary of marker
    upper: float                    # upper boundary of marker


@dataclass
class Peak:
    """Class for an identified or expected allele peak.
    Has everything needed for plotting."""
    name: str       # Using "locus_allele" for now because it makes dict access easy
    x: float        # denk na over eenheid/naam
    height: float   # height of peak
    dye: Dye        # dye of peak
    # allele: Optional[Allele] Could also just add the allele for all info. allele+dye is enough, right?



@dataclass
class Sample:
    """
    Class for samples, data is (nx6) matrix of all 6 colours
    Should I split this into a list per color attribute?
    Should I add the color_list here instead of in pf? Only used icw Samples for ordering
    """
    name: str       # example: '1A2'
    data: List      #
    color_list = ['FL-6C', 'JOE-6C', 'TMR-6C', 'CXR-6C', 'TOM-6C', 'WEN-6C']


@dataclass
class Person:
    """ Class to store alleles a Person has. """
    name: str            # name is A - Z, letter used to identify person
    alleles: List[str]   # list of 'locus_allele' names


### PROBLEM: need to add together same peaks
### Instead of constantly adding new peaks
# Can't hash user-defined classes
@dataclass
class PersonMixture:
    name: str                       # for example: "1A2"
    persons: List[Person]           # list of Persons present in mix
    fractions: Dict[str, float]     # fractional contribution of each person in mixture
    # why was this supposed to be a class function?
    def create_peaks(self, locus_dict):
        """Returns list of peaks expected in mixture and their relative heights"""
        peak_list = []
        peak_dict = {}
        # add X and Y by hand (all samples are male)
        X_and_Y = locus_dict['AMEL'].alleles
        X = X_and_Y['X']
        Y = X_and_Y['Y']
        peak_list.append(Peak("AMEL_X", X.mid, 0.5, BLUE))
        peak_list.append(Peak("AMEL_Y", Y.mid, 0.5, BLUE))
        # iterate through persons in mix
        for person in self.persons:
            # iterate over their alleles
            for locus_allele in person.alleles:
                try:
                    peak_dict[locus_allele] += self.fractions[person.name]
                except:     # What is the difference between except and else?
                    peak_dict[locus_allele] = self.fractions[person.name]
        # now we have a dictionary of the height of the alleles
        # all that's left is to store corresponding peaks in list
        for locus_allele in peak_dict:
            # I keep storing locus_allele names to access dye color
            # and also to access locus dictionary
            locus_name, allele_name = locus_allele.split("_")
            locus = locus_dict[locus_name]
            allele = locus.alleles[allele_name]
            x = allele.mid                          # store x_location
            height = peak_dict[locus_allele]        # store rel. height
            dye = locus.dye                         # store dye
            new_peak = Peak(locus_allele,x,height,dye)
            peak_list.append(new_peak)               # append peak to list
        return peak_list


@dataclass
class AnalystMixture:
    """ Class to store peaks identified/expected in mixture. """
    name: str               # name of mixture, '1A2' for example
    replicate: str          # where 1 is donor set, 2 is #donors, A is mixture type and 3 is replicate
    peaks: List[Peak]       # list of peaks


# misschien uiteindelijk:
# output class/geanalyseerd profiel, welke pieken zijn aangewezen door CNN
@dataclass
class Result:
    """ TBD """
    name: str
    peaks: Dict[Locus, float]
    thresholds: List[float]


# Global variables
PICOGRAMS = np.array([[300, 150, 150, 150, 150],
                      [300, 30,  30,  30,  30],
                      [150, 150, 60,  60,  60],
                      [150, 30,  60,  30,  30],
                      [600, 30,  60,  30,  30]])

TOTAL_PICOGRAMS = np.array([[450, 600, 750, 900],
                            [330, 360, 390, 420],
                            [300, 360, 420, 480],
                            [180, 240, 270, 300],
                            [630, 690, 720, 750]])

BLUE = Dye('FL-6C', 'b', 1)
GREEN = Dye('JOE-6C', 'g', 2)
YELLOW = Dye('TMR-6C', 'y', 3)
RED = Dye('CXR-6C', 'r', 4)
PURPLE = Dye('TOM-6C', 'm', 5)
LADDER = Dye('WEN-6C', 'k', 6)