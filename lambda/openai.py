import requests
from dotenv import load_dotenv
import os

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
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"""
                        Please evaluate a given daily report of the employee.
                        You must rate the daily report on the following points.

                        - It's clear enough to understand what the employee did that day.
                        - It doesn't miss any tasks that need to be written.
                        - It provides a conclusion for each task.

                        ## Output format
                        The output consists of a score and possible improvements in bullet points and must be in less than ten lines.
                        Minimize redundancy in your output as much as possible. Use a gentle tone ending with です/ます. Avoid a repetition. Do not include the question in the output.
                        If the daily report is not good enough, give instructions for rewriting it, each in less than 200 tokens. If the daily report is good enough, just give a compliment on what is good about the daily report in less than 200 tokens.
                        Below is an example of the output style you must strictly follow.

                        ### If the daily report is not good enough and needs to be rewritten

                        以下の指示に従って、日報を書き直してみてください。
                        - {{instruction 1}}
                        - {{instruction 2}}
                        - {{instruction 3}}

                        ### If the daily report is good enough and does not need rewriting

                        良い日報ですね！{{compliment}}

                        ## Output (Output must be in Japanese)
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
            print("Response from OpenAI:", response.json())
            content = response.json()['choices'][0]['message']['content']
            return content
        else:
            print("Error:", response.status_code, response.text)
