# Exercises

These exercises are based on the following hostnames and fixed
IP-addresses. Please adjust them to your specific hardware setup.


| Hostname                  | IP Address  |
| ------------------------- | ----------- |
| rpi0 (**master**/manager) | 10.42.0.250 |
| rpi1 (**slave**/worker)   | 10.42.0.251 |
| rpi2 (**slave**/worker)   | 10.42.0.252 |
| rpi3 (**slave**/worker)   | 10.42.0.253 |




## Introduction to Spark

<div align="center">
  <a href="https://www.youtube.com/watch?v=vHBhx6Gcr64">
    <img src="images/spark.png" alt="PiCluster Resilience" style="width:30%;">
  </a>
</div>

In this exercise, you will use PySpark and the [MovieLens 20M Dataset](https://grouplens.org/datasets/movielens/20m/) on movie ratings to answer several questions. These exercises promote "Learning by Doing" which means that we guide you through the steps but you have to do them yourself. Sometimes, this means that you have to use Google, Stackoverflow, or the [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/pyspark.html).

First, **visit JupyterLab** (10.42.0.250:8888) and upload the [MovieLens 20M Dataset](https://grouplens.org/datasets/movielens/20m/) into **/gfs** (default view in the file explorer). Alternatively, run the following commands in the JupyterLab terminal:

```bash
# change directory
cd /gfs
# install wget
apt install wget -y
# download and unzip MovieLens dataset
wget http://files.grouplens.org/datasets/movielens/ml-20m.zip
unzip ml-20m.zip
```

Now, run [this](https://github.com/DocSeven/PiCluster/blob/master/Exercises/Movielens_exercises.ipynb) Jupyter Notebook and follow the instructions. 



## Testing Resilience

<div align="center">
  <a href="https://www.youtube.com/watch?v=4scaV421mQo">
    <img src="images/resilience.png" alt="PiCluster Resilience" style="width:30%;">
  </a>
</div>
For testing the resilience of the cluster, you can try your own code or use the template below. The template calculates the mean, standard deviation, min, max, and count of the rating columns and parallelizes well. Other tasks might not parallelize well, hence, they do not profit from additional workers.

```python
import time
start_time = time.time()

from pyspark.sql import SparkSession

if __name__ == "__main__":

    print("--- start ---")

    # Connect to the master
    spark = SparkSession\
        .builder\
        .master("spark://sparkmaster:7077")\
        .appName("resilience") \
        .getOrCreate()

    # Calculate count, mean, sd, min, max of ratings
    ratings = spark.read.csv('ml-20m/ratings.csv', inferSchema=True, header=True)
    ratings.describe().show()

    # Disconnect
    spark.stop()

    print("Duration: %s seconds" % (time.time() - start_time))
    print("--- end ---")
```
First, check JupyterLab, Spark UI, and Visualizer. Make sure that your cluster is in working condition. Afterward, open JupyterLab and create a new notebook. **Run the template above** (or your own code) and visit Spark UI. **Check** the **number of assigned cores** and the **duration**. If something goes wrong, you can kill the task in Spark UI but make sure to restart the IPython kernel. If everything works as expected, you should see a table with descriptive statistics and duration (seconds) in your notebook's output. Remember the duration and **disconnect a worker** (or two). Please note that the cluster crashes when master is down or less than two nodes are active. **Wait** until Spark UI highlights the status of the workers as "DEAD" and **re-run the notebook**. Again, **check the assigned cores and the duration**. The duration should now be longer because you have fewer workers. Last but not least, **reconnect the workers**, wait till they are "ALIVE" and **run the notebook again**. The results should be comparable to the first run.

In a second step, you can try to **disconnect the workers while running your notebook**. The notebook should still run to the end but it might take longer because the resources have to be reallocated.
