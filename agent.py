import os
import openai
import requests
import time
import json
import ui
from sound import Recorder, Player
import speech

openai.api_key = ""


def transcribe(filename):
    with open(filename, "rb") as f:
        res = openai.Audio.transcribe("whisper-1", f)
        return res["text"]


def get_weather(region):
    res = requests.get("http://weather.tsukumijima.net/api/forecast/city/130010").json()
    return res["forecasts"][0]["detail"]["weather"]

def add(a, b):
    return a + b


functions = [
    {
        "name": "get_weather",
        "description": "Get the weather information for a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "都市名。大阪、東京、福岡など"}
            },
        },
        "required": ["region"],
    },
    {
        "name": "add",
        "description": "Take the sum of two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "The integer value from add"},
                "b": {"type": "integer", "description": "The integer value to add"},
            },
        },
        "required": ["a", "b"],
    },
]


def function_mapping(text):
    messages = [
        {
            "role": "user",
            "content": text,
        }
    ]
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response_message = res["choices"][0]["message"]
    if response_message.get("function_call"):
        func_map = {
            "get_weather": get_weather,
            "add": add,
        }
        func = func_map.get(response_message["function_call"]["name"], None)

        if func is None:
            return "存在しない関数です"
        
        args = json.loads(response_message["function_call"]["arguments"])
        result = str(func(**args))
        return result
    else:
        return "すみません。お役に立てません"


def speech_result(filename):
    input_text = transcribe(filename)
    answer_text = function_mapping(input_text)
    speech.say(answer_text)

global recorder
recorder = None

def on_push_recorder(sender):
    button = sender.superview["button1"]
    filename = 'audio.wav'

    global recorder
    if not recorder:
        # 開始処理
        recorder = Recorder(filename)
        recorder.record()

        button.title = "止める"
    else:
        # 終了処理
        recorder.stop()
        recorder = None

        speech_result(filename)

        button.title = "開始"


v = ui.load_view()
v.present()
