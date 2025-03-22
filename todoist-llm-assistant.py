#!/usr/bin/env python3
import os
import datetime
import configparser
from openai import OpenAI
from todoist_api_python.api import TodoistAPI
from colorama import Fore, Style, init
import argparse
from tqdm import tqdm
import sys
import json
import time


# Initialize colorama
init()
# Read configuration
CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()
try:
    config.read(CONFIG_FILE)
    todoist_api_key = config['todoist']['api_key']
    openai_api_key = config['openai']['api_key']
    # Get preferred model from config if available, otherwise use default
    preferred_model = config['openai'].get('preferred_model', "gpt-4o-mini")
    # Get project-specific model mappings
    project_models = {}
    if 'project_models' in config:
        project_models = dict(config['project_models'])
except Exception as e:
    print(f"{Fore.RED}Error reading configuration file: {e}{Style.RESET_ALL}")
    print(f"Please make sure {CONFIG_FILE} exists with [todoist] and [openai] sections containing api_key fields.")
    sys.exit(1)

def get_model_for_project(task, cli_model):
    """
    Determine which model to use based on the task's project and CLI arguments.
    CLI model takes precedence over project-specific models.
    """
    # Available models for validation
    available_models = [
        "o3-mini", "o1", "o1-mini",  # Reasoning models
        "gpt-4o", "chatgpt-4o-latest",  # Flagship models
        "gpt-4o-mini",  # Cost-optimized models
        "gpt-4o-realtime-preview",  # Realtime models
    ]
    
    if cli_model:  # CLI argument takes precedence
        return cli_model
        
    project_id = str(task.project_id) if hasattr(task, 'project_id') and task.project_id else None
    if project_id and project_id in project_models:
        model = project_models[project_id]
        if model in available_models:  # Validate the model name
            return model
        else:
            print(f"{Fore.YELLOW}Warning: Invalid model '{model}' specified for project {project_id}. Using default model.{Style.RESET_ALL}")
    
    return preferred_model

# Get the seven most recent tasks that are due today or earlier
def get_seven_most_recent_tasks(api, offset=0, include_inbox=False, include_no_date=False):
    try:
        tasks = api.get_tasks()
        
        # Sort tasks by due date if available
        tasks.sort(key=lambda task: task.due.date if task.due else '', reverse=True)
        
        filtered_tasks = []
        
        for task in tasks:
            # Skip tasks that already have suggestions
            if "SUGGESTION" in task.description.upper():
                continue
                
            # Skip recurring tasks
            if task.due and "every" in task.due.string.lower():
                continue
                
            # Include task based on filters
            if (
                # Include due tasks (today or earlier)
                (task.due and datetime.datetime.strptime(task.due.date, '%Y-%m-%d').date() <= datetime.date.today()) or
                # Include inbox tasks if flag is set
                (include_inbox and (not hasattr(task, 'project_id') or task.project_id is None or str(task.project_id) == str(api.get_projects()[0].id))) or
                # Include tasks without due dates if flag is set
                (include_no_date and not task.due)
            ):
                filtered_tasks.append(task)
        
        return filtered_tasks[offset:offset + 7]
    except Exception as e:
        print(f"{Fore.RED}Error retrieving tasks from Todoist: {e}{Style.RESET_ALL}")
        return []

# Update task description with GPT suggestion
def update_task_description(api, task, suggestion, debug=False, no_update=False):
    try:
        task_id = task.id
        existing_content = task.description if hasattr(task, 'description') else ""
        
        # Check if the task already has a suggestion
        if "SUGGESTION" in existing_content.upper() and not update_all:
            if debug:
                print(f"Task '{task.content}' already has a suggestion. Skipping.")
            return
            
        # Combine existing content with the new suggestion
        new_description = suggestion
        
        if no_update:
            print(f"{Fore.YELLOW}Would update task '{task.content}' with new description (Skipped in demo mode){Style.RESET_ALL}")
            return
            
        # Update the task in Todoist
        api.update_task(task_id=task_id, description=new_description)
        print(f"{Fore.GREEN}✓ Updated task '{task.content}'{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error updating task '{task.content}': {e}{Style.RESET_ALL}")


