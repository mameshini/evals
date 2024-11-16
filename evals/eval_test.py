# Based on https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide?pivots=programming-language-python
# pip install semantic-kernel
# https://github.com/microsoft/semantic-kernel/blob/main/python/samples/getting_started/05-using-the-planner.ipynb

import asyncio
import os

from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from openai import AsyncAzureOpenAI
import semantic_kernel as sk
from semantic_kernel.core_plugins.time_plugin import TimePlugin

from dotenv import load_dotenv
import braintrust
from braintrust import EvalAsync
from autoevals import Factuality

import logging

async def main():

    logger = logging.getLogger("kernel")
    load_dotenv()

    BRAINTRUST_API_KEY = os.environ.get("BRAINTRUST_API_KEY")
    logger.info(f"Braintrust key: {BRAINTRUST_API_KEY}")  
    braintrust.login()  # This is optional, but makes it easier to grab the api url (and other variables) later on

    braintrust_client = braintrust.wrap_openai(
        AsyncAzureOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_version='2024-02-15-preview'  # Use the appropriate API version
        )
    )

    # Initialize OpenAI chat completion API by providing a custom AsyncAzureOpenAI to Semantic Kernel
    # This is where the error is happening: Input should be an instance of AsyncAzureOpenAI [type=is_instance_of, input_value=<braintrust.oai.OpenAIV1Wrapper 
    # Comment out the line below to use the default OpenAI chat completion API
    chat_completion = AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        async_client=braintrust_client
    )

    # Initialize OpenAI chat completion API without Braintrust - working fine, but not using the proxy
    chat_completion = AzureChatCompletion(
        service_id="default",
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    # Initialize the kernel abd add chat_completion service to it
    kernel = Kernel()
    kernel.add_service(chat_completion)

    # Set the logging level for  semantic_kernel.kernel to DEBUG.
    setup_logging()
    logging.getLogger("kernel").setLevel(logging.DEBUG)

    # Add a plugin (time is a core plugin)
    kernel.add_plugin(TimePlugin(), "time")
    prompt  = """
    Today is: {{time.date}}
    Current time is: {{time.time}}
    Answer to the following questions using JSON syntax, including the data used.
    Is it morning, afternoon, evening, or night (morning/afternoon/evening/night)?
    Is it weekend time (weekend/not weekend)?
    """
    prompt_function = kernel.add_function(function_name="test01", plugin_name="sample", prompt=prompt)
    response = await kernel.invoke(prompt_function, request=prompt)
    print(response)

    # Also run a simple eval 
    if os.getenv("USE_BRAINTRUST_EVALS") == "true":    
        await EvalAsync(
            "Dev",
            data=lambda: [
                {
                    "input": "Foo",
                    "expected": "Hi Foo",
                },
                {
                    "input": "Bar",
                    "expected": "Hello Bar",
                },
            ],  
            task=lambda input: "Hi " + input,  
            scores=[Factuality],
        )


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())

