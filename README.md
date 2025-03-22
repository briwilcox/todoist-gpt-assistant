# Todoist LLM Assistant

An AI assistant for your Todoist tasks.

Todoist LLM Assistant transforms how you approach your to-do list by leveraging advanced AI models to provide personalized, actionable guidance for completing your tasks. This powerful command-line tool connects seamlessly to your Todoist account, analyzes your tasks, and generates step-by-step instructions tailored to each item's complexity.

Currently powered by state-of-the-art language models, the assistant adapts its suggestions to match your needs. The interactive mode lets you refine suggestions through feedback, while project-specific model configuration ensures you get the perfect balance of insight and efficiency for different types of work.

Whether you're tackling complex projects that need detailed breakdowns or simple tasks requiring quick guidance, Todoist LLM Assistant helps you turn overwhelming to-do lists into achievable action plans.

## Features

- Automatically generates actionable suggestions for your Todoist tasks
- Updates task descriptions with AI-generated suggestions
- Supports project-specific model selection via config file
- Interactive mode with feedback loop for refining suggestions
- Currently supports models from OpenAI, including:
  - **Reasoning models**: o3-mini, o1, o1-mini
  - **Flagship models**: gpt-4o, chatgpt-4o-latest
  - **Cost-optimized models**: gpt-4o-mini
  - **Realtime models**: gpt-4o-realtime-preview
- Designed with an extensible architecture to support additional AI providers in the future
- Optional fallback to reliable models when issues occur (via --fallback flag)
- Configurable reasoning effort for compatible models (low, medium, high)
- Interactive mode for reviewing suggestions before updating tasks
- Batch processing mode for updating all tasks at once
- Colorful terminal output for fun
- Set a preferred model in the config file

## Installation

1. Clone this repository:
```bash
git clone https://github.com/briwilcox/todoist-llm-assistant.git
cd todoist-llm-assistant
```

2. Install the required packages:
```bash
pip install openai todoist-api-python colorama tqdm
```

3. Set up your configuration file:
```bash
cp config.ini.template config.ini
```

