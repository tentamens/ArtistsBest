import requests
import Levenshtein

def find_closest_word(input_str, word_list):
    closest_word = None
    min_distance = float("inf")
    word_list = [item["name"] for item in word_list]
    for word in word_list:
        distance = Levenshtein.distance(input_str.lower(), word.lower())
        if distance < min_distance:
            closest_word = word
            min_distance = distance
    return closest_word

def findClosestWord(inputStr, wordList):
    closest_word = None
    min_distance = float("inf")
    for word in wordList:
        distance = Levenshtein.distance(inputStr.lower(), word.lower())
        if distance < min_distance:
            closest_word = word
            min_distance = distance
    return closest_word


def make_request(url, headers, data, whereCalledFrom):
    response = None
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err} \n called from {whereCalledFrom}")
        
        return ["error", response.json()]


def makeGetRequest(url, headers, data, whereCalledFrom):
    response = None
    try:
        response = requests.get(url, headers=headers, params=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err} \n called from {whereCalledFrom}")
        
        return ["error", response.json()]