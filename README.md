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

## Steps for Creating the CI/CD Pipeline:

### Step 1: Launch an EC2 instance and Install Jenkins
- Launch an EC2 instance. Navigate to EC2 in your AWS Console:
![Search EC2](/assets/images/search_ec2.png)

- With the basic configurations, launch an EC2 instance (Select Ubuntu AMI while launching EC2):
![Launch EC2](/assets/images/launch_ec2.png)

- Once the EC2 instance is created, click on "Connect" button and connect using "EC2 Instance Connect":
![Connect EC2](/assets/images/connect_ec2.png)
![EC2 Instance Connect](/assets/images/ec2_instance_connect.png)

- After connecting to EC2 instance, run all the following commands:
    - sudo apt update
    - sudo apt install openjdk-11-jre
    - java -version
    - sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
    - echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
    - sudo apt-get update
    - sudo apt-get install jenkins
    - sudo systemctl enable jenkins
    - sudo systemctl start jenkins
    - sudo systemctl status jenkins

- Next step is to verify the installation. But before that, we need to configure port 8080 of EC2 for Jenkins. To do that, navigate to appropriate security group attached and create an inbound rule for port 8080 as shown in image below:
![Jenkins EC2 Inbound Rule](/assets/images/jenkins_ec2_inbound_rule.png)

- Open any browser on your local machine and copy paste the IP address of your EC2 instance followed by the port ":8080" as shown below and hit enter. Make sure that the EC2 is up and running and Jenkins has been started as part of the commands executed above:
![Launch Jenkins](/assets/images/launch_jenkins_browser.png)

- You will see a Jenkins Login page. This is a confirmation that we have installed Jenkins successfully:
![Jenkins Login](/assets/images/jenkins_login.png)


### Step 2: Configure Jenkins and Create SSH key in GitHub
#### Configure Jenkins
- To unlock Jenkins, go to CMD and get the password saved on the server using "cat" command as shown below:
    - sudo cat /var/lib/jenkins/secrets/initialAdminPassword

- Copy and paste the password in the browser - Jenkins webpage to unlock it:
![Unlock Jenkins](/assets/images/unlock_jenkins.png)

- Install the recommended plugins by clicking on "Install suggested plugins" button:
![Install Recommended Plugins for Jenkins](/assets/images/install_plugins_jenkins.png)

- Create a new user by filling in required details and click on "Save and Continue":
![Create User for Jenkins](/assets/images/create_user_jenkins.png)

- Keep the Jenkins URL as it is and click on "Save and Continue". Please make sure the URL contains the IP of your EC2 instance followed by ":8080". This is the last step of setting up Jenkins server. You should be able to see the Jenkins dashboard:
![Jenkins URL](/assets/images/jenkins_url.png)

- After successfully configuring Jenkins, we will now integrate GitHub with Jenkins.

#### Setup Github and Create SSH Key
- Initially, we will create a rsa keypair on the server using "ssh-keygen" command. Press "Enter" three times to keep the key directory as default (/home/ubuntu/.ssh/id_rsa.pub):
![SSH Keygen CMD](/assets/images/ssh_keygen_cmd.png)

- Run the following commands:
    - cd .ssh
    - ls
    - sudo cat id_rsa.pub

- After navigating to ".ssh" folder, you will see the private and public key created. "id_rsa" is the private key and "id_rsa.pub" is the public key. Copy the public key (id_rsa.pub) which will be pasted in GitHub while adding a new SSH key:
![Private and Public Keys](/assets/images/keys_cmd.png)

- Navigate to GitHub and click on the profile picture on the top right corner to open a drop-down menu. Click on "Settings".

- Settings page will open. Scroll down and click on "SSH and GPG keys". Click on "New SSH key":
![Github Settings - SSH and GPG Keys](/assets/images/github_settings.png)

- Give an appropriate name and paste the public key (id_rsa.pub) which was copied from EC2 instance and click "Add SSH key" to give GitHub access to our EC2 server:
![Add SSH Key](/assets/images/add_ssh_key.png)

- Create a new repository in Github and push the code, If you create a public repository, you won't have to add the Github credentials in Jenkins. If it's a private repository, you will have to create Jenkins Github credentials while creating the pipeline explained in the next section.

