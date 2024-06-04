import os
import time
import logging
from openai import AzureOpenAI
from openai import RateLimitError

# Set up logging to print information to the console
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

# Retrieve environment variables for API configuration
openai_api_base = os.getenv('OPENAI_API_BASE')
openai_api_key = os.getenv('OPENAI_API_KEY')
ptu_deployment = os.getenv('PTU_DEPLOYMENT')
standard_deployment = os.getenv('STANDARD_DEPLOYMENT')

# Set constants for maximum retries and latency threshold
MAX_RETRIES = 0  # Maximum number of retries for API calls
PTU_MAX_WAIT = 4000  # Maximum acceptable wait time in milliseconds for PTU model

def call_ptu(client, input_messages):
    """
    Calls the PTU model of AzureOpenAI with the provided messages.

    Args:
        client (AzureOpenAI): The AzureOpenAI client.
        input_messages (list): The list of messages to be processed.

    Returns:
        response: The response from the AzureOpenAI client.
    """
    # Send request to PTU model
    response = client.chat.completions.create(
        messages=input_messages,
        model=ptu_deployment,
    )
    # Log that the response was received through PTU model
    logging.info('responded through PTU')
    return response

def call_standard(client, input_messages):
    """
    Calls the standard model of AzureOpenAI with the provided messages.

    Args:
        client (AzureOpenAI): The AzureOpenAI client.
        input_messages (list): The list of messages to be processed.

    Returns:
        response: The response from the AzureOpenAI client.
    """
    # Send request to standard model
    response = client.chat.completions.create(
        messages=input_messages,
        model=standard_deployment,
    )
    # Log that the response was received through Standard model
    logging.info('responded through Standard')    
    return response

def call_with_retries(input_messages):
    """
    Calls the AzureOpenAI client with retries in case of a RateLimitError.

    Args:
        input_messages (list): The list of messages to be processed.

    Returns:
        response: The response from the AzureOpenAI client.
    """
    # Record the start time to measure latency
    start_time = time.time()
    
    # Initialize the AzureOpenAI client with provided configuration
    client = AzureOpenAI(
        azure_endpoint=openai_api_base,
        api_key=openai_api_key,
        api_version='2024-02-01',
        max_retries=MAX_RETRIES
    )

    while True:
        try:
            # Try calling the PTU model
            return call_ptu(client, input_messages)
        except RateLimitError as e:
            # If a rate limit error occurs, calculate the retry wait time
            retry_after_ms = int(e.response.headers['retry-after-ms'])        
            elapsed_time = (time.time() - start_time) * 1000
            # Check if the total wait time exceeds the maximum allowed latency
            if elapsed_time + retry_after_ms > PTU_MAX_WAIT:
                # If it does, log and switch to the standard model
                logging.info(f"Latency {elapsed_time + retry_after_ms} ms exceeds threshold. Switching to paygo.")
                return call_standard(client, input_messages)
            else:
                # If not, log and wait for the retry time before retrying the PTU model
                logging.info(f"retrying PTU after {retry_after_ms} ms")
                time.sleep(e.retry_after / 1000)

if __name__ == "__main__":
    # Define a list of messages to be sent to the Azure OpenAI API
    input_messages= [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure AI services support this too?"}
    ]

    # Measure the total execution time for the API call
    start_time = time.time()
    response = call_with_retries(input_messages)
    end_time = time.time()
    execution_time = round(end_time - start_time, 3)
    
    # Log the total latency and the content of the response
    logging.info(f"Total latency was {execution_time} seconds.")
    logging.info(response.choices[0].message.content)
