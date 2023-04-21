# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 13:34:01 2022

@author: brumor
"""

import numpy as np
import datetime

# LEAP SECONDS
DELTA_UNIX_GPS = 18
datetimeformat = "%Y%m%d_%H%M%S"
epoch = datetime.datetime.strptime("19800106_000000", datetimeformat)

# finner gps uke fra dato i filnavn pcapfil
def filename2gpsweek(pcap_file):
    utc = filename2utc(pcap_file)
    tdiff = utc - epoch + datetime.timedelta(seconds=DELTA_UNIX_GPS)
    gpsweek = tdiff.days // 7
    return gpsweek

def filename2utc(pcap_file):
    ymd_hms = (pcap_file.split('x')[1]).split('_')[1] + '_' + (pcap_file.split('x')[1]).split('_')[2].replace('.pcap', '')
    return datetime.datetime.strptime(ymd_hms, datetimeformat)

# regner om fra unix time til gps seconds of week. Lidar bruker unix og sbet bruker seconds of week (SoW)
def timestamp_unix2sow(unix, gps_week):
    # Correction by Erlend: subtract epoch unix time as well!
    # Another correction (?) by Erlend: removed subtraction of DELTA_UNIX_GPS -- this makes PCAP and SBET correspond.
    sow = unix - 315964800 - (gps_week * 604800)
    return sow
    
def timestamp_sow2unix(sow, gps_week):
    unix = sow + 315964800 + (gps_week * 604800)
    return unix

# leser sbet og smrmsg. Under record types ser du feltene i hver fil
def read_sbet(sbet_filename, smrmsg_filename) -> np.array:
    sbet_record_types = [
        ("time", np.float64),
        ("lat", np.float64),  # radians
        ("lon", np.float64),  # radians
        ("alt", np.float64),
        ("x-vel", np.float64),  # m/s
        ("y-vel", np.float64),
        ("vert-vel", np.float64),
        ("roll", np.float64),  # radians
        ("pitch", np.float64),
        ("heading", np.float64),
        ("wander", np.float64),  # radians
        ("x-acc", np.float64),  # m/s^2
        ("y-acc", np.float64),
        ("vert-acc", np.float64),
        ("x-angrate", np.float64),  # radians/s
        ("y-angrate", np.float64),
        ("z-angrate", np.float64)
    ]

    # kolonner funnet ved å sammenligne txt eksport fra Qinertia
    smrmsg_record_types = [
        ("time", np.float64),
        ("lat-std", np.float64),  # radians
        ("lon-std", np.float64),  # radians
        ("alt-std", np.float64),
        ("roll-std", np.float64),
        ("pitch-std", np.float64),
        ("yaw-std", np.float64),
        ("unknown1", np.float64),  # akselerasjon std.dev?
        ("unknown2", np.float64),
        ("unknown3", np.float64)
    ]
    sbet_np = np.fromfile(sbet_filename, dtype=np.dtype(sbet_record_types))
    smrmsg_np = np.fromfile(smrmsg_filename, dtype=np.dtype(smrmsg_record_types))

    return sbet_np, smrmsg_np