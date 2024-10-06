# model_factory.py

from models.most_common_model import MostCommonModel
from models.ngram_model import NGramModel


def create_most_common_model():
    """
    Initializes and returns a MostCommonModel instance.

    Returns:
        MostCommonModel: An instance of MostCommonModel.
    """
    return MostCommonModel()


def create_ngram_model(n=3, k=0.5, base_tokens=None):
    """
    Initializes and returns an NGramModel instance.

    Args:
        n (int): The 'n' in N-Gram.
        k (float): Smoothing parameter.
        base_tokens (list): List of base tokens (e.g., accelerator names with prefixes).

    Returns:
        NGramModel: An instance of NGramModel.
    """
    return NGramModel(n=n, k=k, base_tokens=base_tokens)
