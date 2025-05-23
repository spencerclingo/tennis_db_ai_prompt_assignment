import pandas as pd
from sentence_transformers import SentenceTransformer

def generate_embeddings(csv_file, column_name):
    """Generates and adds sentence embeddings to a CSV file."""
    try:
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)

        # Initialize the sentence transformer model
        model = SentenceTransformer('all-mpnet-base-v2')

        # Generate embeddings for the 'talk' column
        df['embeddings'] = df[column_name].apply(lambda x: model.encode(x).tolist())

        df.to_csv(column_name + "s_and_embeddings.csv", index=False)
        print("Embeddings generated and saved to '" + column_name + "s_with_embeddings.csv'")
    except Exception as e:
        print(f"An error occurred: {e}")

generate_embeddings("talks.csv", "talk")
generate_embeddings("paragraphs.csv", "paragraph")