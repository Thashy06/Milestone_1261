import pandas as pd
from src.ingest_hdfs import ingest_to_hdfs

def main():
  
    df = pd.read_csv("data/GlobalLandTemperaturesByCity.csv")
    ingest_to_hdfs(df)

if __name__ == "__main__":
    main()
