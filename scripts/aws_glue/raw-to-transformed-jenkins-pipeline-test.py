import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import gs_to_timestamp

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Amazon S3
AmazonS3_node1710052918037 = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": '"', "withHeader": True, "separator": ","},
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://jenkins-aws-glue-data-pipeline-test/raw/"],
        "recurse": True,
    },
    transformation_ctx="AmazonS3_node1710052918037",
)

# Script generated for node To Timestamp
ToTimestamp_node1710054954011 = AmazonS3_node1710052918037.gs_to_timestamp(
    colName="StartTime", colType="iso"
)

# Script generated for node Amazon S3
AmazonS3_node1710055015451 = glueContext.write_dynamic_frame.from_options(
    frame=ToTimestamp_node1710054954011,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://jenkins-aws-glue-data-pipeline-test/transformed/",
        "partitionKeys": ["CPID"],
    },
    format_options={"compression": "snappy"},
    transformation_ctx="AmazonS3_node1710055015451",
)

job.commit()
