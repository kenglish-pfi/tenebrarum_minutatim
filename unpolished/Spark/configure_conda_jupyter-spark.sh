conda create --name jupyter-spark
conda activate jupyter-spark

which jupyter
# still /opt/anaconda/bin/jupyter

python -m ipykernel install --user --name jupyter-spark --display-name "Python 3 (jupyter-spark)"

cd ~/.local/share/jupyter/kernels/jupyter-spark

# Replace the default kernel.json:
cat > kernel.json <<__EOF__
{
 "argv": [
  "/opt/anaconda/bin/python",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "Python 3 (jupyter-spark)",
 "env": {
  "CAPTURE_STANDARD_OUT": "true",
  "CAPTURE_STANDARD_ERR": "true",
  "SEND_EMPTY_OUTPUT": "false",
  "SPARK_HOME": "/opt/cloudera/parcels/CDH-6.3.2-1.cdh6.3.2.p0.1605554/lib/spark",
  "JAVA_HOME": "/usr/java/jdk1.8.0_181-cloudera",
  "HADOOP_HOME": "/opt/cloudera/parcels/CDH-6.3.2-1.cdh6.3.2.p0.1605554/lib/hadoop",
  "HIVE_HOME": "/opt/cloudera/parcels/CDH-6.3.2-1.cdh6.3.2.p0.1605554/lib/hive",
  "PYSPARK_PYTHON": "/opt/anaconda/bin/python",
  "PYSPARK_DRIVER_PYTHON": "/opt/anaconda/bin/python",
  "PYTHONPATH": "/opt/cloudera/parcels/CDH-6.3.2-1.cdh6.3.2.p0.1605554/lib/spark/python/lib/py4j-0.10.7-src.zip:/opt/cloudera/parcels/CDH-6.3.2-1.cdh6.3.2.p0.1605554/lib/spark/python/lib/pyspark.zip",
  "PYTHONSTARTUP": "/opt/cloudera/parcels/CDH-6.3.2-1.cdh6.3.2.p0.1605554/lib/spark/python/pyspark/shell.py",
  "PYSPARK_SUBMIT_ARGS": "--master yarn-client --conf spark.executor.cores=1 --conf spark.executor.memory=1g pyspark-shell"
 },
 "language": "python"
}
__EOF__

cd

# start Jupyter
jupyter notebook jupyter notebook --ip 0.0.0.0 --no-browser

# Ignore this warning
# 20/10/28 15:50:56 WARN cluster.YarnSchedulerBackend$YarnSchedulerEndpoint: Attempted to request executors before the AM has registered!

# Choose the jupyter-spark kernel


PYSPARK_SUBMIT_ARGS