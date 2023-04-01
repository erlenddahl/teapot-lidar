import argparse
from itertools import chain
from pcapReader import PcapReader   
from tqdm import tqdm  
import os
from glob import glob

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--root-directory', type=str, required=True, help="Recreate caches for all pcap files found recursively under the given root directory.")
    args = parser.parse_args()

    files = list(chain.from_iterable(glob(os.path.join(x[0], '*.pcap')) for x in os.walk(args.root_directory)))

    failures = 0
    successes = 0
    for pcap in tqdm(files, ascii=True, desc="Recreating caches"):
        try:
            reader = PcapReader(pcap)
            reader.count_frames()
            reader.get_coordinates()
            successes += 1
        except:
            failures += 1

    print("Succesful:", successes)
    print("Failed:", failures)