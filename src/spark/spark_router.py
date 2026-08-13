import sys, argparse
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
except ImportError:
    SparkSession = None

def run_batch_job(input_path, output_path):
    if not SparkSession:
        print("[!] PySpark not installed in local environment.")
        return
    spark = SparkSession.builder.appName("TicketBatchRouter").getOrCreate()
    df = spark.read.json(input_path)
    df.show(5)
    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/sample_tickets.json")
    parser.add_argument("--output", default="output/routed_tickets.json")
    args = parser.parse_args()
    run_batch_job(args.input, args.output)
