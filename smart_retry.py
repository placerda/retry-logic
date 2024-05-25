import os
import time
import logging
from openai import AzureOpenAI
from openai import RateLimitError

# Set up logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

openai_api_base = os.getenv('OPENAI_API_BASE')
openai_api_key = os.getenv('OPENAI_API_KEY')
ptu_deployment = os.getenv('PTU_DEPLOYMENT')
standard_deployment = os.getenv('STANDARD_DEPLOYMENT')

MAX_RETRIES = 0 # Set your max number of retries
PTU_MAX_WAIT = 4000  # Latency threshold in milliseconds

def call_ptu(client, input_messages):
    """
    Calls the PTU model of AzureOpenAI with the provided messages.

    Args:
        client (AzureOpenAI): The AzureOpenAI client.
        input_messages (list): The list of messages to be processed.

    Returns:
        response: The response from the AzureOpenAI client.
    """
    response = client.chat.completions.create(
        messages=input_messages,
        model=ptu_deployment,
    )
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
    response = client.chat.completions.create(
        messages=input_messages,
        model=standard_deployment,
    )
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
    start_time = time.time()
    client = AzureOpenAI(
        azure_endpoint=openai_api_base,
        api_key=openai_api_key,
        api_version='2024-02-01',
        max_retries=MAX_RETRIES
    )

    while True:
        try:
            return call_ptu(client, input_messages)
        except RateLimitError as e:
            retry_after_ms = int(e.response.headers['retry-after-ms'])        
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time + retry_after_ms > PTU_MAX_WAIT:
                logging.info(f"Latency {elapsed_time + retry_after_ms} ms exceeds threshold. Switching to paygo.")
                return call_standard(client, input_messages)
            else:
                logging.info(f"retrying PTU after {retry_after_ms} ms")
                time.sleep(e.retry_after / 1000)

if __name__ == "__main__":
    input_messages= [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure AI services support this too?"}
    ]

    start_time = time.time()
    response = call_with_retries(input_messages)
    end_time = time.time()
    execution_time = round(end_time - start_time,3)
    logging.info(f"Total latency was {execution_time} seconds.")
    logging.info(response.choices[0].message.content)