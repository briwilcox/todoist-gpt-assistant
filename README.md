# Todoist GPT Assistant
An AI assistant for your todoist tasks. 

Todoist GPT Assistant is a Python script that helps you conquer your to-do list by providing AI-generated suggestions on how to complete your tasks. This script connects to your Todoist account, retrieves your most recent tasks, and uses OpenAI's GPT-3.5-turbo to generate step-by-step suggestions on how to accomplish them.

## Features

- Connects to your Todoist account and retrieves your seven most recent tasks due today or earlier
- Uses OpenAI's GPT-3.5-turbo to analyze tasks and generate actionable suggestions
- Presents suggestions in a clear, easy-to-follow format
- Optionally sends task suggestions via text message using the Twilio API

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

3. Set up a `todoist-config.ini` file in the project directory with the following structure:

```
[todoist]
api_key = YOUR_TODOIST_API_KEY

[openai]
api_key = YOUR_OPENAI_API_KEY

[twilio]
account_sid = YOUR_TWILIO_ACCOUNT_SID
auth_token = YOUR_TWILIO_AUTH_TOKEN
phone_number = YOUR_TWILIO_PHONE_NUMBER
recipient_phone_number = RECIPIENT_PHONE_NUMBER
```

Replace the placeholders with your respective API keys and Twilio information.

## Usage

Run the script by executing:

```bash
python todoist_gpt_assistant.py
```

## Example output

TASK: Post todoist gpt assistant python script to Github and write a readme

SUGGESTION: To post the Todoist GPT Assistant Python script to GitHub and write a readme, follow these steps:
1. Create a GitHub account and repository.
2. Install Git on your computer.
3. Open your terminal or command prompt and navigate to the directory where your script is located.
4. Initialize a Git repository with the command "git init".
5. Add your script to the repository with the command "git add <filename>".
6. Commit your changes with the command "git commit -m 'Initial commit'".
7. Add the remote repository URL to your local repository with the command "git remote add origin <remote-repo-URL>".
8. Push your changes to the remote repository with the command "git push -u origin master".
9. Create a README.md file in your repository and add information about the script, such as its purpose, how to use it, and any dependencies.
10. Commit and push your changes to the repository with the commands "git add

TASK: Buy groceries

SUGGESTION: Create a shopping list with all the items you need, organized by category. Visit a nearby grocery store during off-peak hours to avoid crowds. Stick to your list and use a shopping cart or basket to carry your items. Check expiration dates and choose fresh produce. Pay at the cashier and bring reusable bags for an eco-friendly shopping experience.

TASK: Finish the presentation.

SUGGESTION: Break the task into smaller steps: 1) Outline the presentation, including key points and supporting arguments. 2) Gather relevant data and visuals to support your arguments. 3) Create slides with a consistent design, using bullet points and visuals to convey information. 4) Write speaker notes to guide your delivery. 5) Rehearse the presentation, focusing on clarity, pacing, and body language. 6) Revise and refine as needed.


## Contributing

If you'd like to contribute to the project or have any suggestions, feel free to create a pull request or open an issue. All contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
