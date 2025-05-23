from openai import OpenAI
import pandas as pd
from config import OPENAI_API_KEY

OpenAI.api_key = OPENAI_API_KEY

client = OpenAI(api_key=OpenAI.api_key)

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

df = pd.read_csv("talks.csv")

df['ada_embedding'] = df['talk'].apply(lambda x: get_embedding(x, model='text-embedding-3-small'))
df.to_csv('talks_with_embeddings.csv', index=False)

df = pd.read_csv("paragraphs.csv")

df['ada_embedding'] = df['paragraph'].apply(lambda x: get_embedding(x, model='text-embedding-3-small'))
df.to_csv('paragraphs_with_embeddings.csv', index=False)