
"""
Data Integration and Large-scale Analysis Exercise 2026/2027
Technische Universitaet Berlin

@author{ywcb00}

Adapted from Robertas Jurkus et al.
https://github.com/RobJur/rnn-vessels-trajectory-prediction
https://doi.org/10.1016/j.engappai.2023.106448
"""

import glob
import multiprocessing as mp
import numpy as np
import pandas as pd
from pyproj import Geod


RESAMPLE_FREQUENCY = '60s'
DISTANCE_THRESHOLD = 100 # meters
LOOKAHEAD_TIME = pd.Timedelta(5 * 60, "sec")

def loadData() -> pd.DataFrame:
    # === Data Loading ===
    # Path to the data (folders)
    path = ['data']
    print(f'=== Reading AIS data from the following paths: {", ".join(path)} ===')
    frames = []
    for p in path:
        # Get data file names
        allFiles = glob.glob(p + "/*.csv")
        for filename in allFiles:
            dfFile = pd.read_csv(filename, header=0, sep=',', index_col=None)
            frames.append(dfFile)
    # Concatenate all data into one DataFrame
    data = pd.concat(frames)
    return data

def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    # === Data Transformations ===
    print(f'=== Transforming the data (i.e., feature selection, resampling, etc.) ===')
    # select interested features
    data = data[["MMSI", "# Timestamp", "Longitude", "Latitude", "SOG", "Heading"]]
    data = data.dropna()
    data = data.drop_duplicates()
    data['DateTime'] = pd.to_datetime(data['# Timestamp'])
    # resample the data with the specified frequency
    data = data.groupby("MMSI").apply(lambda dfGroup: dfGroup.drop_duplicates(subset=['DateTime'])
            .set_index("DateTime").resample(RESAMPLE_FREQUENCY).nearest(limit=1).dropna(how='all')
        ).drop_duplicates().reset_index(drop=True)
    # retain original timestamp as datetime type
    data['DateTime'] = pd.to_datetime(data['# Timestamp'])
    data = data.drop_duplicates() # resampling strategy 'nearest' might duplicate entries

    data.sort_values(["MMSI", "DateTime"], inplace=True)
    lookaheadTimesList = list()
    for idx, (vIdx, vessel) in enumerate(data.iterrows()):
        lookaheadTime = LOOKAHEAD_TIME
        if(idx < (data.shape[0] - 1) and vessel["MMSI"] == data.iloc[idx+1]["MMSI"]):
            reportDiffTime = data.iloc[idx+1]["DateTime"] - vessel["DateTime"]
            lookaheadTime = min(lookaheadTime, reportDiffTime)
        lookaheadTimesList.append(lookaheadTime)
    data["LookaheadTime"] = lookaheadTimesList

    return data

def getData() -> pd.DataFrame:
    data = loadData()
    data = preprocess(data)
    return data

# convert knots to meters per second
def ktsToMps(velocityKnots):
    return velocityKnots * 1_852 / (60 * 60)

geod = Geod(ellps='WGS84', proj="utm", zone=33)
def getFuturePosition(p, azi, dist):
    futLon, futLat, bckAzi = geod.fwd(p[0], p[1], azi, dist)
    return np.array([futLon, futLat])

def distanceBetweenCoordinates(thisPos, thatPos):
    azi12, azi21, dist = geod.inv(thisPos[0], thisPos[1], thatPos[0], thatPos[1])
    return dist

def checkCollision(vesselA, vesselB):
    if(vesselA["MMSI"] == vesselB["MMSI"]):
        return None # avoid detecting self-collisions (A -> A)
    if(vesselA["SOG"] == 0 and vesselB["SOG"] == 0):
        return None # not moving vessels are not in a collision situation

    # coordinate positions of both vessels
    a1 = np.array([vesselA["Longitude"], vesselA["Latitude"]])
    b1 = np.array([vesselB["Longitude"], vesselB["Latitude"]])

    # get change in position after one second
    at = getFuturePosition(a1, vesselA["Heading"], ktsToMps(vesselA["SOG"])) - a1
    bt = getFuturePosition(b1, vesselB["Heading"], ktsToMps(vesselB["SOG"])) - b1
    # minimum and maximum time bounds to consider
    t0 = max(vesselA["DateTime"], vesselB["DateTime"])
    t1 = min(vesselA["DateTime"] + vesselA["LookaheadTime"], vesselB["DateTime"] + vesselB["LookaheadTime"])
    if(t1 < t0):
        return None # no collision during considered time range
    # positions at time t0
    a0 = a1 + at * (t0 - vesselA["DateTime"]).total_seconds()
    b0 = b1 + bt * (t0 - vesselB["DateTime"]).total_seconds()
    with np.errstate(divide='ignore', invalid='ignore'):
        # obtain time of minimum distance (in seconds from t0)
        # adapted from https://codepen.io/sveinatle/pen/OPqLKE
        mintime = -(a0[0]*at[0] - at[0]*b0[0] - (a0[0]-b0[0])*bt[0] + a0[1]*at[1] - at[1]*b0[1] - (a0[1]-b0[1])*bt[1]) / np.sum(np.power(at - bt, 2))
    # vessels sail parallel to each other
    if(np.isnan(mintime)):
        mintime = 0
    elif(np.isinf(mintime)):
        mintime = (t1 - t0).seconds
    mintime = max(mintime, 0) # if minimum distance is in the past, check current state
    mintime = min(mintime, (t1 - t0).seconds) # cap by maximum look ahead time
    # calculate minimum distance between vessels
    mindist = distanceBetweenCoordinates(a0 + (mintime * at), b0 + (mintime * bt))
    return (mindist < DISTANCE_THRESHOLD) # collision detected

