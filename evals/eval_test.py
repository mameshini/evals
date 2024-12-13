# Based on https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide?pivots=programming-language-python
# pip install semantic-kernel
# https://github.com/microsoft/semantic-kernel/blob/main/python/samples/getting_started/05-using-the-planner.ipynb

import asyncio
import os
import time
import logging

from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.core_plugins.time_plugin import TimePlugin
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI

from dotenv import load_dotenv
import braintrust
from braintrust import EvalAsync
from braintrust import init_logger, traced, start_span
from autoevals import Factuality

@traced
async def main():

    logger = logging.getLogger("kernel")
    load_dotenv()

    BRAINTRUST_API_KEY = os.environ.get("BRAINTRUST_API_KEY")
    logger.info(f"Braintrust key: {BRAINTRUST_API_KEY}")  
    braintrust.login(org_name="AMN")  # This is optional, but makes it easier to grab the api url (and other variables) later on
    braintrust.init_logger(project="Dev")

    client = AsyncOpenAI(
        base_url="https://api.braintrust.dev/v1/proxy",
        api_key=os.environ["BRAINTRUST_API_KEY"],  # Can use Braintrust, Anthropic, etc. API keys here
    )

    start = time.time()
    response = await client.chat.completions.create(
        model="gpt-4o",  # Can use claude-2, llama-2-13b-chat, etc. here
        messages=[{"role": "user", "content": "What is a proxy?"}],
        seed=1,  # A seed activates the proxy's cache
    )
    print(response.choices[0].message.content)
    print(f"Took {time.time()-start}s")
    with start_span() as span:
        result = response.choices[0].message.content
        span.log(input="What is a proxy?", output=result)

    service = OpenAIChatCompletion(async_client=client, service_id="chat_completion", ai_model_id="gpt-4o")
    
    kernel = Kernel()
    kernel.add_service(service)

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
    with start_span() as span:
        result = response.string()
        span.log(input="prompt", output=result)

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

