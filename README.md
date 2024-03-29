# Galactic Core Service

Service will provide configurations to following services

- `Bifrost`

- `Webb`

- `Stormbreaker`

- `Wormhole`

## Local Setup

Currently, Python version used for this flask server is 3.9.1

### For MAC OS,

Setup all pre-requisite in local using

```bash
make setup
```

When above commands ae run, below steps are performed in background

1. Install relevant python version
2. Create virtual environment and activate it
3. Install all requirements

### For all other operating system

Need to perform below steps manually

For running application Python version required is 3.9.1, check locally installed python version using

```bash
python3 --version 

or 

python --version
```

If Python version is not 3.9.1, need to install it (can install multiple python version)

Create a virtual environment to run a local application server with all required dependencies and connect to your
Snowflake account for data access.

Create a virtual environment locally:

```bash
venv --python=python3
source ./venv/bin/activate
pip install -r requirements.txt
```

## Starting Server

### For MAC OS

Start application in local mode using

```bash
make run
```

### For all other OS

Start the local server:

```bash
source ./venv/bin/activate
python run.py
```

Note : Before starting service in local, the env variables need to be set.

## Invocation

After successful startup, you can call the created application via HTTP:

```bash
curl http://localhost:5000/v1

or

curl http://127.0.0.1:5000/v1
```

Which should result in the following response:

```text
Welcome to the frickin' Galactic Core.
```

## Setting up new environments

1. Make sure all the infra is up using terraform
2. Snowflake Setup
    - Creating a DB `ROSTRA` and schema `CONFIGURATION`
    - Creating a service user `<ENV>_GALACTIC_CORE_SVC_USR` with below permission granted.
    ```sql
    <insert grant statements here>
   <use <var> notation for dyanamic inputs>
    ```
    - Create key pair authentication by referring to https://docs.snowflake.com/en/user-guide/key-pair-auth
    - Set public key on svc uyser & store private key and passphrase used in SSM parameter store at:
   ```text
   /galactic_core/<ENV>/SNOWFLAKE_PRIVATE_KEY
   /galactic_core/<ENV>/SNOWFLAKE_PRIVATE_KEY_PASSWORD
    ```
    - Apart from this we also need to store few more ssm secrets:
   ```text
   /galactic_core/<ENV>/SNOWFLAKE_ACCOUNT
   /galactic_core/<ENV>/SNOWFLAKE_DATABASE
   /galactic_core/<ENV>/SNOWFLAKE_USER
   /galactic_core/<ENV>/SNOWFLAKE_SCHEMA
   /galactic_core/<ENV>/SNOWFLAKE_WAREHOUSE
   /galactic_core/<ENV>/SNOWFLAKE_ROLE
   /galactic_core/<ENV>/SNOWFLAKE_REGION
    ```
3. We need to add below secrets related to User Pool
   ```text
   /galactic_core/<ENV>/COGNITO_USERPOOL_ID
   /galactic_core/<ENV>/COGNITO_ISSUER (cognito domain)
   /galactic_core/<ENV>/COGNITO_REGION
   ```
4. The app setup is complete, Please follow the steps below to setup github secrets and assume roles.

### Setting up GitHub Action

#### Prerequisites

We should have AWS assume role stored in GitHub secrets with following naming convention `<ENV>`_AWS_ASSUME_ROLE (For
Eg, DEV_AWS_ASSUME_ROLE). It will be responsible majorily for following purposes:

- `Pushing build images to ECR`

- `Deploying task definitions to ECS`

- `Fetching secrets from AWS SSM parameters`

#### Assume role permissions.

### 2.Assume role permissions.
`<ENV>`_AWS_ASSUME_ROLE set for each environment is currently provided with following Permission policies as stated below.
### 2.Assume role permissions.
`<ENV>`_AWS_ASSUME_ROLE set for each environment is currently provided with following Permission policies as stated below.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:CompleteLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:InitiateLayerUpload",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage"
            ],
            "Resource": [
                "arn:aws:ecr:`<REGION>`::repository/`<ENV>`-`<APP_NAME>`-ecr"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "ecr:GetAuthorizationToken",
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameters"
            ],
            "Resource": [
                "arn:aws:ssm:`<REGION>`:`<ACCOUNT_ID>`:parameter/`<APP_NAME>`/`<ENV>`/workflow/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:UpdateService",
                "iam:PassRole",
                "ecs:DescribeServices"
            ],
            "Resource": [
                "arn:aws:ecs:`<REGION>`:`<ACCOUNT_ID>`:service/`<ENV>`-`<APP_NAME>`-ecscluster/`<ENV>`-`<APP_NAME>`-web-service",
                "arn:aws:iam::`<ACCOUNT_ID>`:role/`<ENV>`-`<APP_NAME>`-`<WEB_SUFFIX>`-ecs-execution-role"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RegisterTaskDefinition"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

#### Setting up SSM parameters

For each environment SSM parameters with similar naming convention <app_name>/`<env>`/workflow/<variable> needs to be
created.
here is an example of a galactic core dev environment below.

   ```text
   /galactic_core/dev/workflow/ECR : It stores the ECR domain name.
   /galactic_core/dev/workflow/ECS_ACCOUNT_ID : The account ID of the account where ECS cluster is located.
   /galactic_core/dev/workflow/ECS_CLUSTER : Name of the ECS cluster.
   /galactic_core/dev/workflow/ECS_SERVICE_NAME : Name of the ECS service created. Not including `<env>` prefix and service suffix.
   /galactic_core/dev/workflow/ECR_IMAGE_REPO: It stores ECR repository name.
   ```