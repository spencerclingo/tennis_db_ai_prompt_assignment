import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import ast
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cluster_paragraph_embeddings(csv_file, k=3):
    """
    Generate k cluster embeddings per talk from paragraph embeddings by clustering paragraphs
    within each talk and using cluster centroids as the new embeddings.
    
    Parameters:
    - csv_file: Path to CSV file containing paragraph embeddings
    - k: Number of clusters (default=3)
    
    Returns:
    - DataFrame containing cluster embeddings and metadata
    """
    try:
        # Load the paragraph embeddings CSV
        df = pd.read_csv(csv_file)
        logging.info(f"Loaded CSV with {len(df)} paragraphs")

        # Validate required columns
        required_columns = ['url', 'ada_embedding', 'title', 'speaker', 'calling', 'year', 'season']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")

        # Convert string embeddings to numpy arrays
        df['ada_embedding'] = df['ada_embedding'].apply(lambda x: np.array(ast.literal_eval(x)))
        
        # Group paragraphs by talk (using url as unique identifier for talks)
        grouped = df.groupby('url')
        cluster_data = []
        
        for talk_url, group in grouped:
            # Extract metadata for the talk
            talk_info = group.iloc[0][['title', 'speaker', 'calling', 'year', 'season', 'url']].to_dict()
            
            # Get all embeddings for the talk
            embeddings = np.stack(group['ada_embedding'].values)
            
            # Check if there are enough paragraphs for clustering
            if len(embeddings) < k:
                logging.warning(f"Talk {talk_info['title']} ({talk_url}) has {len(embeddings)} "
                              f"paragraphs, fewer than k={k}. Skipping clustering.")
                continue
            
            # Perform k-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(embeddings)
            
            # Get cluster centroids (these are the new embeddings)
            centroids = kmeans.cluster_centers_
            
            # Store each centroid as a new embedding for the talk
            for cluster_idx in range(k):
                cluster_data.append({
                    'title': talk_info['title'],
                    'speaker': talk_info['speaker'],
                    'calling': talk_info['calling'],
                    'year': talk_info['year'],
                    'season': talk_info['season'],
                    'url': talk_info['url'],
                    'cluster_id': cluster_idx + 1,
                    'cluster_embedding': centroids[cluster_idx].tolist()
                })
            
            logging.info(f"Generated {k} cluster embeddings for talk: {talk_info['title']} ({talk_url})")
        
        # Create DataFrame for cluster embeddings
        if not cluster_data:
            raise ValueError("No cluster embeddings generated. Check input data or clustering process.")
        
        cluster_df = pd.DataFrame(cluster_data)
        
        # Save to CSV
        output_file = k + '_cluster_embeddings.csv'
        cluster_df.to_csv(output_file, index=False)
        logging.info(f"Cluster embeddings saved to {output_file}")
        
        return cluster_df
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

# Execute the clustering
if __name__ == "__main__":
    cluster_paragraph_embeddings("paragraphs_with_embeddings.csv", k=3)