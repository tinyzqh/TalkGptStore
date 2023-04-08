import os
import torch
import pandas as pd
import torch.nn.functional as F
from typing import Any, List, Tuple


def generate_knowledge_index(model: Any, knowledge_path: str) -> None:
    """Generates an index of knowledge embeddings from a file containing knowledge texts.

    Args:
        model (Any): A model used to generate sentence embeddings.
        knowledge_path (str): The path to the file containing knowledge texts.

    Raises:
        ValueError: If the knowledge file does not exist or is empty.

    Returns:
        None
    """

    # Check that the knowledge file exists and is not empty
    if not os.path.exists(knowledge_path) or os.stat(knowledge_path).st_size == 0:
        raise ValueError(f"{knowledge_path} does not exist or is empty!")

    # Load the knowledge file into memory
    with open(knowledge_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    # Construct the path for the knowledge embedding file
    knowledge_embedding_path = os.path.join(os.path.dirname(knowledge_path), "knowledge_embeddings.csv")

    # If the knowledge embedding file does not exist, generate knowledge embeddings and save to file
    if not os.path.exists(knowledge_embedding_path):
        print(f"Generating knowledge embeddings for {knowledge_embedding_path} ...")
        knowledge_embeddings = [[line, sentence_embedding(model, line)] for line in lines]
        df = pd.DataFrame(knowledge_embeddings, columns=["texts", "embeddings"])
        df.to_csv(knowledge_embedding_path, index=False, encoding="utf-8")


def retrieve_related_documents(query_embedding: List[float], knowledge_df: pd.DataFrame) -> List[Tuple[str, float]]:
    """Perform retrieve_related_documents to find the most similar texts in knowledge_df to the given query_embedding.

    Args:
        query_embedding (List[float]): The embedding of the query text.
        knowledge_df (pd.DataFrame): The dataframe containing texts and their embeddings.

    Returns:
        List[Tuple[str, float]]: A list of tuples containing the most similar texts and their similarity scores.
    """
    texts = knowledge_df["texts"]
    embeddings = knowledge_df["embeddings"].apply(lambda x: eval(x))
    query_tensor = torch.tensor(query_embedding)
    knowledge_tensor = torch.tensor(embeddings)

    similarities = F.cosine_similarity(query_tensor, knowledge_tensor).tolist()
    pairs = list(zip(texts, similarities))
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs


def sentence_embedding(model: Any, text: str) -> List[float]:
    """
    Generates a sentence embedding for the input text using the given model.

    Args:
        model: A pre-trained sentence embedding model.
        text: The input text to generate embedding for.

    Returns:
        A list of floats representing the sentence embedding generated by the model.

    Raises:
        TypeError: If the input model is not compatible.
    """
    if isinstance(model, torch.nn.Module):
        result = model.encode(text, show_progress_bar=False, convert_to_numpy=True).tolist()
        return result
    else:
        raise TypeError("Invalid type for model argument. Expected torch.nn.Module, but got " + str(type(model)))
