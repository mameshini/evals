# evals

Examples of how to use Braintrust Proxy with Microsoft Semantic Kernel framework.
The code demonstrates how to use Braintrust as an API proxy with Semantic Kernel.

Using Braintrust as the AI proxy allows the following benefits:
- Manage LLM endpoints and keys on Braintrust side
- Simplify code by accessing many AI providers through a single API.
- Reduce costs by automatically caching results when possible. 
- Increase observability by logging all LLM requests to Braintrust.

## Prerequisites

This sample **requires** prerequisites in order to run.

### Install Python 3.12

### Configure Environment

Create and initialize the environment file by running:

```bash
echo "BRAINTRUST_API_KEY=sk-your-token" > ./evals/.env
```

Add the following environment variables to the .env file:
```bash
BRAINTRUST_API_KEY=sk-your-token
AZURE_OPENAI_ENDPOINT=https://x.openai.azure.com
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://x.openai.azure.com/
AZURE_OPENAI_API_KEY=x
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
```

### Run the sample

- Run ./start.sh


## Known issues
- Not able to initialize the kernel with wrapped AsyncAzureOpenAI

