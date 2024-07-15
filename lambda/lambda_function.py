import os
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from dotenv import load_dotenv
from openai import OpenAi

# Enable process_before_response for AWS Lambda compatibility
load_dotenv()
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True
)

cached_timestamp = None

@app.message("\[日報\]")
def message_evaluation(message, say, ack):
    ack()
    global cached_timestamp
    timestamp, subtype = message["ts"], message.get("subtype")
    print(f"cached_timestamp: {cached_timestamp}, message timestamp: {timestamp}, subtype: {subtype}")
    if timestamp == cached_timestamp or subtype != None:
        return
    cached_timestamp = timestamp
    user, text = message["user"], message["text"].replace("`", "")
    print(f"text: {text}")
    evaluation = OpenAi().create_evaluation(text)
    print(f"evaluation: {evaluation}")
    if "以下の指示に従って" in evaluation:
        say(f"{evaluation}")
    else:
        say(f"{evaluation}お疲れさまでした 🍵")

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

def lambda_handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
