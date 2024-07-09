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
                        You have to rate the daily report on a scale of 0 to 100.
                        Please rate the daily report on the following points.

                        - It's clear enough to understand what the employee did that day.
                        - It doesn't miss any tasks that need to be written.
                        - It provides a conclusion for each task.

                        ## Output format
                        The output consists of a score and possible improvements in bullet points and must be in less than ten lines.
                        Minimize redundancy in your output as much as possible. Use a gentle tone ending with です/ます. Avoid a repetition. Do not include the question in the output.
                        First, give a score on a scale of 0 to 100 for the given daily report.
                        Then give possible improvements, each in less than 200 tokens.
                        Below is an example of the output style you must strictly follow.

                        {{score}}点です。
                        - {{possible improvement 1}}
                        - {{possible improvement 2}}
                        - {{possible improvement 3}}

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
