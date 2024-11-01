import os
import argparse

from pcap.pcapReader import PcapReader
from pcap.serialPcapReader import SerialPcapReader

class PcapReaderHelper:

    @staticmethod
    def get_path_args(args = None):
        """ Creates an argument parser that handles --pcap and --json, where the latter is optional.
        If --json is not given, it will be replaced with the values of the --pcap parameter with the file
        extension changed to .json.
        """

        if args is None:
            parser = argparse.ArgumentParser()
            PcapReaderHelper.add_path_arguments(parser)
            args = parser.parse_args()

        return args

    @staticmethod
    def add_sbet_arguments(parser, browsing_only=False):
        parser.add_argument('--sbet-crs-from', type=int, default=4937, required=False, help="SBET coordinates will be transformed from the CRS provided by --sbet-crs-from to the CRS provided by --sbet-crs-to. The latter must correspond to the CRS of the point cloud.")
        parser.add_argument('--sbet-crs-to', type=int, default=5972, required=False, help="SBET coordinates will be transformed from the CRS provided by --sbet-crs-from to the CRS provided by --sbet-crs-to. The latter must correspond to the CRS of the point cloud.")
        
        if browsing_only:
            return

        parser.add_argument('--sbet', type=str, required=True, help="The path to a corresponding SBET file with GNSS coordinates.")
        parser.add_argument('--sbet-noise', type=float, nargs=3, required=False, help="If given, all SBET coordinates will be randomized by adding a random value between +/- this value to the X, Y and Z coordinates. A value must be provided for each dimension (three values). This should be used together with --recreate-caches, otherwise any cached coordinates will be loaded and override the randomization.")
        parser.add_argument('--sbet-noise-from-frame-ix', type=int, default=0, required=False, help="If SBET noise is activated, the noise will start from this frame index (frames before this index will use the actual unchanged coordinates).")

    @staticmethod
    def add_path_arguments(parser, browsing_only=False):
        parser.add_argument('--pcap', type=str, nargs='+', required=True, help="The path to one or more PCAP files to visualize, relative or absolute. A path to a directory containing multiple pcap files can also be provided.")
        parser.add_argument('--json', type=str, nargs='+', required=False, help="The path to corresponding JSON file(s) for each of the PCAP file(s) with the sensor metadata, relative or absolute. If this is not given, the PCAP location is used (by replacing .pcap with .json). A path to a directory containing multiple json files can also be provided.")
        parser.add_argument('--max-frame-radius', type=float, default=None, required=False, help="If given as a number larger than 0, all PCAP frames will be reduced in size by removing all points that are further away from the origin than this value (measured in meters).")
        parser.add_argument('--recreate-caches', action='store_true')

        PcapReaderHelper.add_sbet_arguments(parser, browsing_only)

    @staticmethod
    def from_path_args(args = None):

        if args is None:
            args = PcapReaderHelper.get_path_args()

        return PcapReaderHelper.from_lists(args.pcap, args.json, args=args)

    @staticmethod
    def expand_folders(items, file_extension):
        if items is None:
            return None

        expanded = []
        for item in items:
            if os.path.isdir(item):
                for file in os.listdir(item):
                    if os.path.isfile(os.path.join(item, file)) and file.lower().endswith(file_extension.lower()):
                        expanded.append(os.path.join(item, file))
            else:
                expanded.append(item)

        return expanded

    @staticmethod
    def from_lists(pcaps, jsons = None, skip_frames = 0, args=None):

        if isinstance(pcaps, str):
            pcaps = [pcaps]
        if isinstance(jsons, str):
            jsons = [jsons]

        pcaps = PcapReaderHelper.expand_folders(pcaps, ".pcap")
        jsons = PcapReaderHelper.expand_folders(jsons, ".json")

        if jsons is None:
            jsons = [x.replace(".pcap", ".json") for x in pcaps]

        if len(jsons) != len(pcaps):
            raise ValueError("Number of JSON files does not match number of PCAP files.")

        if len(pcaps) < 1:
            raise Exception("Found no PCAP files in the given location(s).")

        if len(pcaps) == 1:
            return PcapReader(pcaps[0], jsons[0], skip_frames, args=args)
        else:
            return SerialPcapReader(pcaps, jsons, skip_frames, args=args)