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

variable "open_ai_api_key" {
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
  timeout          = 10
  environment {
    variables = {
      OPEN_AI_API_KEY      = var.open_ai_api_key,
      SLACK_BOT_TOKEN      = var.slack_bot_token,
      SLACK_SIGNING_SECRET = var.slack_signing_secret
    }
  }
}

resource "aws_lambda_function_event_invoke_config" "lambda_function_event_invoke_config" {
  function_name                = aws_lambda_function.lambda_function.function_name
  maximum_event_age_in_seconds = 120
  maximum_retry_attempts       = 0
}

resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name          = "lambda_layer_slack_bolt"
  filename            = data.archive_file.lambda_layer_zip.output_path
  source_code_hash    = data.archive_file.lambda_layer_zip.output_base64sha256
  compatible_runtimes = ["python3.12"]
}

resource "aws_apigatewayv2_api" "api" {
  name          = "daily-report-evaluator-api"
  protocol_type = "HTTP"
}
resource "aws_apigatewayv2_integration" "integration" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"

  integration_method = "POST"
  integration_uri    = aws_lambda_function.lambda_function.invoke_arn
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /${aws_lambda_function.lambda_function.function_name}"

  target = "integrations/${aws_apigatewayv2_integration.integration.id}"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.api.id
  auto_deploy = true
  name        = "dev"
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*/daily-report-evaluator"
}
