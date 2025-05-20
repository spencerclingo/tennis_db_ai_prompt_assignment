import pandas as pd
from sentence_transformers import SentenceTransformer

def generate_embeddings(csv_file):
    """Generates and adds sentence embeddings to a CSV file of conference talks."""
    try:
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)

        # Initialize the sentence transformer model
        model = SentenceTransformer('all-mpnet-base-v2')

        # Generate embeddings for the 'talk' column
        df['embeddings'] = df['talk'].apply(lambda x: model.encode(x).tolist())
        
        df.to_csv("talks_with_embeddings.csv", index=False)
        print("Embeddings generated and saved to 'talks_with_embeddings.csv'")
    except Exception as e:
        print(f"An error occurred: {e}")

generate_embeddings("talks.csv")