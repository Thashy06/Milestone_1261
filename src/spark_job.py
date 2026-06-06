from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month


def get_spark():
    spark = (
        SparkSession.builder
        .appName("ClimateSparkJob")
        .config("spark.mongodb.output.uri", "mongodb://mongodb:27017/climate.clean")
        .config(
            "spark.jars.packages",
            "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,"
            "org.elasticsearch:elasticsearch-spark-30_2.12:7.17.9"
        )
        .getOrCreate()
    )
    return spark


def load_raw_from_hdfs(spark):
    hdfs_path = "hdfs://hadoop-namenode:9000/user/root/raw/temperatures.csv"
    df = spark.read.csv(hdfs_path, header=True, inferSchema=True)
    return df


def clean_data(df):
    df = df.dropna(subset=["AverageTemperature"])

    df = df.withColumn("AverageTemperature", col("AverageTemperature").cast("double"))
    df = df.withColumn(
        "AverageTemperatureUncertainty",
        col("AverageTemperatureUncertainty").cast("double")
    )
    df = df.withColumn("dt", col("dt").cast("date"))

    df = df.withColumnRenamed("AverageTemperature", "avg_temp")
    df = df.withColumnRenamed("AverageTemperatureUncertainty", "temp_uncertainty")

    df = df.dropDuplicates()
    return df


def add_features(df):
    df = df.withColumn("year", year(col("dt")))
    df = df.withColumn("month", month(col("dt")))
    return df


def write_to_mongo(df):
    df.write.format("mongo").mode("overwrite").save()


def write_to_es(df):
    (
        df.write.format("org.elasticsearch.spark.sql")
        .option("es.resource", "climate_clean/_doc")
        .option("es.nodes", "elasticsearch")
        .mode("overwrite")
        .save()
    )


def main():
    spark = get_spark()

    raw_df = load_raw_from_hdfs(spark)
    clean_df = clean_data(raw_df)
    final_df = add_features(clean_df)

    write_to_mongo(final_df)
    write_to_es(final_df)

    spark.stop()


if __name__ == "__main__":
    main()
