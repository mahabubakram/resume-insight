import requests
import fitz
import re
import json
import os

from gptQuery.gptCommons import CreateGPTQuery
from models import Resume


def download_file(resume: Resume):
    filename = "resume.pdf"
    is_file = os.path.isfile(filename)
    if is_file:
        os.remove(filename)
    if resume.submitted_pdf_url :
        response = requests.get(resume.submitted_pdf_url)
        if response.status_code == 200:
            file = open(filename, "wb")
            file.write(response.content)
            file.close()
            return file
    return None


def resume_parser(file):
    data = {}
    doc = fitz.open(file)
    for page in doc:  # iterate the document pages
        text = page.get_text()  # get plain text encoded as UTF-8
        regex = "[ ]*(.+):[ ]*\n?((?:.+\n?[^\s])*)"
        dataPoints = re.search(regex, text, re.MULTILINE)
        # print(dataPoints)
        # print(text)
        data[page.number] = text
    return json.dumps(data)


def gpt_task_executor(prompt_body: str, agent_task: str):
    gpt_query = CreateGPTQuery(prompt_body)
    prompt_body = prompt_body + os.linesep + agent_task

    gpt_query.PROMPT = prompt_body
    gpt_query.generate()
    #print(gpt_query.get_result())
    return gpt_query.get_result()


def is_resume(prompt) -> bool:
    agent_task = "just tell if the prompt is a Personal Resume or Not. give the answer just in boolean"
    return_value = gpt_task_executor(prompt, agent_task)
    return json.loads(return_value.lower())


def gpt_resume_insight(prompt):
    gptQuery = CreateGPTQuery(prompt)
    prompt = prompt + os.linesep \
             + "from the text above, detect the language and give me the list of professional experiences in the same language, " \
               "including their employer details and detail work experiences. " \
               "make it as a json object but list the responsibilites as a list." \
               "also provide personal information as an object," \
               "provide education as an object," \
               "provide skills as an object" \
               "and also other certifications and rewards as an object"
    gptQuery.PROMPT = prompt
    gptQuery.generate()
    # print(gptQuery.get_result())
    return gptQuery.get_result()