def processSingleThreaded(aisData: pd.DataFrame) -> pd.DataFrame:
    # TODO: Student task 1.1
        # sort by time: only records at most LOOKAHEAD_TIME apart can be on a collision course
    data = aisData.sort_values("DateTime", kind="stable").reset_index(drop=True)
    mmsi = data["MMSI"].to_numpy()
    sog = data["SOG"].to_numpy(dtype=float)
    times = data["DateTime"].to_numpy()
    lookahead = data["LookaheadTime"].to_numpy()
    lat = np.radians(data["Latitude"].to_numpy(dtype=float))
    lon = np.radians(data["Longitude"].to_numpy(dtype=float))
    # distance (m) a vessel can travel within its own lookahead window
    reach = ktsToMps(sog) * (lookahead / np.timedelta64(1, "s"))
    # candidates of record i: all later records j with time_j <= time_i + lookahead_i
    windowEnd = np.searchsorted(times, times + lookahead, side="right")
    earthRadius = 6_350_000 # below the polar radius, so distances are never overestimated

    pairs = []
    for i in range(data.shape[0]):
        j = np.arange(i + 1, windowEnd[i])
        # cheap vectorized haversine distance between record i and all its candidates
        h = (np.sin((lat[j] - lat[i]) / 2) ** 2
             + np.cos(lat[i]) * np.cos(lat[j]) * np.sin((lon[j] - lon[i]) / 2) ** 2)
        dist = 2 * earthRadius * np.arcsin(np.sqrt(h))
        # prune pairs that are too far apart to get closer than the threshold (1% safety margin)
        near = dist <= (DISTANCE_THRESHOLD + reach[i] + reach[j]) * 1.01 + 1
        for k in j[near]:
            # smaller MMSI is vessel A, which avoids mirrored duplicates
            a, b = (i, k) if mmsi[i] < mmsi[k] else (k, i)
            if(checkCollision(data.iloc[a], data.iloc[b])):
                pairs.append((a, b))

    idxA, idxB = np.array(pairs, dtype=int).reshape(-1, 2).T
    vesselsA, vesselsB = data.iloc[idxA], data.iloc[idxB]
    return pd.DataFrame({
        "A.MMSI": vesselsA["MMSI"].to_numpy(), "A.DateTime": vesselsA["DateTime"].to_numpy(),
        "B.MMSI": vesselsB["MMSI"].to_numpy(), "B.DateTime": vesselsB["DateTime"].to_numpy()
    }).drop_duplicates().reset_index(drop=True)

def partitionData(data: pd.DataFrame, numPartitions: int | None) -> list[pd.DataFrame]:
    # TODO: Student task 1.2
        # Time-based partitioning: records can only collide if they are at most LOOKAHEAD_TIME apart.
    # Each partition covers a time range [start, end) plus a halo of the following
    # LOOKAHEAD_TIME, so that pairs across partition boundaries are not lost.
    if(numPartitions is None):
        numPartitions = mp.cpu_count()
    data = data.sort_values("DateTime", kind="stable")
    times = data["DateTime"]
    # boundaries at equal record counts to balance the load (duplicates removed for ties)
    starts = sorted(set(times.iloc[k * len(data) // numPartitions] for k in range(numPartitions)))
    ends = starts[1:] + [times.iloc[-1] + pd.Timedelta(1, "ns")]
    return [data[(times >= start) & (times <= end + LOOKAHEAD_TIME)].reset_index(drop=True)
            for start, end in zip(starts, ends)]

def processMultiThreaded(partitions: list[pd.DataFrame]):
   # TODO: Student task 1.3
       # worker processes (instead of threads) circumvent the GIL for this CPU-bound workload
    with mp.Pool(min(len(partitions), mp.cpu_count())) as pool:
        results = pool.map(processSingleThreaded, partitions)
    # pairs in the halo of a partition are also found by the neighboring partition
    return pd.concat(results, ignore_index=True).drop_duplicates().reset_index(drop=True)

def main():
    data = getData()

    collisions1 = processSingleThreaded(data)

    partitions = partitionData(data, None)
    collisions2 = processMultiThreaded(partitions)

    collisions1 = collisions1.sort_values(["A.MMSI", "A.DateTime", "B.MMSI", "B.DateTime"]).reset_index(drop=True)
    collisions2 = collisions2.sort_values(["A.MMSI", "A.DateTime", "B.MMSI", "B.DateTime"]).reset_index(drop=True)
    collisionsDiff = collisions1.compare(collisions2)
    if(collisionsDiff.empty):
        print("Single-threaded results and multi-threaded results are equivalent.")
    else:
        print(f'ERROR: Multi-threaded results differ from single-threaded results.\n Difference:\n{collisionsDiff}')
        exit(-1)

    collisions1.to_pickle("collisions_pandas.pkl")

if __name__ == "__main__":
    main()