# Generate a suggestion for how to accomplish a task, and select which model to use, as well as the token budget, and temperature
def generate_suggestions(client, task, model, max_tokens, temperature, debug=False, enable_fallback=False, reasoning_effort="medium", conversation_history=None):
    is_o_series_model = model.startswith('o')
    fallback_model = "gpt-4o-mini"
    
    # Prepare the prompt - Enhanced for reasoning models
    if is_o_series_model:
        system_message = {
            "role": "system",
            "content": "You are a task planning assistant that uses step-by-step reasoning to provide actionable suggestions. Your goal is to help users accomplish their tasks effectively. Adapt your response length to the task's complexity - be concise for simple tasks but provide more detail for complex ones. Focus on being specific and actionable."
        }
        
        initial_prompt = f"""Task: '{task.content}'

Please analyze this task and provide a suggestion that matches its complexity:

1. First, understand what this task requires and its scope
2. Consider the most effective approach to accomplish it
3. Think about any potential challenges, requirements, or dependencies
4. For complex tasks, break down the solution into clear steps
5. For simple tasks, provide a straightforward approach

Based on your reasoning, provide a suggestion that matches the task's complexity:
- For simple tasks: A concise 1-2 sentence suggestion
- For complex tasks: A more detailed response with specific steps or considerations
- Always be specific and actionable"""
    else:
        system_message = {
            "role": "system",
            "content": "You are a task planning assistant. Your goal is to help users accomplish their tasks effectively by providing actionable suggestions. Be concise for simple tasks and more detailed for complex ones."
        }
        
        initial_prompt = f"""For the task: '{task.content}'

Please provide a suggestion that matches the task's complexity:
- For simple tasks: A concise 1-2 sentence suggestion
- For complex tasks: A more detailed response with specific steps
Always be specific and actionable."""
    
    # Set up messages with conversation history if available
    messages = [system_message]
    
    if conversation_history:
        messages.extend(conversation_history)
    else:
        messages.append({"role": "user", "content": initial_prompt})
    
    params = {
        "messages": messages,
        "model": model,
    }
    
    # Add model-specific parameters
    if is_o_series_model:
        # o-series models (reasoning models) use different parameters
        if max_tokens is not None:
            params["max_completion_tokens"] = max_tokens
        params["reasoning_effort"] = reasoning_effort  # Can be "low", "medium", or "high"
        
        model_info = f"{model.upper()} (reasoning_effort={reasoning_effort})"
        if max_tokens is not None:
            model_info += f", max_completion_tokens={max_tokens}"
    else:
        # GPT models use max_tokens and support temperature
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        params["temperature"] = temperature
        model_info = f"{model.upper()} (temp={temperature})"
        if max_tokens is not None:
            model_info += f", max_tokens={max_tokens}"
    
    if debug:
        print(f"\n{Fore.CYAN}Debug - API call parameters:{Style.RESET_ALL}")
        print(json.dumps(params, indent=2))
    
    print(f"\n{Fore.GREEN}Generating suggestion using {model_info}...{Style.RESET_ALL}")
    
    try:
        # Make the API call
        openai_client = OpenAI(api_key=openai_api_key)
        response = openai_client.chat.completions.create(**params)
        
        # Debug response information
        if debug:
            print(f"\n{Fore.CYAN}Debug - Response object:{Style.RESET_ALL}")
            print(f"Response type: {type(response)}")
            print(f"Response has content: {hasattr(response, 'choices') and len(response.choices) > 0}")
            
            # Show reasoning tokens information if available
            if hasattr(response, 'usage') and hasattr(response.usage, 'completion_tokens_details'):
                print(f"Reasoning tokens used: {response.usage.completion_tokens_details.reasoning_tokens}")
            
        # Extract the suggestion text
        suggestion = response.choices[0].message.content.strip()
        
        # Check if suggestion is empty and retry with fallback model if needed
        if not suggestion and is_o_series_model and enable_fallback:
            print(f"{Fore.YELLOW}Warning: Received empty response from {model}. Falling back to {fallback_model}...{Style.RESET_ALL}")
            return generate_suggestions(client, task, fallback_model, max_tokens, temperature, debug, enable_fallback, reasoning_effort)
            
        if debug and suggestion:
            print(f"\n{Fore.CYAN}Debug - Generated suggestion:{Style.RESET_ALL}")
            print(suggestion)
            
        if not suggestion:
            return f"Unable to generate suggestion using {model.upper()}"
            
        return f"{model.upper()} SUGGESTION:\n{suggestion}"
    except Exception as e:
        print(f"{Fore.RED}Error generating suggestion: {str(e)}{Style.RESET_ALL}")
        if is_o_series_model and enable_fallback:
            print(f"{Fore.YELLOW}Falling back to {fallback_model}...{Style.RESET_ALL}")
            return generate_suggestions(client, task, fallback_model, max_tokens, temperature, debug, enable_fallback, reasoning_effort)
        return f"Error: {str(e)}"

