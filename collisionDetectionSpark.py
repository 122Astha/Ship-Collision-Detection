
"""
Data Integration and Large-scale Analysis Exercise 2026/2027
Technische Universitaet Berlin

@author{ywcb00}

Adapted from Robertas Jurkus et al.
https://github.com/RobJur/rnn-vessels-trajectory-prediction
https://doi.org/10.1016/j.engappai.2023.106448
"""

import glob
import numpy as np
from pyproj import Geod
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, desc, lag, least, udf
import pyspark.sql.types as pstypes
import pyspark.pandas as pspd

spark = SparkSession.builder.master("local[*]").config("spark.driver.memory", "4g").getOrCreate()

RESAMPLE_FREQUENCY = '60s'
DISTANCE_THRESHOLD = 100 # meters
LOOKAHEAD_TIME = 5 * 60 # seconds

def loadData() -> pspd.DataFrame:
    # === Data Loading ===
    # Path to the data (folders)
    path = ['data']
    print(f'=== Reading AIS data from the following paths: {",".join(path)} ===')
    frames = []
    for p in path:
        # Get data file names
        allFiles = glob.glob(p + "/*.csv")
        for filename in allFiles:
            dfFile = pspd.read_csv(filename, header=0, sep=',', index_col=None)
            frames.append(dfFile)
    # Concatenate all data into one DataFrame
    data = pspd.concat(frames)
    return data

def preprocess(data: pspd.DataFrame) -> pspd.DataFrame:
    raise NotImplementedError # TODO: Student task 2.1

def getData() -> pspd.DataFrame:
    data = loadData()
    data = preprocess(data)
    return data

geod = Geod(ellps='WGS84', proj="utm", zone=33)
def getFuturePosition(lon, lat, azi, dist):
    futLon, futLat, bckAzi = geod.fwd(lon, lat, azi, dist)
    return futLon, futLat

def distanceBetweenCoordinates(thisPos, thatPos):
    azi12, azi21, dist = geod.inv(thisPos[0], thisPos[1], thatPos[0], thatPos[1])
    return dist

# convert knots to meters per second
def ktsToMps(velocityKnots):
    return velocityKnots * 1_852 / (60 * 60)
ktsToMps_udf = udf(ktsToMps, pstypes.DoubleType())

def partitionData(data: pspd.DataFrame):
    raise NotImplementedError # TODO: Student task 2.2

def process(partitions) -> pspd.DataFrame:
    raise NotImplementedError # TODO: Student task 2.3

def main():
    data = getData()
    partitions = partitionData(data)
    collisions = process(partitions)

    collisions = collisions.toPandas()
    collisions = collisions.sort_values(["A.MMSI", "A.DateTime", "B.MMSI", "B.DateTime"]).reset_index(drop=True)
    collisions.to_pickle("collisions_spark.pkl")
    try:
        import pandas as pd
        collisionsPandas = pd.read_pickle("collisions_pandas.pkl")
        if(collisions.shape[0] != collisionsPandas.shape[0]):
            print(f'ERROR: Different numbers of collisions: {collisionsPandas.shape[0]} (Pandas) vs. {collisions.shape[0]} (Spark).')
            exit(-2)
        else:
            collisionsDiff = collisions.compare(collisionsPandas)
            if(collisionsDiff.empty):
                print("Spark results and Pandas results are equivalent.")
            else:
                print(f'ERROR: Spark results differ from Pandas results.\n Difference:\n{collisionsDiff}')
                exit(-1)
    except FileNotFoundError:
        print("Could not find Pandas results to compare against.")
        exit(1)

if __name__ == "__main__":
    main()
