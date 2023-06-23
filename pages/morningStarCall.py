import openai
import json
import os
from dotenv import load_dotenv
from pyairtable import Table
import requests
import streamlit as st
import random
from auth import check_password

if check_password():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    rapid_api_key = os.getenv("X-RapidAPI-Key")

    airtable_api_key = os.getenv("AIRTABLE_API_KEY")
    table = Table(airtable_api_key, "app9MZWpzdds8HZnW", "tblLrEv4NUzoeUrc5")

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
                },
                "required": ["title"],
            },
        },
    ]

    def get_movie_by_title(title, country="us"):
        url = "https://streaming-availability.p.rapidapi.com/v2/search/title"

        querystring = {"title": title, "country": country}

        headers = {
            "X-RapidAPI-Key": "3e7a3f317cmsh87c96d2f7287a55p123a6cjsn50cacf322200",
            "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers, params=querystring)

        return response.json()["result"][0]["overview"]

    def get_current_weather(location, unit="fahrenheit"):
        url = "https://yahoo-weather5.p.rapidapi.com/weather"

        querystring = {"location": location, "unit": unit}

        headers = {
            "X-RapidAPI-Key": "3e7a3f317cmsh87c96d2f7287a55p123a6cjsn50cacf322200",
            "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers, params=querystring)
        return response.json()

    def get_free_games():
        url = "https://free-epic-games.p.rapidapi.com/free"

        headers = {
            "X-RapidAPI-Key": "3e7a3f317cmsh87c96d2f7287a55p123a6cjsn50cacf322200",
            "X-RapidAPI-Host": "free-epic-games.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers)

        print("GAMES", response.json())
        return response.json()

    def add_stock_news_airtable(stock, move, news_summary):
        table.create({"stock": stock, "move%": move, "news_summary": news_summary})

    def get_stock_news(markets):
        url = "https://bb-finance.p.rapidapi.com/news/list"

        querystring = {"id": markets}

        headers = {
            "X-RapidAPI-Key": rapid_api_key,
            "X-RapidAPI-Host": "bb-finance.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers, params=querystring)
        print(" json response:", response.json()["modules"][0])

        short_news_list = response.json()["modules"][:1]

        return short_news_list

    def get_stock_movers():
        url = "https://bb-finance.p.rapidapi.com/market/get-movers"

        querystring = {"id": "nky:ind", "template": "INDEX"}

        headers = {
            "X-RapidAPI-Key": rapid_api_key,
            "X-RapidAPI-Host": "bb-finance.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers, params=querystring)

        print(" !!!!!json response:", response.json()["leaders"])
        return response.json()["leaders"]

    def function_call(ai_response):
        function_call = ai_response["choices"][0]["message"]["function_call"]
        function_name = function_call["name"]
        arguments = function_call["arguments"]
        if function_name == "get_stock_movers":
            return get_stock_movers()
        elif function_name == "get_stock_news":
            performanceId = eval(arguments).get("performanceId")
            return get_stock_news(performanceId)
        elif function_name == "add_stock_news_airtable":
            stock = eval(arguments).get("stock")
            news_summary = eval(arguments).get("news_summary")
            move = eval(arguments).get("move")
            return add_stock_news_airtable(stock, move, news_summary)
        elif function_name == "get_current_weather":
            location = eval(arguments).get("location")
            unit = eval(arguments).get("unit")
            return get_current_weather(location, unit)
        elif function_name == "get_free_games":
            return get_free_games()
        elif function_name == "get_movie_by_title":
            title = eval(arguments).get("title")
            return get_movie_by_title(title)
        else:
            return

    def ask_function_calling(query):
        messages = [{"role": "user", "content": query}]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=function_descriptions,
            function_call="auto",
        )

        print("^%&^*%&^AIRESPONSE: ", response)

        while response["choices"][0]["finish_reason"] == "function_call":
            function_response = function_call(response)
            messages.append(
                {
                    "role": "function",
                    "name": response["choices"][0]["message"]["function_call"]["name"],
                    "content": json.dumps(function_response),
                }
            )

            print("messages: ", messages)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
                functions=function_descriptions,
                function_call="auto",
            )

            print("response: ", response)
        else:
            print(response)

        return response["choices"][0]["message"]["content"]

    st.set_page_config("API Call Chatbot", "🤖", "wide")
    st.header("Api Call Chatbot 😎")
    st.write(
        "Current Functions: Get stock movers, Get stock news, List Current Free games on Epic Games, Get Current Weather, Movie Description"
    )

    st.write("Example Prompt: Get Stock News for AAPL")
    user_query = st.text_input("User Query", "Get Stock News for AAPL")
    if st.button("Submit"):
        st.write("Response:")
        st.write(ask_function_calling(user_query))
