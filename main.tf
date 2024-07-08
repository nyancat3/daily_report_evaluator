terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.2.0"
}

variable "aws_region" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "slack_bot_token" {
  type = string
}

variable "slack_signing_secret" {
  type = string
}

provider "aws" {
  region = var.aws_region
}

resource "aws_iam_role" "lambda_role" {
  name = "daily_report_evaluator_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name = "daily_report_evaluator_lambda_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:log-group:/aws/lambda/daily-report-evaluator:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

data "archive_file" "lambda_layer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/build"
  output_path = "${path.module}/lambda_layer_slack_bolt.zip"
}

resource "aws_lambda_function" "lambda_function" {
  function_name    = "daily-report-evaluator"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  depends_on       = [aws_iam_role_policy_attachment.lambda_policy_attachment]
  layers           = [aws_lambda_layer_version.lambda_layer.arn]
  environment {
    variables = {
      SLACK_BOT_TOKEN      = var.slack_bot_token,
      SLACK_SIGNING_SECRET = var.slack_signing_secret
    }
  }
}

resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name          = "lambda_layer_slack_bolt"
  filename            = data.archive_file.lambda_layer_zip.output_path
  source_code_hash    = data.archive_file.lambda_layer_zip.output_base64sha256
  compatible_runtimes = ["python3.12"]
}
