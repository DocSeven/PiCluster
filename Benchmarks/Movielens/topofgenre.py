'''
Shows to top movies of a particular genre
Parameters e.g: program.py movies.csv ratings.csv --delim="," --genre="Comedy"

Important:
1. Python < 3.7 requires to run: export PYTHONIOENCODING=UTF-8 
(https://issues.apache.org/jira/browse/SPARK-11772)
2. Throws shuffle error with large files still but works

Databases:
Not supported: ml-100k u.item u.data
sudo wget http://files.grouplens.org/datasets/movielens/ml-1m.zip
sudo wget http://files.grouplens.org/datasets/movielens/ml-10m.zip
sudo wget http://files.grouplens.org/datasets/movielens/ml-20m.zip

sudo unzip ml-1m.zip
sudo unzip ml-10m.zip
sudo unzip ml-20m.zip

Run:
program <movies_file> <ratings_file> <tag>

Tags:
--delim: the delimitor/seperator of the file e.g --delim=","
--header: specify if the file has headers e.g --deader="true"

spark-submit --master spark://spark-master:7077  topofgenre.py ./ml-1m/movies.dat ./ml-1m/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  topofgenre.py ./ml-10M100K/movies.dat ./10M100K/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  topofgenre.py ./ml-20m/movies.csv ./ml-20m/ratings.csv --delim=","
'''
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.functions import split, explode
from pyspark.sql.types import *

from csv import reader
import argparse
import numpy
import time
import sys, os

parser = argparse.ArgumentParser()
parser.add_argument("movies_file", help="Movies File")
parser.add_argument("ratings_file", help="Ratings File")
parser.add_argument("--delimit", default="::", help="The delimiter of the file: e.g --delimit=\"::\"")
parser.add_argument("--genre", default="Comedy", help="The desired genre: e.g --genre=\"Drama\"")
args = parser.parse_args()

DELIMITER = args.delimit
MOVIES_FILE = args.movies_file
RATINGS_FILE = args.ratings_file
GENRE = args.genre
CONTAINS_HEADER = "false"

rating_schema = StructType([
    StructField("userID", IntegerType()),
    StructField("movieID", IntegerType()),
    StructField("rating", DoubleType()),
    StructField("timestamp", LongType()) ])

movie_schema = StructType([
    StructField("movieID", IntegerType()),
    StructField("movieTitle", StringType()),
    StructField("genres", StringType()) ])

def check_header():
    global CONTAINS_HEADER
    with open(MOVIES_FILE, encoding='ascii', errors='ignore') as f:
        first_line = f.readline()
        fields = first_line.split(DELIMITER)
        CONTAINS_HEADER = "false" if fields[0].isnumeric() else "true"

def parse_ratings(line):
    fields = line.value.split(DELIMITER)
    return Row(userID = int(fields[0]), movieID = int(fields[1]), rating = float(fields[2]))

def parse_movies(line):
    fields = line.value.split(DELIMITER)
    return Row(movieID = int(fields[0]), movieTitle = str(fields[1]).encode('ascii', 'ignore').decode(),  genres = str(fields[2]).encode('ascii', 'ignore').decode() )

def print_rdd(df):
    df_tmp = df
    df_tmp.show(5)
    df_tmp.printSchema()

def main():
    spark = SparkSession.builder.appName("topofgenre").getOrCreate()
    check_header()

    if len(DELIMITER) == 1:
        ratings_data = spark.read.load(RATINGS_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, schema=rating_schema).rdd
        movie_names = spark.read.load(MOVIES_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, schema=movie_schema).rdd
    else:
        ratings_data = spark.read.text(RATINGS_FILE).rdd.map(parse_ratings)
        movie_names = spark.read.text(MOVIES_FILE).rdd.map(parse_movies)

    movies = spark.createDataFrame(movie_names).cache()
    ratings = spark.createDataFrame(ratings_data).cache()

    top_movies = ratings.groupBy("movieID").count().filter("count > 500").join(ratings.groupBy("movieID").avg("rating"), "movieID").join(movies, "movieID")
    top_movies_explode = top_movies.withColumn("genres", explode(split("genres", "[|]")))
    top_comedy = top_movies_explode.filter(f"genres == '{GENRE}'").orderBy("avg(rating)", ascending=False)
    result = top_comedy.select("movieTitle", "avg(rating)", "count")
    result.show(10, False)

    print(f"> Top movies of genre: {GENRE}")
    print("------------------------")
    # result = result.take(10)
    # for line in result:
    #     print(line['movieTitle'].encode('ascii', 'ignore').decode(), line['avg(rating)'])
    spark.stop()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time() - start_time

    print("------------------------")
    print("Runtime: ", end_time)
    print("------------------------")