def handle_interactive_suggestion(api, task, task_model, token_budget, temperature, debug, enable_fallback, reasoning_effort):
    conversation_history = [
        {"role": "user", "content": f"Task: {task.content}\n\nPlease provide a suggestion for how to accomplish this task."}
    ]
    
    current_model = task_model
    
    while True:
        # Generate suggestion with current conversation history and model
        suggestion = generate_suggestions(
            api, task, current_model, token_budget, temperature, 
            debug, enable_fallback, reasoning_effort, 
            conversation_history=conversation_history
        )
        
        print(f"{Fore.GREEN}TASK: {task.content}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{suggestion}{Style.RESET_ALL}")
        print()
        
        # Add the assistant's response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": suggestion.split("\n", 1)[1]  # Remove the "MODEL SUGGESTION:" prefix
        })
        
        print("\nChoose an option:")
        print("1. Accept and update task (y)")
        print("2. Provide additional context/feedback with same model (f)")
        print("3. Switch to another model:")
        print("   - Switch to GPT-4o-mini (m)")
        print("   - Switch to GPT-4o (g)")
        print("   - Switch to o1 (o1)")
        print("   - Switch to o3-mini (o3)")
        print("4. Provide feedback AND switch model:")
        print("   - Feedback + GPT-4o-mini (fm)")
        print("   - Feedback + GPT-4o (fg)")
        print("   - Feedback + o1 (fo1)")
        print("   - Feedback + o3-mini (fo3)")
        print("5. Skip this task (n)")
        
        choice = input("Enter your choice: ").lower()
        
        if choice in ['y', 'yes', '1']:
            update_task_description(api, task, suggestion, False, no_update=False)
            break
        elif choice in ['n', 'no', 'skip', '5']:
            print("Skipping this task.")
            break
        elif choice in ['f', '2']:
            feedback = input("\nPlease provide additional context or feedback:\n")
            conversation_history.append({"role": "user", "content": feedback})
            print(f"\nGenerating new suggestion with your feedback using {current_model.upper()}...")
            continue
        elif choice in ['m', 'mini']:
            current_model = "gpt-4o-mini"
            print(f"\nSwitching to {current_model.upper()}...")
            continue
        elif choice in ['g', 'gpt', 'gpt4o']:
            current_model = "gpt-4o"
            print(f"\nSwitching to {current_model.upper()}...")
            continue
        elif choice in ['o1']:
            current_model = "o1"
            print(f"\nSwitching to {current_model.upper()}...")
            continue
        elif choice in ['o3', 'o3mini']:
            current_model = "o3-mini"
            print(f"\nSwitching to {current_model.upper()}...")
            continue
        elif choice.startswith('f'):
            # Handle feedback + model switch combinations
            new_model = None
            if choice == 'fm':
                new_model = "gpt-4o-mini"
            elif choice == 'fg':
                new_model = "gpt-4o"
            elif choice == 'fo1':
                new_model = "o1"
            elif choice == 'fo3':
                new_model = "o3-mini"
            
            if new_model:
                feedback = input("\nPlease provide additional context or feedback:\n")
                conversation_history.append({"role": "user", "content": feedback})
                current_model = new_model
                print(f"\nGenerating new suggestion with your feedback using {current_model.upper()}...")
                continue
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Invalid choice. Please try again.")

