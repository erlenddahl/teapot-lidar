from pcapReader import PcapReader
from tqdm import tqdm

class SerialPcapReader:

    def __init__(self, pcap_paths, meta_data_paths, skip_frames = 0):
        self.readers = [PcapReader(x[0], x[1], skip_frames) for x in zip(pcap_paths, meta_data_paths)]
        self.current_reader_index = 0
        self.max_distance = None
        self._set_metadata()

    def count_frames(self, show_progress):
        return sum([x.count_frames(False) for x in tqdm(self.readers, ascii=True, desc="Counting frames", disable=not show_progress)])

    def reset(self):
        for reader in self.readers:
            reader.reset()
        self.current_reader_index = 0
        self._set_metadata()

    def _next_reader(self):
        self.current_reader_index += 1
        self._set_metadata()

    def _set_metadata(self):
        self.pcap_path = None if self.current_reader_index >= len(self.readers) else self.readers[self.current_reader_index].pcap_path

    def skip_and_get(self, iterator):

        if self.current_reader_index >= len(self.readers):
            return None

        self.readers[self.current_reader_index].max_distance = self.max_distance
        frame = self.readers[self.current_reader_index].skip_and_get(iterator)
        if frame is None:
            self._next_reader()
            return self.skip_and_get(iterator)

        return frame


    def print_info(self, frame_index = None, printFunc = print):
        for reader in self.readers:
            reader.print_info(frame_index, printFunc)

    def remove_vehicle(self, frame, cloud = None):
        return self.readers[0].remove_vehicle(frame, cloud)

    def next_frame(self, remove_vehicle:bool = False, timer = None):
        if self.current_reader_index >= len(self.readers):
            return None

        self.readers[self.current_reader_index].max_distance = self.max_distance
        frame = self.readers[self.current_reader_index].next_frame(remove_vehicle, timer)
        if frame is None:
            self._next_reader()
            return self.next_frame(remove_vehicle, timer)

        return frame

    def read_all_frames(self, remove_vehicle:bool = False):

        frames = []
        while True:
            frame = self.next_frame(remove_vehicle)
            if frame is None:
                return frames
            frames.append(frame)