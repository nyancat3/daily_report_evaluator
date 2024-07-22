import requests
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class OpenAi:
    def create_evaluation(self, daily_report_text):
        load_dotenv()
        open_ai_api_key = os.getenv("OPEN_AI_API_KEY")
        if open_ai_api_key is None:
            raise ValueError("OpenAI API key is not set in environment variables.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {open_ai_api_key}"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"""
                        Please evaluate a given daily report of the employee.
                        You must evaluate the daily report based on the following points:

                        - Clarity: Is it easy to understand what the employee did that day?
                        - Completeness: Does it include all necessary tasks?
                        - Conclusion: Does it provide a conclusion for each task?

                        ## Output format
                        Minimize redundancy and avoid repetition. Use a gentle tone ending with です/ます. Do not include the question in the output.
                        If the daily report is not good enough, give instructions for rewriting it in bullet points, each under 200 tokens. If the daily report is good enough, give a compliment on what is good about it within 200 tokens.
                        Below is an example of the output style you must strictly follow.

                        ### Example Output (Must be in Japanese)

                        #### If the daily report is not good enough and needs to be rewritten

                        以下の指示に従って、日報を書き直してみてください。
                        - {{instruction 1}}
                        - {{instruction 2}}
                        - {{instruction 3}}

                        #### If the daily report is good enough and does not need rewriting

                        良い日報ですね！{{compliment}}

                        ## Output (Must be in Japanese)
                        """
                    )
                },
                {
                    "role": "user",
                    "content": f"A daily report: \n{daily_report_text}"
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            logger.info("Response from OpenAI:", response.json())
            content = response.json()['choices'][0]['message']['content']
            return content
        else:
            logger.error("Error:", response.status_code, response.text)
