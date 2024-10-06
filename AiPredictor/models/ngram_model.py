# ngram_model.py

# Import necessary libraries
import pandas as pd
import numpy as np
from collections import Counter
import nltk
from nltk.util import ngrams
from nltk.lm import Lidstone
from nltk.lm.preprocessing import padded_everygram_pipeline

from nltk.lm import MLE
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Ensure NLTK data is downloaded
nltk.download('punkt', quiet=True)



class NGramModel:
    def __init__(self, n=6, k=0.5, min_prob=1e-8, base_tokens=None, base_prob=1e-9):
        self.n = n
        self.k = k  # Smoothing parameter
        self.min_prob = min_prob  # Minimum probability
        self.base_tokens = base_tokens if base_tokens is not None else []  # Optional base tokens
        self.base_prob = base_prob  # Base probability for base tokens
        self.model = None
        self.vocab = set()

    def train(self, train_sequences):
        # Prepare the data
        tokens = [token for seq in train_sequences for token in seq]
        self.vocab.update(tokens)

        # Add base tokens to the vocabulary if provided
        self.vocab.update(self.base_tokens)

        # Train the n-gram model with add-k (Lidstone) smoothing
        train_data, padded_sents = padded_everygram_pipeline(self.n, train_sequences)
        self.model = Lidstone(self.k, self.vocab)
        self.model.fit(train_data, padded_sents)

        # Set the base probability for the base tokens
        for token in self.base_tokens:
            if token not in tokens:
                # If token is not in the training data, assign it a base probability
                self.model.counts.unigrams[token] = max(self.base_prob, self.min_prob)

    def score(self, word, context=None):
        # Retrieve the probability of a word given a context
        if context is None:
            context = ()
        prob = self.model.score(word, context)
        # Ensure the probability is at least min_prob

        return max(prob, self.min_prob)

    def predict_accelerator_probs(self, context_tokens):
        # Use the last n-1 tokens as context
        context = tuple(context_tokens[-(self.n - 1):])
        probs = {}

        # Make a copy of context_tokens so we can modify it
        remaining_context_tokens = context_tokens[:]

        for accelerator in self.vocab:
            if accelerator.startswith('Accelerator_'):
                prob = self.model.score(accelerator, context)

                # Extract the last word of the accelerator
                last_word_accelerator = accelerator.split()[-1]

                # Check if the last word of the accelerator is present in any of the remaining context tokens
                checked_jumpstart=False
                i=0
                for token in remaining_context_tokens:
                    if not checked_jumpstart and "Jumpstart" in accelerator and 'implemented' not in remaining_context_tokens:
                        prob += 1
                        checked_jumpstart = True
                    if last_word_accelerator in token:
                        prob+=10
                        # Adjust the probability based on specific conditions
                        if i+1 < len(remaining_context_tokens):
                            if "TuneUp" in accelerator and remaining_context_tokens[i+1] == 'implemented':
                                prob += 100
                            elif "TuneUp" in accelerator and remaining_context_tokens[i+1] != 'implemented':
                                prob=0
                                break
                            elif "TuneUp" not in accelerator and remaining_context_tokens[i+1] == 'implemented':
                                prob = 0
                                break

                        # Remove the matched token
                        remaining_context_tokens.pop(i)

                        # Remove the token right after the matched one, if it exists
                        if i < len(remaining_context_tokens):  # Ensure the next token exists
                            remaining_context_tokens.pop(i)

                        break  # Break the loop to avoid further checks
                    i+=1

                probs[accelerator] = prob

        # Sort by probability in descending order
        sorted_accelerators = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        return sorted_accelerators

    def recommend(self, context_tokens, top_n=5):
        sorted_accelerators = self.predict_accelerator_probs(context_tokens)
        recommendations = [acc.replace('Accelerator_', '') for acc, prob in sorted_accelerators[:top_n]]
        return recommendations