4. Edit `config.ini` with your API keys and model preferences:
- Get your Todoist API key from [Todoist Integrations](https://todoist.com/app/settings/integrations)
- Get your OpenAI API key from [OpenAI API Keys](https://platform.openai.com/api-keys)
- Set your preferred model (defaults to gpt-4o-mini if not specified)
- Optionally specify different models for specific projects

```ini
[todoist]
api_key = YOUR_TODOIST_API_KEY_HERE

[openai]
api_key = YOUR_OPENAI_API_KEY_HERE
preferred_model = gpt-4o-mini

[project_models]
# Optional: Specify different models for specific projects
# Use your project IDs from Todoist
2023456789 = o1           # Use o1 for complex project
2023456790 = gpt-4o      # Use gpt-4o for creative project
# Projects not listed here will use the preferred_model
```

> **Note**: To find your project ID in Todoist:
> 1. Open the project in your web browser
> 2. The project ID is the number in the URL after `/project/`
> 3. For example, in `https://todoist.com/app/project/2023456789`, the ID is `2023456789`

## Model Selection Priority

The script selects which model to use for each task in the following order:

1. Command-line argument (`--model`): If specified, this overrides all other settings
2. Project-specific model: If the task's project ID is listed in the `[project_models]` section
3. Default model: The `preferred_model` from the `[openai]` section

## Usage

### Basic Usage

Generate suggestions for the first 7 tasks due today or earlier:

```bash
python todoist-llm-assistant.py
```

### Command-Line Options

```
usage: todoist-llm-assistant.py [-h] [-u] [-i] [-d] [--inbox] [--no-due-date]
                               [-m {o3-mini,o1,o1-mini,gpt-4o,chatgpt-4o-latest,
                                   gpt-4o-mini,gpt-4o-realtime-preview}]
                               [-t TOKENS] [-temp TEMPERATURE] [--debug] [--fallback]
                               [--reasoning {low,medium,high}]

Generate suggestions for Todoist tasks

options:
  -h, --help            show this help message and exit
  -u, --update-all      Update all task descriptions that haven't been updated yet
  -i, --interactive     Enable interactive mode
  -d, --due-today       Only update tasks that are overdue or due today
  --inbox               Include tasks from inbox even without due dates
  --no-due-date         Include tasks without a due date
  -m MODEL, --model MODEL
                        OpenAI model to use (overrides config file setting)
  -t TOKENS, --tokens TOKENS
                        Maximum tokens for the OpenAI API request (optional, no limit if not specified)
  -temp TEMPERATURE, --temperature TEMPERATURE
                        Temperature for the OpenAI API request (0.0-2.0)
  --debug               Enable debug mode for troubleshooting
  --fallback            Enable fallback to gpt-4o-mini when errors occur with o-series models
  --reasoning {low,medium,high}
                        Reasoning effort for o-series models (default: medium)
```

### Examples

1. Use GPT-4o (flagship model) for high-quality suggestions:
```bash
python todoist-llm-assistant.py --model gpt-4o
```

2. Use o1 (high-intelligence reasoning model) for complex tasks:
```bash
python todoist-llm-assistant.py --model o1
```

3. Use your preferred model set in config.ini:
```bash
python todoist-llm-assistant.py
```

4. Update all tasks in interactive mode:
```bash
python todoist-llm-assistant.py --update-all --interactive
```

5. Only process tasks due today or earlier with higher creativity:
```bash
python todoist-llm-assistant.py --due-today --temperature 1.0
```

6. Use a specific token limit (optional):
```bash
python todoist-llm-assistant.py --tokens 300
```

7. Run without token limit for unrestricted responses:
```bash
python todoist-llm-assistant.py
```

8. Run with debug mode to troubleshoot API issues:
```bash
python todoist-llm-assistant.py --debug
```

9. Use o3-mini with fallback to gpt-4o-mini if errors occur:
```bash
python todoist-llm-assistant.py --model o3-mini --fallback
```

10. Use o1 with high reasoning effort for complex tasks:
```bash
python todoist-llm-assistant.py --model o1 --reasoning high
```

11. Use o3-mini with low reasoning effort for faster responses:
```bash
python todoist-llm-assistant.py --model o3-mini --reasoning low
```

12. Process all tasks in your inbox:
```bash
python todoist-llm-assistant.py --inbox
```

13. Process all tasks without due dates:
```bash
python todoist-llm-assistant.py --no-due-date
```

14. Process all tasks (with or without due dates, including inbox tasks):
```bash
python todoist-llm-assistant.py --inbox --no-due-date
```

## Model Compatibility

The script currently handles API differences between OpenAI model types:

- **o-series models** (Reasoning models):
  - Uses `max_completion_tokens` parameter instead of `max_tokens`
  - Uses `reasoning_effort` parameter (low, medium, high) to control how much "thinking" the model does
  - Does not support the `temperature` parameter (temperature settings are ignored when using these models)
  - Optional fallback to gpt-4o-mini if errors or empty responses occur (requires --fallback flag)
  - These models generate internal "reasoning tokens" (not visible) before providing a response
  - O-series models are designed for complex reasoning and problem-solving

- **GPT models** (gpt-4o, gpt-4o-mini, etc.): 
  - Uses `max_tokens` parameter
  - Supports the `temperature` parameter for controlling creativity
  - Does not use reasoning tokens or reasoning effort

The codebase is designed to accommodate additional model providers in future updates, with appropriate API adaptations.

> **Note**: When using o-series models, any temperature value specified via the command line will be ignored since these models don't support temperature control. Use the `--reasoning` flag to control how much "thinking" the model does instead. If you experience issues with o-series models, you can use the `--fallback` flag to automatically fall back to gpt-4o-mini.

## How It Works

1. The script connects to both the Todoist API and OpenAI API
2. It retrieves your tasks from Todoist
3. For each task, it asks the AI to generate a suggestion on how to accomplish it
4. The suggestion is added to the task description in Todoist
5. Tasks are marked with the model name (e.g., "MODEL SUGGESTION:")

## Interactive Mode

When running in interactive mode (`-i` or `--interactive`), you can:
1. Review each suggestion before it's applied
2. Provide additional context or feedback to get refined suggestions
3. Escalate to more powerful models when needed
4. Accept or skip suggestions for each task

### Model Escalation

The interactive mode allows you to start with a simpler model (like gpt-4o-mini) and escalate to more powerful models only when needed:

* Switch directly to another model for the current task
* Provide feedback AND switch models simultaneously
* Continue with the same model and just provide feedback
* Accept the suggestion at any point

This approach helps optimize both cost and performance by using more expensive models only when necessary.

Example interactive session:
```bash
python todoist-llm-assistant.py -i

TASK: Write documentation for new feature
MODEL SUGGESTION:
Create comprehensive documentation covering installation, usage, and examples...

Choose an option:
1. Accept and update task (y)
2. Provide additional context/feedback with same model (f)
3. Switch to another model:
   - Switch to GPT-4o-mini (m)
   - Switch to GPT-4o (g)
   - Switch to o1 (o1)
   - Switch to o3-mini (o3)
4. Provide feedback AND switch model:
   - Feedback + GPT-4o-mini (fm)
   - Feedback + GPT-4o (fg)
   - Feedback + o1 (fo1)
   - Feedback + o3-mini (fo3)
5. Skip this task (n)

# To provide feedback and switch to a more powerful model:
> fo1
Please provide additional context or feedback:
> Please include API reference section and troubleshooting guide, and make it more concise.

Generating new suggestion with your feedback using O1...
```

The model maintains conversation context throughout the session, so each refinement builds upon previous feedback, regardless of which model is used.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
