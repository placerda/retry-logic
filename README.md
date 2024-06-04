# Azure OpenAI Smart Retry

This Python script demonstrates how to interact with Azure OpenAI's API using a smart retry mechanism. It is designed to handle rate limit errors by switching between different deployments (PTU and Standard) based on a maximum wait time for the PTU retry. This approach ensures improved reliability, performance, and user experience.

## Benefits

### Handling Rate Limits Gracefully
- **Automated Retry Logic:** The script handles `RateLimitError` exceptions by automatically retrying after a specified delay, ensuring that temporary rate limit issues do not cause immediate failure.
- **Fallback Mechanism:** If the rate limit would cause a significant delay, the script switches to a standard deployment, maintaining the application's responsiveness and reliability.

### Improved User Experience
- **Latency Management:** By setting a maximum acceptable latency (`PTU_MAX_WAIT`), the script ensures that users do not experience excessive wait times. If the latency for the preferred deployment exceeds this threshold, the script switches to an alternative deployment to provide a quicker response.
- **Continuous Service Availability:** Users receive responses even when the primary service (PTU model) is under heavy load, as the script can fall back to a secondary service (standard model).

### Resilience and Robustness
- **Error Handling:** The approach includes robust error handling for `RateLimitError`, preventing the application from crashing or hanging when the rate limit is exceeded.
- **Logging:** Detailed logging provides insights into the application's behavior, including response times and when fallbacks occur. This information is valuable for debugging and optimizing performance.

### Optimized Resource Usage
- **Adaptive Resource Allocation:** By switching between PTU and standard models based on latency and rate limits, the script optimizes resource usage, balancing between cost (PTU might be more cost-effective) and performance (standard deployment as a fallback).

### Scalability
- **Dynamic Adaptation:** As the application's usage scales, the dynamic retry and fallback mechanism ensures that it can handle increased load without manual intervention. This is crucial for applications expecting varying traffic patterns.

## How it Works

This script interacts with the Azure OpenAI Chat Completion API, initially attempting to use the PTU model.

Here's the step-by-step process:

1.  The script sends a request to the PTU model.

2.  If the PTU model responds successfully, the process ends here. 
    However, if a rate limit error occurs, the script takes the following steps:

    - The script calculates the elapsed time since the first request and the 'retry-after-ms' time provided in the error response and adds these two times together.
    
    - This total is compared with a predefined 'maximum wait time'.
     
       - If the total time is greater than the 'maximum wait time', the script switches to the standard model to get a response.

       - If the total time is less than the 'maximum wait time', the script waits for the 'retry-after-ms' time and then tries again with the PTU model. (returns to step 1)

It's worth noting that falling back to the standard deployment doesn't necessarily guarantee a faster response. Instead, it simply provides an alternative way to get a response without waiting for the `retry-after-ms` to make a new request to the PTU.

Here is a video demonstrating the script in action. It shows how the script handles rate limit errors and switches between different deployments based on the maximum wait time for the PTU retry.

<a href="https://www.youtube.com/embed/iQnW0cy1-sY" target="_blank"><img src="https://img.youtube.com/vi/iQnW0cy1-sY/hqdefault.jpg" width="300" height="150" /></a>

## How to Run

1. Clone this repository to your local machine.
2. Install the required Python packages by running `pip install -r requirements.txt`.
3. Set the following environment variables:
    - `OPENAI_API_BASE`: The base URL of the OpenAI API.
    - `OPENAI_API_KEY`: Your OpenAI API key.
    - `PTU_DEPLOYMENT`: The deployment ID of your PTU model.
    - `STANDARD_DEPLOYMENT`: The deployment ID of your standard model.
4. Modify the `MAX_RETRIES` and `PTU_MAX_WAIT` constants in the script as needed.
5. Run the script with `python smart_retry.py`.

The `MAX_RETRIES` constant is used to leverage the automatic retry mechanism provided by the Python SDK. This constant defines the maximum number of times the script will attempt to resend a request to the Azure OpenAI Chat Completion API after encountering a rate limit error.

The `PTU_MAX_WAIT` constant is used to define the maximum time (in milliseconds) the script should wait before falling back to the standard deployment. If the sum of the elapsed time since the first request and the retry-after-ms time from the error response exceeds this threshold, the script will switch from the PTU model to the standard model to avoid further delay.

Please note that you need to have the necessary permissions to access the Azure OpenAI API and the specified deployments.
