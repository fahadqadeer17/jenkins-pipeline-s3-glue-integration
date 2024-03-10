# jenkins-pipeline-s3-glue-integration

![Jenkins CI/CD Pipeline for an AWS Data Pipeline](/assets/images/Jenkins%20Pipeline%20Test.png)

## CI/CD Pipeline
- The CI/CD Pipeline expects a push to be made in the relevant Github repository in the dev branch
- The push on the dev branch triggers the Jenkins pipeline (running on EC2) via a Webhook which retrieves the code from Github and pushes the relevant artifacts to AWS S3 where AWS Glue code is updated.

## Data Flow:
- When a CSV file is uploaded to the raw bucket, it initiates the data pipeline by firstly triggering a Lambda Function
- The Lambda function initiates the State Machine used as the data orchestrator
- As the first step of the state machine, a Glue job runs and reads CSV data from the raw bucket, converts the data into parquet format and saves the file in the Transformed folder of the bucket
- In the second step of the state machine, another Glue job is initiated which reads the parquet files from the previous step and saves them in the glue catalog, also writes the data in parquet format in the semantics folder of the bucket
- The user(s) can now query the bucket via Athena
