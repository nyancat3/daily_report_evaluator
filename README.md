# daily_report_evaluator

A Slack app to evaluate daily reports

## Slack app

https://api.slack.com/apps

Create New App

Subscribe to Bot Events

- `message.channels` listens for messages in public channels that your app is added to
- `message.groups` listens for messages in 🔒 private channels that your app is added to

## Library

https://github.com/SlackAPI/bolt-python

Socket vs HTTPS -> HTTPS

## Infrastructure

[Create and distribute a slack bot with python and AWS in 1 hour](https://medium.com/analytics-vidhya/create-and-distribute-a-slack-bot-with-python-and-aws-in-1-hour-41c4a6c0f99d)

- Lambda
- API Gateway (HTTP API)

### Terraform

https://developer.hashicorp.com/terraform/tutorials/aws-get-started

```bash
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
```

```bash
terraform init
terraform plan
terraform validate
terraform apply
```

terraform.tfvars

```hcl
aws_region     =
aws_account_id =
```

To make access keys more secure;

- https://docs.aws.amazon.com/prescriptive-guidance/latest/terraform-aws-provider-best-practices/security.html
- https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services

## Lambda Function

https://slack.dev/bolt-python/tutorial/getting-started-http


```bash
python3 -m venv .venv
source .venv/bin/activate
```

https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment

```bash
source deactivate
```

```bash
export SLACK_SIGNING_SECRET=<your-signing-secret>
export SLACK_BOT_TOKEN=xoxb-<your-bot-token>
```

```bash
pip install -r requirements.txt
```

```bash
python3 lambda/lambda_function.py
```

## Lambda Layer

The layer path should be `python`
https://docs.aws.amazon.com/lambda/latest/dg/packaging-layers.html

```bash
pip install -r requirements.txt -t ./build/python/
```
