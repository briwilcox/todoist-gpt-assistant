# Todoist GPT Assistant

An AI assistant for your Todoist tasks.

Todoist GPT Assistant is a Python script designed to provide you with AI-generated suggestions to help you complete your to-do list. This script connects to your Todoist account, retrieves your most recent tasks, and uses OpenAI's advanced models (including GPT-4 and GPT-3.5-turbo) to generate step-by-step instructions on how to accomplish them. Please note that this script may update the descriptions of your tasks with these suggestions. It can also be configured to update tasks that are due today, overdue tasks, or tasks that don't have a GPT-generated description yet. It's recommended to use this feature with caution to avoid any unexpected changes to your task descriptions. With Todoist GPT Assistant, you can easily stay on top of your to-do list and streamline your productivity.

## Features

- Connects to your Todoist account and retrieves your seven most recent tasks due today or earlier that do not have a GPT-generated description yet.
- Uses OpenAI's advanced models (including GPT-4 and GPT-3.5-turbo) to analyze tasks and generate actionable suggestions. Options are included to select the model, token budget, and temperature to customize the suggestions.
- Presents suggestions in a clear, easy-to-follow format.
- Updates tasks descriptions with the generated suggestions for future reference.

## Installation

Clone this repository or download the source code.
Install the required dependencies using pip:

## Installation

Clone this repository or download the source code.
Install the required dependencies using pip:

```
pip install openai configparser todoist_api_python colorama argparse tqdm
```

Set up a todoist-config.ini file in the project directory with the following structure:

```
[todoist]
api_key = YOUR_TODOIST_API_KEY

[openai]
api_key = YOUR_OPENAI_API_KEY
```

Replace the placeholders with your respective API keys and Twilio information.

## Usage
Run the script by executing:

```
python todoist_gpt_assistant.py
```

You can also pass the following command-line arguments:

```
python todoist_gpt_assistant.py -u

python todoist_gpt_assistant.py -i

python todoist_gpt_assistant.py -d
```

-u, --update-all: Update all task descriptions that haven't been updated yet

-i, --interactive: Enable interactive mode

-d, --due-today: Only update tasks that are overdue or due today

### Example output
<img width="1184" alt="image" src="https://user-images.githubusercontent.com/3598417/233871374-ff9a2aa7-d63a-48df-b809-4098fb20b04e.png">


### Example text output

TASK: Post todoist gpt assistant python script to Github and write a readme

GPT-3.5-turbo SUGGESTION: To post the Todoist GPT Assistant Python script to GitHub and write a readme, follow these steps:

Create a GitHub account and repository.
Install Git on your computer.
Open your terminal or command prompt and navigate to the directory where your script is located.
Initialize a Git repository with the command "git init".
Add your script to the repository with the command "git add <filename>".
Commit your changes with the command "git commit -m 'Initial commit'".
Add the remote repository URL to your local repository with the command "git remote add origin <remote-repo-URL>".
Push your changes to the remote repository with the command "git push -u origin master".
Create a README.md file in your repository and add information about the script, such as its purpose, how to use it, and any dependencies.
Commit and push your changes to the repository with the commands "git add README.md" and "git commit -m 'Add README.md'".

TASK: Buy groceries

GPT-3.5-turbo SUGGESTION: Create a shopping list with all the items you need organized by category. Visit a nearby grocery store during off-peak hours to avoid crowds. Stick to your list and use a shopping cart or basket to carry your items. Check expiration dates and choose fresh produce. Pay at the cashier and bring reusable bags for an eco-friendly shopping experience.

TASK: Finish the presentation.

GPT-3.5-turbo SUGGESTION: Break the task into smaller steps: 1) Outline the presentation, including key points and supporting arguments. 2) Gather relevant data and visuals to support your arguments. 3) Create slides with a consistent design, using bullet points

## Contributing

If you'd like to contribute to the project or have any suggestions, feel free to create a pull request or open an issue. All contributions are welcome!

## Important Notes

This tool has no affiliation with Todoist the company and is a hobby project. 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Reminder:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
