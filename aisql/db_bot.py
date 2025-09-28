import json

# from openai import OpenAI
from google import genai
import os
import sqlite3
from time import time

print("Running db_bot.py!")

fdir = os.path.dirname(__file__)


def getPath(fname):
    return os.path.join(fdir, fname)


# SQLITE
sqliteDbPath = getPath("aidb.sqlite")
setupSqlPath = getPath("setup.sql")
setupSqlDataPath = getPath("setupData.sql")

# Erase previous db
if os.path.exists(sqliteDbPath):
    os.remove(sqliteDbPath)

sqliteCon = sqlite3.connect(sqliteDbPath)  # create new db
sqliteCursor = sqliteCon.cursor()
with open(setupSqlPath) as setupSqlFile, open(setupSqlDataPath) as setupSqlDataFile:
    setupSqlScript = setupSqlFile.read()
    setupSQlDataScript = setupSqlDataFile.read()

sqliteCursor.executescript(setupSqlScript)  # setup tables and keys
sqliteCursor.executescript(setupSQlDataScript)  # setup tables and keys


def runSql(query):
    # print(f"\n\n\n\nin run sql\n{query}")
    result = sqliteCursor.execute(query).fetchall()
    # print(f"\n\n\n\n{result}\n\n\n\n")
    return result


# OPENAI
configPath = getPath("config.json")
print(configPath)
with open(configPath) as configFile:
    config = json.load(configFile)

geminiClient = genai.Client(api_key=config["openaiKey"])
geminiClient.models.list()  # check if the key is valid (update in config.json)


def getGeminiResponse(content):
    response = geminiClient.models.generate_content(
        model="gemini-2.5-flash",
        contents=content,
    )

    return response.text


# strategies
commonSqlOnlyRequest = " Give me a sqlite select statement that answers the question. Only respond with sqlite syntax. If there is an error do not explain it!"
strategies = {
    "zero_shot": setupSqlScript + setupSQlDataScript,
    "single_domain_double_shot": (
        setupSqlScript + setupSQlDataScript + commonSqlOnlyRequest
    ),
}

questions = [
    "Who was ranked in the top 25 on September 1st?",
    "What rounds in tournaments did the 4th ranked player on December 31st get to throughout the year?",
    "Which players played each other the most throughout the year?",
]


def sanitizeForJustSql(value):
    gptStartSqlMarker = "```sqlite"
    gptEndSqlMarker = "```"
    if gptStartSqlMarker in value:
        value = value.split(gptStartSqlMarker)[1]
    if gptEndSqlMarker in value:
        value = value.split(gptEndSqlMarker)[0]

    return value


for strategy in strategies:
    responses = {"strategy": strategy, "prompt_prefix": strategies[strategy]}
    questionResults = []
    print("########################################################################")
    print(f"Running strategy: {strategy}")
    for question in questions:
        print(
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        print("Question:")
        print(question)
        error = "None"
        try:
            getSqlFromQuestionEngineeredPrompt = (
                strategies[strategy] + " " + question + "\n" + commonSqlOnlyRequest
            )
            sqlSyntaxResponse = getGeminiResponse(getSqlFromQuestionEngineeredPrompt)
            sqlSyntaxResponse = sanitizeForJustSql(sqlSyntaxResponse)
            print("SQL Syntax Response:")
            print(sqlSyntaxResponse)
            queryRawResponse = str(runSql(sqlSyntaxResponse))
            print("Query Raw Response:")
            print(queryRawResponse)
            friendlyResultsPrompt = (
                'I asked a question "'
                + question
                + '" and the response was "'
                + queryRawResponse
                + '" Please, just give a concise response in a more friendly way? Please do not give any other suggests or chatter.'
            )
            # betterFriendlyResultsPrompt = "I asked a question: \"" + question +"\" and I queried this database " + setupSqlScript + " with this query " + sqlSyntaxResponse + ". The query returned the results data: \""+queryRawResponse+"\". Could you concisely answer my question using the results data?"
            friendlyResponse = getGeminiResponse(friendlyResultsPrompt)
            print("Friendly Response:")
            print(friendlyResponse)
        except Exception as err:
            error = str(err)
            print(err)

        questionResults.append(
            {
                "question": question,
                "sql": sqlSyntaxResponse,
                "queryRawResponse": queryRawResponse,
                "friendlyResponse": friendlyResponse,
                "error": error,
            }
        )

    responses["questionResults"] = questionResults

    with open(getPath(f"response_{strategy}_{time()}.json"), "w") as outFile:
        json.dump(responses, outFile, indent=2)


sqliteCursor.close()
sqliteCon.close()
print("Done!")
