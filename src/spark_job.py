from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.sql import types as T


def get_spark():
    spark = (
        SparkSession.builder
        .appName("SalarySparkJob")
        .config("spark.mongodb.output.uri", "mongodb://mongodb:27017/salaries.clean")
        .config(
            "spark.jars.packages",
            "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,"
            "org.elasticsearch:elasticsearch-spark-30_2.12:7.17.9"
        )
        .getOrCreate()
    )
    return spark


def load_raw_from_hdfs(spark):
    hdfs_path = "hdfs://namenode:9000/user/root/raw/ds_salaries.csv"
    df = spark.read.csv(hdfs_path, header=True, inferSchema=True)
    return df


def clean_data(df):
    # 1) Null handling – drop rows with critical nulls
    critical_cols = ["work_year", "job_title", "salary_in_usd"]
    df = df.dropna(subset=critical_cols)

    # 2) Data type fixing – cast numeric columns
    df = (
        df
        .withColumn("work_year", col("work_year").cast(T.IntegerType()))
        .withColumn("salary", col("salary").cast(T.DoubleType()))
        .withColumn("salary_in_usd", col("salary_in_usd").cast(T.DoubleType()))
        .withColumn("remote_ratio", col("remote_ratio").cast(T.IntegerType()))
    )

    # 3) Column renaming – make names consistent / readable
    df = df.withColumnRenamed("salary_in_usd", "salary_usd")

    # 4) Duplicate removal – remove exact duplicate rows
    df = df.dropDuplicates()

    # Normalize experience level (extra cleaning)
    df = df.withColumn(
        "experience_level",
        when(col("experience_level") == "EN", "Entry")
        .when(col("experience_level") == "MI", "Mid")
        .when(col("experience_level") == "SE", "Senior")
        .when(col("experience_level") == "EX", "Executive")
        .otherwise(col("experience_level"))
    )

    return df


def add_features(df):
    # Remote category
    df = df.withColumn(
        "remote_category",
        when(col("remote_ratio") == 100, "Fully Remote")
        .when(col("remote_ratio") == 0, "Onsite")
        .otherwise("Hybrid")
    )

    # Salary band
    df = df.withColumn(
        "salary_band",
        when(col("salary_usd") < 80000, "Low")
        .when((col("salary_usd") >= 80000) & (col("salary_usd") < 150000), "Medium")
        .otherwise("High")
    )

    return df


def write_to_mongo(df):
    df.write.format("mongo").mode("overwrite").save()


def write_to_es(df):
    (
        df.write.format("org.elasticsearch.spark.sql")
        .option("es.resource", "salaries_clean/_doc")
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
