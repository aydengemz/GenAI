import requests
import json
import os
from dotenv import find_dotenv, load_dotenv
from langchain import PromptTemplate, LLMChain, OpenAI
import streamlit as st
import openai

load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")
brawl_stars_api_key = os.getenv("BS_API_KEY")

# get Player info
def get_player_info(playerId):
    url = f"https://bsproxy.royaleapi.dev/v1/players/{playerId}"
    query_string = {"playerId": playerId}

    headers = {"BS-API_KEY": brawl_stars_api_key}

    response = requests.get(url, headers=headers, params=query_string)
    print(response)

    return url


print(get_player_info("2L2C2Q2"))