### Step 3: Install Plugins and Create a new Jenkins pipeline
#### Install Plugins and Configure Access Token
- Navigate to "Manage Jenkins" to install the "AWS Credentials" and "S3 Publisher" plugins:
![Manage Jenkins - Install Plugins](/assets/images/manage_jenkins_plugins.png)

- Navigate to "Available plugins" and search for "AWS Credentials" and then "S3 Publisher" in the search bar and install. Restart Jenkins once the plugins are installed.

- Before the next step, please make sure that you have generated the Security credentials(Access Key and Secret Access Key) for your AWS IAM User.
![Security Credentials - AWS](/assets/images/security_credentials_aws.png)

- Once restarted, configure AWS S3 Profiles available in Jenkins. You can do these configurations by visiting Manage Jenkins -> System and scroll down until you find AWS S3 Profiles configurations. Provide the necessary details (AWS Access Key ID & Secret Access Key for your IAM User) and save the profile.
![Create S3 Profile in Jenkins](/assets/images/create_s3_profile_jenkins.png)

- To add the access token required for Github Webhook, Navigate to Manage Jenkins -> Security -> Git plugin notifyCommit access tokens. Give an appropraite name to your project and generate the token. Copy the generated token:
![Github Webhook Token](/assets/images/github_webhook_token.png)

- Navigate to your Github Repository Settings -> Webhooks:
![Github Repo Settings](/assets/images/github_repo_settings.png)
![Github Repo Settings](/assets/images/github_repo_settings_webhooks.png)