# Parse command line arguments
def main(interactive, update_all, due_today, model_name, token_budget, temperature, debug=False, enable_fallback=False, reasoning_effort="medium", include_inbox=False, include_no_date=False):
    try:
        api = TodoistAPI(todoist_api_key)
        # Test the API connection
        api.get_tasks(limit=1)
        print(f"{Fore.GREEN}Successfully connected to Todoist API{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error connecting to Todoist API: {e}{Style.RESET_ALL}")
        print(f"Please check your API key in {CONFIG_FILE}")
        sys.exit(1)
        
    offset = 0

    while True:
        if update_all:
            try:
                tasks = api.get_tasks()
                filtered_tasks = []
                
                for task in tasks:
                    # Skip tasks that already have suggestions
                    if "SUGGESTION" in task.description.upper():
                        continue
                        
                    # Filter based on due date if flag is set
                    if due_today and task.due:
                        if datetime.datetime.strptime(task.due.date, '%Y-%m-%d').date() <= datetime.date.today():
                            filtered_tasks.append(task)
                    # Include tasks without due dates if flag is set
                    elif include_no_date and not task.due:
                        filtered_tasks.append(task)
                    # Include inbox tasks if flag is set
                    elif include_inbox and (not hasattr(task, 'project_id') or task.project_id is None or str(task.project_id) == str(api.get_projects()[0].id)):
                        filtered_tasks.append(task)
                    # Otherwise include all tasks
                    elif not due_today and not include_inbox and not include_no_date:
                        filtered_tasks.append(task)
                        
                tasks_to_update = filtered_tasks
            except Exception as e:
                print(f"{Fore.RED}Error retrieving tasks: {e}{Style.RESET_ALL}")
                sys.exit(1)
        else:
            tasks_to_update = get_seven_most_recent_tasks(api, offset, include_inbox, include_no_date)

        if not tasks_to_update:
            if update_all:
                print("No tasks to update. This is probably because you have already updated all tasks with suggestions.")
            else:
                print("No tasks found that match your current filters. Try:")
                print(" - Adding the --inbox flag to include inbox tasks")
                print(" - Adding the --no-due-date flag to include tasks without due dates")
                print(" - Adding tasks with due dates set to today or earlier")
            break

        # Wrap tasks_to_update with tqdm to show progress bar
        for task in tqdm(tasks_to_update, desc="Updating tasks", unit="task"):
            # Get the appropriate model for this task
            task_model = get_model_for_project(task, model_name)
            if task_model != model_name:
                print(f"\n{Fore.CYAN}Using model {task_model} for project {task.project_id}{Style.RESET_ALL}")
            
            if interactive and not update_all:
                handle_interactive_suggestion(api, task, task_model, token_budget, temperature, debug, enable_fallback, reasoning_effort)
            else:
                suggestion = generate_suggestions(api, task, task_model, token_budget, temperature, debug, enable_fallback, reasoning_effort)
                print(f"{Fore.GREEN}TASK: {task.content}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}{suggestion}{Style.RESET_ALL}")
                print()
                update_task_description(api, task, suggestion, update_all, no_update=False)

        if not interactive or update_all:
            break

        while True:
            print("\nChoose an option:")
            print("1. Get advice on the next 7 tasks. (Type 1, n, or next to continue)")
            print("2. Quit. Type 2, q, or quit to quit.")

            choice = input("Enter the number of your choice: ")

            if choice == "1" or choice.lower() in ["n", "next"]:
                offset += 7
                break
            elif choice == "2" or choice.lower() in ["q", "quit"]:
                print("Goodbye!")
                exit(0)
            else:
                print("Invalid choice. Please try again.")


# Run the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate suggestions for Todoist tasks")
    # Add arguments for task selection and update behavior
    parser.add_argument("-u", "--update-all", help="Update all task descriptions that haven't been updated yet", action="store_true")
    parser.add_argument("-i", "--interactive", help="Enable interactive mode", action="store_true")
    parser.add_argument("-d", "--due-today", help="Only update tasks that are overdue or due today", action="store_true")
    parser.add_argument("--inbox", help="Include tasks from inbox (default: only tasks with due dates)", action="store_true")
    parser.add_argument("--no-due-date", help="Include tasks without a due date (default: only tasks with due dates)", action="store_true")
    
    available_models = [
        "o3-mini", "o1", "o1-mini",  # Reasoning models
        "gpt-4o", "chatgpt-4o-latest",  # Flagship models
        "gpt-4o-mini",  # Cost-optimized models
        "gpt-4o-realtime-preview",  # Realtime models
    ]
    
    # Add arguments for OpenAI API configuration with updated model choices (removed audio and legacy models)
    parser.add_argument("-m", "--model", 
                      help="OpenAI model to use (overrides config file)", 
                      choices=available_models, 
                      default=preferred_model)
    parser.add_argument("-t", "--tokens", 
                      help="Maximum tokens for the OpenAI API request (optional, no limit if not specified)", 
                      type=int, 
                      default=None)
    parser.add_argument("-temp", "--temperature", 
                      help="Temperature for the OpenAI API request (0.0-2.0)", 
                      type=float, 
                      default=0.7)
    parser.add_argument("--debug", help="Enable debug mode", action="store_true")
    parser.add_argument("--fallback", help="Enable fallback to gpt-4o-mini when errors occur with o-series models", action="store_true")
    parser.add_argument("--reasoning", help="Reasoning effort for o-series models (low, medium, high)", choices=["low", "medium", "high"], default="medium")
    
    args = parser.parse_args()
    
    # Validate temperature range
    if args.temperature < 0.0 or args.temperature > 2.0:
        print(f"{Fore.RED}Error: Temperature must be between 0.0 and 2.0. Using default of 0.7.{Style.RESET_ALL}")
        args.temperature = 0.7
    
    main(args.interactive, args.update_all, args.due_today, args.model, args.tokens, args.temperature, args.debug, args.fallback, args.reasoning, args.inbox, args.no_due_date)
