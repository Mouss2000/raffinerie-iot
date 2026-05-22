FROM apache/spark:3.4.1

USER root

# Install dependencies for Spark-Submit
# Using spark-submit --packages download strategy instead of manual jar management for simplicity
# but we can pre-cache them if needed.

COPY traitement_kpi.py /app/traitement_kpi.py

WORKDIR /app

ENTRYPOINT [ "/opt/spark/bin/spark-submit", \
             "--conf", "spark.jars.ivy=/tmp/.ivy", \
             "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.postgresql:postgresql:42.6.0,org.apache.hadoop:hadoop-aws:3.3.1", \
             "traitement_kpi.py" ]