- Add a Webhook for your repository, give the URL(http://EC2_IP_ADDRESS:8080/github-webhook/) in the "Payload URL" box and paste the access token from Jenkins generated in the previous step in the "Secret" box. Keep rest of the settings as shown:
![Github - Add Webhook](/assets/images/github_add_webhook.png)

#### Create a new Jenkins Pipeline
- As we have installed all the necessary tools, we can start creating our Jenkins pipeline. Navigate back to Jenkins webpage and click on "Create a job" link:
![Create Jenkins Job](/assets/images/create_jenkins_job.png)

- Give an appropriate name (give hyphens in the name), select "Freestyle project" and click on "OK" button.
![Freestyle Project](/assets/images/freestyle_project_jenkins.png)

- Next step is to give a proper description and select "GitHub project" option as per the image. Copy paste your Git repository (URL) in the input field:
![Jenkins Pipeline - General Config](/assets/images/jenkins_pipeline_general_config.png)

- Our source code will be in GitHub, so we need to select GitHub as our "source code management" option. Paste the Git repository (URL). Specify the branch:
![Jenkins Pipeline - Source Code](/assets/images/jenkins_pipeline_source_config.png)

- If your repository is public, these steps can be SKIPPED otherwise :

    - Create credentials for Jenkins. A new window will pop up. This credential will validate the GitHub SSH key (created in Step 2):

    - Copy the private key (id_rsa) from the server which we had created earlier in Step 2. Copy the entire section:

    - Select the configurations as below. Paste the private key under "Private key" section as shown below and click on "Add" button. Select the created credentials from the drop-down list:

- Enable the "Github hook trigger for GitSCM Polling" checkbox:
![Jenkins Pipeline - Build Trigger](/assets/images/jenkins_pipeline_build_trigger.png)

- Add a Post-Build Action, Select "Publish Artifacts to S3" and provide the necessary details as shown below:
![Jenkins Pipeline - Post Build Action](/assets/images/jenkins_pipeline_post_build.png)

- Keep the rest of the configurations as-is. Save the project:
![Jenkins Pipeline - Save](/assets/images/jenkins_pipeline_save.png)

- Jenkins pipeline is created with GitHub as a source code repository. Whenever a push is made to the repository, it will deploy the relevant code on S3 used as source for Glue. PLease go through the next section for setting up the Data Pipeline before testing the CI/CD Pipeline.

### Add-on Step: Secure your Jenkins app by mapping the endpoint to https
-


## Steps for Creating the Data Pipeline:
Since this is a POC, we are creating the resources manually from the console. These can also be created through an IaC script (not included in scope).

### Step 1: Create an S3 Bucket
- Go to the AWS Management Console and search "S3", create a bucket with the relevant name. Create the following folders:
    - raw
    - transformed
    - semantics
    - scripts
        - aws_glue
            - raw_to_transformed
            - transformed_to_semantics
    - aws_glue (optional)
        - athena (can be used for storing Athena logs, optional)
        - sparkHistoryLogs (can be used for storing Spark UI logs, optional)
        - temporary (can be used as a working directory for glue, optional)
    
    ![S3 Folder Structure](/assets/images/s3_jenkins_glue_data_pipeline.png)

### Step 2: Create Glue Jobs
- Go to the AWS Management Console and search "iam". Create a role to be used by the relevant glue jobs for accessing the S3 bucket. Refer to the "scripts/iam/glue_role.json" file in the repository. Please note that we have used full access policies for now but these can be fine-grained.

- Go to the AWS Management Console and search "glue". Navigate to the ETL Jobs sections and create the relevant jobs below. Use the code provided in the repository as the base code initially.

    - Job: raw_to_transformed 
        - Refer to "scripts/aws_glue/raw_to_transformed/raw-to-transformed-jenkins-pipeline-test.py" to be used as baseline code
        - Configure the job details as below:
            - Select the role created above in the IAM Role section
            - Update the "Requested number of workers" to 2
            - In Advanced properties, update the "Script path" to s3://YOUR_S3_BUCKET/scripts/aws_glue/raw_to_transformed/ (**IMPORTANT** as this folder is updated as part of the CI/CD pipeline)
    ![Glue Job - Raw to Transformed](/assets/images/glue_raw_to_transformed_code.png)
    
    - Job: transformed_to_semantics 
        - Refer to "scripts/aws_glue/transformed_to_semantics/transformed-to-semantics-jenkins-pipeline-test.py" to be used as baseline code
        - Configure the job details as below:
                - Select the role created above in the IAM Role section
                - Update the "Requested number of workers" to 2
                - In Advanced properties, update the "Script path" to s3://YOUR_S3_BUCKET/scripts/aws_glue/transformed_to_semantics/ (**IMPORTANT** as this folder is updated as part of the CI/CD pipeline)
    ![Glue Job - Transformed to Semantics](/assets/images/glue_transformed_to_semantics_code.png)

    - Job Config Example:
    ![Job Config Example](/assets/images/glue_job_config.png)
    ![Job Config Example](/assets/images/glue_job_config-1.png)
    ![Job Config Example](/assets/images/glue_job_config-2.png)
    ![Job Config Example](/assets/images/glue_job_config-3.png)

### Step 3: Create a State Machine
- Go to the AWS Management Console and search "Step Functions". Create a State Machine and provide an appropriate name

- Refer to the "scripts/state_machine/sfn_jenkins_pipeline_test.json" file for the definition of your state machine

- Replace the JobName parameters with your glue jobs (created in Step 2)

- The State Machine automatically creates the required roles but a reference has been provided in this repository ("scripts/iam/state_machine_role.json")

![State Machine Definition](/assets/images/state_machine_def.png)

### Step 4: Create a Lambda Function
- Go to the AWS Management Console and search "iam". Create a role to be used by the lambda function for initiating the state machine. Refer to the "scripts/iam/lambda_role.json" file in the repository. Please note that we have used full access policies for now but these can be fine-grained.

- Go to the AWS Management Console and search "Lambda". Create a Lambda function and provide an appropriate name
    - Select Runtime as Python 3.11
    - Select Architecture as x86_64
    - For Permissions, select "Choose an existing role" and select the role created in the previous step

- Refer to the "scripts/aws_lambda/initiate_step_function.py" file for the lambda code

- Add trigger to the lambda function. This will help initiate the data pipeline whenever a new CSV file is uploaded to the "raw" of your S3 bucket as shown below:
![Lambda Trigger - S3](/assets/images/lambda_trigger_s3.png)


## Final Notes
This concludes the PoC of creating a Jenkins CI/CD Pipeline to update Glue scripts running as part of a Data Pipeline. Please note that we can also add the Lambda code as part of the CI/CD process using Jenkins but this was not in scope. Also, we can automate the whole infrastructure deployment using Jenkins as well.
