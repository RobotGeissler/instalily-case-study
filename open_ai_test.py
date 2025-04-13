import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="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",
)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)