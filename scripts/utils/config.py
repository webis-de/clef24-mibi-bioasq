import os

from dotenv import load_dotenv
import instructor
from openai import OpenAI
import tomllib as toml

try:
    assert load_dotenv()
except AssertionError:
    print("Not using .env file and assuming env variables are already set.")

openai_key = os.environ.get("OPENAI_API_KEY")
client = instructor.patch(OpenAI(api_key=openai_key))


def load_toml_params(param_file):
    with open(param_file, "rb") as f:
        config = toml.load(f)
    return config