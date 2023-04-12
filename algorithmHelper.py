from matchers.nicp import NicpMatcher
from matchers.downsamplefirst import DownsampleFirstNicpMatcher
from matchers.globalregistrationfirst import GlobalFirstNicpMatcher
from matchers.fastglobalregistrationfirst import FastGlobalFirstNicpMatcher
#from matchers.probregmatchers import CpdMatcher, FilterregMatcher

class AlgorithmHelper:

    algorithms = []

    @staticmethod
    def get_all_algorithms():

        if len(AlgorithmHelper.algorithms) > 0:
            return AlgorithmHelper.algorithms

        AlgorithmHelper._add_algorithm(NicpMatcher(), "NICP")
        AlgorithmHelper._add_algorithm(DownsampleFirstNicpMatcher(), "Downsample (0.5), then NICP")
        AlgorithmHelper._add_algorithm(DownsampleFirstNicpMatcher(0.1), "Downsample (0.1), then NICP")
        AlgorithmHelper._add_algorithm(DownsampleFirstNicpMatcher(0.05), "Downsample (0.05), then NICP")
        AlgorithmHelper._add_algorithm(GlobalFirstNicpMatcher(), "Global registration, then NICP")
        AlgorithmHelper._add_algorithm(FastGlobalFirstNicpMatcher(), "Fast global registration, then NICP")
        #AlgorithmHelper._add_algorithm(CpdMatcher(tf_type_name="rigid"), "CPD rigid")
        #AlgorithmHelper._add_algorithm(CpdMatcher(tf_type_name="affine"), "CPD affine")
        #AlgorithmHelper._add_algorithm(CpdMatcher(tf_type_name="nonrigid"), "CPD nonrigid")
        #AlgorithmHelper._add_algorithm(FilterregMatcher(), "Filterreg pt2pt")
        #AlgorithmHelper._add_algorithm(FilterregMatcher(objective_type="pt2pl"), "Filterreg pt2pl")

        return AlgorithmHelper.algorithms

    @staticmethod
    def _add_algorithm(algo, name):
        algo.name = name
        algo.search_name = name.lower().strip()
        AlgorithmHelper.algorithms.append(algo)

    @staticmethod
    def get_algorithm(name):
        name = name.lower().strip()

        for a in AlgorithmHelper.get_all_algorithms():
            if a.search_name == name:
                return a

        return None

