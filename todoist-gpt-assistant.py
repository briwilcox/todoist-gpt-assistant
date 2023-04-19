import os
import datetime
import configparser
import openai
from todoist_api_python.api import TodoistAPI
from twilio.rest import Client
from colorama import Fore, Style, init

# Initialize colorama
init()
# Read configuration
config = configparser.ConfigParser()
config.read("todoist-config.ini")
todoist_api_key = config['todoist']['api_key']
openai_api_key = config['openai']['api_key']

# Get the seven most recent tasks that are due today or earlier, and are not repeating tasks
def get_seven_most_recent_tasks(api):
    tasks = api.get_tasks()
    tasks.sort(key=lambda task: task.due.date if task.due else '', reverse=True)
    tasks_due_today_or_earlier = [
        task for task in tasks
        if task.due and datetime.datetime.strptime(task.due.date, '%Y-%m-%d').date() <= datetime.date.today()
        and "every" not in task.due.string.lower()
    ]

    return tasks_due_today_or_earlier[:7]

# Generate a suggestion for how to accomplish a task
def generate_suggestions(task):
    prompt = f"Please suggest how to accomplish the task in under 600 characters including the task name, do not simply repeat the task in the suggestion tell me how to accomplish it with specifics: {task}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [
        {"role": "system", "content": "You are a helpful assistant."}, 
        {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

# Send a text message with a task and its suggested solution
def send_text_message(task, suggestion):
    config.read("todoist-config.ini")
    client = Client(config['twilio']['account_sid'], config['twilio']['auth_token'])
    message = f"TASK: {task}\nGPT: {suggestion}"
    client.messages.create(body=message, from_=config['twilio']['phone_number'], to=config['twilio']['recipient_phone_number'])

# Main function
def main():
    api = TodoistAPI(todoist_api_key)
    seven_most_recent_tasks = get_seven_most_recent_tasks(api)

    openai.api_key = openai_api_key

    suggestions = [generate_suggestions(task.content) for task in seven_most_recent_tasks]
    for task, suggestion in zip(seven_most_recent_tasks, suggestions):
        print(f"{Fore.GREEN}TASK: {task.content}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}SUGGESTION: {suggestion}{Style.RESET_ALL}")
        print()  # Add an empty line for readability

# Run the main function
if __name__ == "__main__":
    main()
