# evals

Examples of how to use Braintrust Proxy with Microsoft Semantic Kernel framework.

## Prerequisites

This sample **requires** prerequisites in order to run.

### Install Python 3.12

### Configure Environment

Create and initialize the environment file by running:

```bash
echo "BRAINTRUST_API_KEY=sk-your-token" > ./evals/.env
```

### Run the sample

- Run ./start.sh


## Known issues
Not able to initialize the kernel with wrapped AsyncAzureOpenAI
```
Starting evals

Traceback (most recent call last):
  File "/Users/igor.mameshin/amn/evals/evals/eval_test.py", line 102, in <module>
    asyncio.run(main())
  File "/Users/igor.mameshin/.pyenv/versions/3.12.7/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/Users/igor.mameshin/.pyenv/versions/3.12.7/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/igor.mameshin/.pyenv/versions/3.12.7/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/igor.mameshin/amn/evals/evals/eval_test.py", line 47, in main
    chat_completion = AzureChatCompletion(
                      ^^^^^^^^^^^^^^^^^^^^
  File "/Users/igor.mameshin/amn/evals/.venv/lib/python3.12/site-packages/semantic_kernel/connectors/ai/open_ai/services/azure_chat_completion.py", line 97, in __init__
    super().__init__(
  File "/Users/igor.mameshin/amn/evals/.venv/lib/python3.12/site-packages/pydantic/validate_call_decorator.py", line 60, in wrapper_function
    return validate_call_wrapper(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/igor.mameshin/amn/evals/.venv/lib/python3.12/site-packages/pydantic/_internal/_validate_call.py", line 96, in __call__
    res = self.__pydantic_validator__.validate_python(pydantic_core.ArgsKwargs(args, kwargs))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for __init__
client
  Input should be an instance of AsyncAzureOpenAI [type=is_instance_of, input_value=<braintrust.oai.OpenAIV1W...r object at 0x10a08c740>, input_type=OpenAIV1Wrapper]
    For further information visit https://errors.pydantic.dev/2.8/v/is_instance_of
Failed to start evals
```
