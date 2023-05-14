import argparse
from itertools import chain
from tqdm import tqdm  
import os
from glob import glob

from pcap.pcapReader import PcapReader
from pcap.pcapReaderHelper import PcapReaderHelper

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--root-directory', type=str, required=True, help="Recreate caches for all pcap files found recursively under the given root directory.")
    parser.add_argument('--recreate-caches', action='store_true', required=False, help="If True, existing caches will be re-created. If False, files with existing caches will be skipped.")
    PcapReaderHelper.add_sbet_arguments(parser)
    args = parser.parse_args()

    # The PCAP reader expects this argument, but it's not relevant here, so we always set it to False.
    args.skip_last_frame_in_pcap_file = False
    args.max_frame_radius = 25

    files = list([x for x in chain.from_iterable(glob(os.path.join(x[0], '*.pcap')) for x in os.walk(args.root_directory)) if not x.endswith(".pcap.meta.json")])

    failures = []
    successes = 0
    for pcap in tqdm(files, ascii=True, desc="Recreating caches"):
        try:
            reader = PcapReader(pcap, args=args)
            reader.count_frames()
            reader.get_coordinates()
            successes += 1
        except Exception as e:
            failures.append(pcap)
            tqdm.write(f"ERROR: {e}")

    tqdm.write(f"Succesful: {successes}")
    tqdm.write(f"Failed: {failures}")