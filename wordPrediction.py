import numpy as np
import random
import string
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.sparse import lil_matrix

# Function to generate word vectors based on a co-occurrence matrix from a large text file
def gen_cooccurrence_matrix_from_file(file_path, window_size=5, chunk_size=1024 * 1024, max_vocab_size=100000):  # 1 MB chunks
    unique_words = set()
    
    # Read the file in chunks to determine unique words
    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            chunk = chunk.translate(str.maketrans('', '', string.punctuation)).lower()
            words = chunk.split()
            unique_words.update(words)

    # Limit vocabulary size
    unique_words = list(unique_words)[:max_vocab_size]
    word_to_idx = {word: idx for idx, word in enumerate(unique_words)}
    idx_to_word = {idx: word for word, idx in word_to_idx.items()}
    vocab_size = len(unique_words)

    # Initialize sparse co-occurrence matrix
    cooccurrence_matrix = lil_matrix((vocab_size, vocab_size), dtype=np.float32)

    # Read the file again to populate the co-occurrence matrix
    with open(file_path, 'r', encoding='utf-8') as f:
        total_chunks = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        f.seek(0)  # Reset file pointer
        pbar = tqdm(total=total_chunks, desc='Training Progress', unit='chunk')

        start_time = time.time()  # Start timer

        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            chunk = chunk.translate(str.maketrans('', '', string.punctuation)).lower()
            words = chunk.split()
            
            for idx, word in enumerate(words):
                if word not in word_to_idx:
                    continue
                
                word_idx = word_to_idx[word]
                start = max(0, idx - window_size)
                end = min(len(words), idx + window_size + 1)
                context_words = words[start:idx] + words[idx + 1:end]
                
                for context_word in context_words:
                    if context_word in word_to_idx:
                        context_idx = word_to_idx[context_word]
                        cooccurrence_matrix[word_idx, context_idx] += 1
            
            pbar.update(1)  # Update progress bar

        pbar.close()  # Close progress bar
        elapsed_time = time.time() - start_time  # Calculate elapsed time

        print(f"Training completed in {elapsed_time:.2f} seconds.")
    
    return cooccurrence_matrix.tocsr(), word_to_idx, idx_to_word  # Convert to CSR format

# Function to calculate cosine similarity between two vectors
def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# Function to perform self-attention (simplified version)
def self_attention(query, key, value):
    """Simple self-attention mechanism."""
    scores = np.dot(query, key.T)
    attention_weights = np.exp(scores) / np.sum(np.exp(scores), axis=1, keepdims=True)
    output = np.dot(attention_weights, value)
    return output

# Function to predict the next word based on the context
def predict_next_word(cooccurrence_matrix, word_to_idx, idx_to_word, context_word):
    """Predict the next word given a context word."""
    if context_word not in word_to_idx:
        return None

    word_idx = word_to_idx[context_word]
    cooccurrences = cooccurrence_matrix[word_idx].toarray().flatten()
    
    # Find the word with the highest co-occurrence count
    next_word_idx = np.argmax(cooccurrences)
    next_word = idx_to_word[next_word_idx]
    return next_word

# Function to generate a sentence given a starting word
def generate_sentence(cooccurrence_matrix, word_to_idx, idx_to_word, starting_word, max_length=10):
    """Generate a sentence starting from a given word."""
    current_word = starting_word
    sentence = [current_word]

    for _ in range(max_length - 1):
        next_word = predict_next_word(cooccurrence_matrix, word_to_idx, idx_to_word, current_word)
        if next_word is None:
            break
        sentence.append(next_word)
        current_word = next_word

    return ' '.join(sentence)

# Main function
def main(file_path):
    cooccurrence_matrix, word_to_idx, idx_to_word = gen_cooccurrence_matrix_from_file(file_path)
    
    # Example usage of the co-occurrence matrix and other functions
    print("Co-occurrence matrix shape:", cooccurrence_matrix.shape)
    print("Vocabulary size:", len(word_to_idx))
    
    # Allow user input for generating a sentence
    starting_word = 'you'
    
    if starting_word not in word_to_idx:
        print(f"'{starting_word}' not found in vocabulary. Using a random word instead.")
        starting_word = random.choice(list(word_to_idx.keys()))
    
    print("Starting word:", starting_word)
    generated_sentence = generate_sentence(cooccurrence_matrix, word_to_idx, idx_to_word, starting_word)
    print("Generated sentence:", generated_sentence)

# Call the main function with a sample file
if __name__ == "__main__":
    training_data_file = 'database.txt'  # Replace this with your actual text file
    main(training_data_file)

