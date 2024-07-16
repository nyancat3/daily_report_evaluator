import os
import logging
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from dotenv import load_dotenv
from openai import OpenAi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Enable process_before_response for AWS Lambda compatibility
load_dotenv()
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True
)

cached_timestamp = None

@app.message(r"\[日報\]")
def message_evaluation(message, say, ack):
    ack()
    global cached_timestamp
    timestamp, subtype = message["ts"], message.get("subtype")
    logger.info(f"cached_timestamp: {cached_timestamp}, message timestamp: {timestamp}, subtype: {subtype}")
    if timestamp == cached_timestamp or subtype != None:
        return
    cached_timestamp = timestamp
    user, text = message["user"], message["text"].replace("`", "")
    logger.info(f"text: {text}")
    evaluation = OpenAi().create_evaluation(text)
    logger.info(f"evaluation: {evaluation}")
    if "以下の指示に従って" in evaluation:
        say(f"{evaluation}")
    else:
        say(f"{evaluation}お疲れさまでした 🍵")

@app.event("message")
def handle_message_events(body):
    logger.info(f"Received message event: {body}")

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

def lambda_handler(event, context):
    if 'headers' in event and 'X-Slack-Retry-Num' in event['headers']:
        slack_retry_num = int(event['headers']['X-Slack-Retry-Num'])
        logger.info(f"X-Slack-Retry-Num: {slack_retry_num}")
        if slack_retry_num > 0:
            return { 'statusCode': 200, 'body': 'Retry ignored' }
    slack_handler = SlackRequestHandler(app=app)
    try:
        return slack_handler.handle(event, context)
    except Exception as e:
        logger.error(f"Error handling Slack event: {e}")
        return { 'statusCode': 500, 'body': 'Internal Server Error' }
