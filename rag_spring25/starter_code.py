# find_similar_talks_with_chatgpt.py
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import openai
from config import OPENAI_API_KEY
import tiktoken

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_chatgpt_response(search_term, talks, model="gpt-4o", max_context_tokens=3000):
    """
    Generate a ChatGPT response based on the search term and provided talks.
    Ensure that the response uses only the talk content, with no external sources.
    """
    try:
        # Return ChatGPT response based on the talks
        return ""
    
    except Exception as e:
        print(f"Error generating ChatGPT response: {e}")
        return "Unable to generate response due to an error."

def find_similar_talks(search_term, top_k=3):
    """
    Finds the top_k most similar conference talks to a given search term based on embeddings
    and generates a ChatGPT response based on those talks.
    """
    try:
        # Load the CSV
        df = pd.read_csv("cleaned_conference_talks.csv")

        # Initialize the sentence transformer model
        model = SentenceTransformer('all-mpnet-base-v2')

        """
        Pseudo code:
        Generate the search embedding from the search term using the model.
        For each row in the dataframe, you should extract the talk embedding and convert it
        from a string to a list (use eval()). Next, use the util.cos_sim() function
        to calculate the cosine similarity between the search embedding and the talk
        embedding. Save each similarity value for use the next step
        """

        top_talks = []
        # Find the top_k most similar talks and store them in a list.

        # Generate ChatGPT response
        chatgpt_response = generate_chatgpt_response(search_term, top_talks)

        return top_talks, chatgpt_response

    except FileNotFoundError:
        print("Error: 'cleaned_conference_talks.csv' not found.")
        return [], ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], ""

# Example usage
if __name__ == "__main__":
    search_term = "How can I deal with serious depression"
    similar_talks, chatgpt_response = find_similar_talks(search_term)

    if similar_talks:
        print(f"Top 3 most similar talks to '{search_term}':")
        for talk in similar_talks:
            print(
                f"- Title: {talk['title']}, "
                f"Speaker: {talk['speaker']}, "
                f"Year: {talk['year']}, "
                f"Similarity: {talk['similarity']:.4f}, "
                f"Text Snippet: {talk['text'][:200]}..."
            )
        print("\nChatGPT Response:")
        print(chatgpt_response)
    else:
        print("No similar talks found.")