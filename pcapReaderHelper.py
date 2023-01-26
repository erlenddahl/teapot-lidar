import os
import argparse

from pcapReader import PcapReader
from serialPcapReader import SerialPcapReader

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
    def add_path_arguments(parser):
        parser.add_argument('--pcap', type=str, nargs='+', required=True, help="The path to one or more PCAP files to visualize, relative or absolute. A path to a directory containing multiple pcap files can also be provided.")
        parser.add_argument('--json', type=str, nargs='+', required=False, help="The path to corresponding JSON file(s) for each of the PCAP file(s) with the sensor metadata, relative or absolute. If this is not given, the PCAP location is used (by replacing .pcap with .json). A path to a directory containing multiple json files can also be provided.")
        parser.add_argument('--sbet', type=str, required=False, help="The path to a corresponding SBET file with GNSS coordinates.")
        parser.add_argument('--sbet-z-offset', type=float, default=0, required=False, help="If the GNSS positions in the SBET file have an altitude offset from the point cloud, this argument will be added/subtracted on the Z coordinates of each SBET coordinate.")
        parser.add_argument('--recreate-caches', action='store_true')

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

        if len(pcaps) == 1:
            return PcapReader(pcaps[0], jsons[0], skip_frames, args=args)
        else:
            return SerialPcapReader(pcaps, jsons, skip_frames, args=args)