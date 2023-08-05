import openai
import json
import os
import requests
import streamlit as st
from auth import check_password

function_descriptions = [
    {
        "name": "get_stock_movers",
        "description": "Get the stocks that has biggest price/volume moves, e.g. actives, gainers, losers, etc.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_stock_news",
        "description": "Get the latest news for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "performanceId": {
                    "type": "string",
                    "description": "id of the stock, which is referred as performanceID in the API",
                },
            },
            "required": ["performanceId"],
        },
    },
    {
        "name": "add_stock_news_airtable",
        "description": "Add the stock, news summary & price move to Airtable",
        "parameters": {
            "type": "object",
            "properties": {
                "stock": {"type": "string", "description": "stock ticker"},
                "move": {"type": "string", "description": "price move in %"},
                "news_summary": {
                    "type": "string",
                    "description": "news summary of the stock",
                },
            },
        },
    },
    {
        "name": "get_free_games",
        "description": "Lists the free epic games right now",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. Chapel Hill, NC",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_movie_by_title",
        "description": "Describes a movie of a certain title",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The name of the movie i.e 'The Matrix'",
                },
                "country": {
                    "type": "string",
                    "description": "The country the mobie was produced in i.e 'us'",
                },
            },
            "required": ["title"],
        },
    },
]


def get_movie_by_title(title, key, country="us"):
    url = "https://streaming-availability.p.rapidapi.com/v2/search/title"

    querystring = {"title": title, "country": country}

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()["result"][0]["overview"]


def get_current_weather(location, key, unit="fahrenheit"):
    url = "https://yahoo-weather5.p.rapidapi.com/weather"

    querystring = {"location": location, "unit": unit}

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


def get_free_games(key):
    url = "https://free-epic-games.p.rapidapi.com/free"

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "free-epic-games.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers)

    print("GAMES", response.json())
    return response.json()


def add_stock_news_airtable(stock, move, news_summary):
    return None


def get_stock_news(markets, key):
    url = "https://bb-finance.p.rapidapi.com/news/list"

    querystring = {"id": markets}

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "bb-finance.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(" json response:", response.json()["modules"][0])

    short_news_list = response.json()["modules"][:1]

    return short_news_list


def get_stock_movers(key):
    url = "https://bb-finance.p.rapidapi.com/market/get-movers"

    querystring = {"id": "nky:ind", "template": "INDEX"}

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "bb-finance.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(" !!!!!json response:", response.json()["leaders"])
    return response.json()["leaders"]


def function_call(ai_response, rkey):
    function_call = ai_response["choices"][0]["message"]["function_call"]
    function_name = function_call["name"]
    arguments = function_call["arguments"]
    if function_name == "get_stock_movers":
        return get_stock_movers(rkey)
    elif function_name == "get_stock_news":
        performanceId = eval(arguments).get("performanceId")
        return get_stock_news(performanceId, rkey)
    elif function_name == "add_stock_news_airtable":
        stock = eval(arguments).get("stock")
        news_summary = eval(arguments).get("news_summary")
        move = eval(arguments).get("move")
        return add_stock_news_airtable(stock, move, news_summary)
    elif function_name == "get_current_weather":
        location = eval(arguments).get("location")
        unit = eval(arguments).get("unit")
        return get_current_weather(location, rkey, unit)
    elif function_name == "get_free_games":
        return get_free_games(rkey)
    elif function_name == "get_movie_by_title":
        title = eval(arguments).get("title")
        country = eval(arguments).get("country")
        return get_movie_by_title(title, rkey, country)
    else:
        return


def ask_function_calling(query, rapidApiKey):
    messages = [{"role": "user", "content": query}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=function_descriptions,
        function_call="auto",
    )

    while response["choices"][0]["finish_reason"] == "function_call":
        function_response = function_call(response, rapidApiKey)
        messages.append(
            {
                "role": "function",
                "name": response["choices"][0]["message"]["function_call"]["name"],
                "content": json.dumps(function_response),
            }
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=function_descriptions,
            function_call="auto",
        )

    return response["choices"][0]["message"]["content"]


st.set_page_config("API Call Chatbot", "🤖", "wide")
st.header("Api Call Chatbot 😎")
st.image("diagrams/apicall.png", use_column_width=True)
st.subheader(
    "Current Functions: Get stock movers, Get stock news, List Current Free games on Epic Games, Get Current Weather, Movie Description"
)

st.subheader("Example Prompt: Get Stock News for AAPL")
openAIKey = st.text_input("Enter your OpenAI API Key")
RapidApiKey = st.text_input("Enter your RapidAPI Key")
user_query = st.text_input("User Query", "Get Stock News for AAPL")
if st.button("Submit"):
    openai.api_key = openAIKey
    st.write("Response:")
    st.write(ask_function_calling(user_query, RapidApiKey))
