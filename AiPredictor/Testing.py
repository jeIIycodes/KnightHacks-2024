# tests.py

import random
import itertools
import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import KFold
import concurrent.futures
from model_factory import create_most_common_model, create_ngram_model
from utils.data_loader import load_data
from models.most_common_model import MostCommonModel
from models.ngram_model import NGramModel

# Suppress warnings
warnings.filterwarnings('ignore')

def generate_permutations_poisson(industry_token, paired_list, num_permutations=None, lambda_poisson=1.0):
    """
    Generate permutations of product tokens and their associated accelerators, keeping the order within pairs.

    Args:
        industry_token (str): The industry token.
        paired_list (list): List of tuples, each containing product tokens list and accelerator.
        num_permutations (int): Number of permutations to generate.
        lambda_poisson (float): Lambda parameter for Poisson distribution.

    Returns:
        permutations (list): List of permuted sequences.
    """
    total_pairs = len(paired_list)
    permutations = []

    if num_permutations is None:
        pair_permutations = list(itertools.permutations(paired_list))
        for pair_perm in pair_permutations:
            new_sequence = [industry_token]
            for product_tokens, accelerator in pair_perm:
                new_sequence.extend(product_tokens)
                new_sequence.append('Accelerator_' + accelerator)
            permutations.append(new_sequence)
    else:
        for _ in range(num_permutations):
            num_pairs_included = np.random.poisson(lambda_poisson)
            num_pairs_included = max(1, min(num_pairs_included, total_pairs))

            selected_pairs = random.sample(paired_list, num_pairs_included)
            random.shuffle(selected_pairs)
            new_sequence = [industry_token]
            new_sequence_back = []
            for product_tokens, accelerator in selected_pairs:
                new_sequence.extend(product_tokens)
                new_sequence_back.append('Accelerator_' + accelerator)
            new_sequence.extend(new_sequence_back)
            permutations.append(new_sequence)

    return permutations

def calculate_metrics(actual_accelerators, recommended_accelerators):
    """
    Calculate precision, recall, F1 score, and accuracy for the recommendations.

    Args:
        actual_accelerators (list): List of actual accelerators.
        recommended_accelerators (list): List of recommended accelerators.

    Returns:
        tuple: (precision, recall, f1, accuracy)
    """
    num_correct = len(set(recommended_accelerators) & set(actual_accelerators))  # Intersection of actual and recommended

    precision = num_correct / len(recommended_accelerators) if recommended_accelerators else 0
    recall = num_correct / len(actual_accelerators) if actual_accelerators else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Accuracy: number of correct recommendations over the number of recommended accelerators
    accuracy = num_correct / len(recommended_accelerators) if recommended_accelerators else 0

    return precision, recall, f1, accuracy

def process_fold(fold, train_index, test_index, all_companies, companies_df, company_products, company_accelerators, n, k, num_permutations):
    """
    Process a single fold: train models and evaluate them.

    Args:
        fold (int): Fold number.
        train_index (array): Training indices.
        test_index (array): Testing indices.
        all_companies (list): List of all company names.
        companies_df (DataFrame): DataFrame of companies.
        company_products (dict): Mapping from companies to products and implementation status.
        company_accelerators (dict): Mapping from companies to accelerators.
        n (int): N for N-Gram model.
        k (float): Smoothing parameter for N-Gram model.
        num_permutations (int): Number of permutations to generate.

    Returns:
        dict: Metrics for both models.
    """
    print(f"Processing Fold {fold}...")

    # Get train and test company names
    train_companies = [all_companies[i] for i in train_index]
    test_companies = [all_companies[i] for i in test_index]

    # Generate training sequences with permutations
    train_sequences = []
    for company in train_companies:
        # Get industry
        industry = companies_df.loc[companies_df['Name'] == company, 'Industry'].values[0]
        industry_token = 'Industry_' + industry

        # Get products tokens and accelerators
        products_impl_list = company_products.get(company, [])  # List of lists of tokens
        accelerators = company_accelerators.get(company, [])  # List of accelerators with 'Accelerator_' prefix

        # Ensure the number of products matches the number of accelerators
        if len(products_impl_list) != len(accelerators):
            print(f"Skipping company '{company}' due to mismatched products and accelerators.")
            continue

        # Build paired_list
        paired_list = list(zip(products_impl_list, [acc.replace('Accelerator_', '') for acc in accelerators]))

        # Generate permutations
        permutations = generate_permutations_poisson(industry_token, paired_list, num_permutations=num_permutations, lambda_poisson=1.0)

        train_sequences.extend(permutations)

    # Generate test sequences without permutations (use original sequences)
    test_sequences = []
    for company in test_companies:
        # Get industry
        industry = companies_df.loc[companies_df['Name'] == company, 'Industry'].values[0]
        industry_token = 'Industry_' + industry

        # Get products tokens and accelerators
        products_impl_list = company_products.get(company, [])
        accelerators = company_accelerators.get(company, [])

        # Ensure the number of products matches the number of accelerators
        if len(products_impl_list) != len(accelerators):
            print(f"Skipping company '{company}' due to mismatched products and accelerators.")
            continue

        # Build sequence
        sequence = [industry_token]
        for product_tokens, accelerator in zip(products_impl_list, accelerators):
            sequence.extend(product_tokens)
            sequence.append(accelerator)
        test_sequences.append(sequence)

    # Train the Most Common Accelerator Model
    most_common_model = create_most_common_model()
    train_accelerators = []
    for seq in train_sequences:
        train_accelerators.extend([token.replace('Accelerator_', '') for token in seq if token.startswith('Accelerator_')])

    most_common_model.train(train_accelerators)

    # Evaluate the Most Common Model
    precisions_mc = []
    recalls_mc = []
    f1s_mc = []
    accuracies_mc = []
    for seq in test_sequences:
        actual_accelerators = [token.replace('Accelerator_', '') for token in seq if token.startswith('Accelerator_')]
        recommendations = most_common_model.recommend(top_n=5)
        precision, recall, f1, accuracy = calculate_metrics(actual_accelerators, recommendations)
        precisions_mc.append(precision)
        recalls_mc.append(recall)
        f1s_mc.append(f1)
        accuracies_mc.append(accuracy)

    metrics_mc = {
        'Precision': np.mean(precisions_mc),
        'Recall': np.mean(recalls_mc),
        'F1 Score': np.mean(f1s_mc),
        'Accuracy': np.mean(accuracies_mc)
    }

    # Train the N-Gram Model
    # Prepare base_tokens
    base_tokens = []
    for company in train_companies:
        industry = companies_df.loc[companies_df['Name'] == company, 'Industry'].values[0]
        industry_token = 'Industry_' + industry
        products_impl_list = company_products.get(company, [])
        accelerators = company_accelerators.get(company, [])
        if len(products_impl_list) != len(accelerators):
            continue
        paired_list = list(zip(products_impl_list, [acc.replace('Accelerator_', '') for acc in accelerators]))
        permutations = generate_permutations_poisson(industry_token, paired_list, num_permutations=num_permutations, lambda_poisson=1.0)
        base_tokens.extend([acc for seq in permutations for acc in seq if acc.startswith('Accelerator_')])

    # Train N-Gram model
    ngram_model = create_ngram_model(n=n, k=k, base_tokens=base_tokens)
    ngram_model.train(train_sequences)

    # Evaluate the N-Gram Model
    precisions_ng = []
    recalls_ng = []
    f1s_ng = []
    accuracies_ng = []
    for seq in test_sequences:
        # Separate context tokens and actual accelerators
        context_tokens = []
        actual_accelerators = []
        i = 0
        while i < len(seq):
            token = seq[i]
            if token.startswith('Industry_'):
                context_tokens.append(token)
                i += 1
            elif token.startswith('Product_'):
                # Product tokens: Product, implementation status, category
                context_tokens.extend(seq[i:i+3])
                i += 3
            elif token.startswith('Accelerator_'):
                actual_accelerators.append(token.replace('Accelerator_', ''))
                i += 1
            else:
                i += 1  # Skip unexpected tokens

        recommendations = ngram_model.recommend(context_tokens, top_n=5)
        precision, recall, f1, accuracy = calculate_metrics(actual_accelerators, recommendations)
        precisions_ng.append(precision)
        recalls_ng.append(recall)
        f1s_ng.append(f1)
        accuracies_ng.append(accuracy)

    metrics_ngram_fold = {
        'Precision': np.mean(precisions_ng),
        'Recall': np.mean(recalls_ng),
        'F1 Score': np.mean(f1s_ng),
        'Accuracy': np.mean(accuracies_ng)
    }

    print(f"Fold {fold} Metrics:")
    print("Most Common Model:", metrics_mc)
    print("N-Gram Model:", metrics_ngram_fold)
    print("-" * 50)

    return {
        'Fold': fold,
        'MostCommonMetrics': metrics_mc,
        'NGramMetrics': metrics_ngram_fold
    }

def compute_mean_metrics(metrics_list):
    """
    Compute the mean of each metric across all folds.

    Args:
        metrics_list (list): List of metric dictionaries.

    Returns:
        dict: Mean metrics.
    """
    mean_metrics = {}
    for metric in metrics_list[0].keys():
        mean_metrics[metric] = np.mean([m[metric] for m in metrics_list])
    return mean_metrics

def run_parallel_folds(kf, company_indices, all_companies, companies_df, company_products, company_accelerators, n, k, num_permutations):
    """
    Run cross-validation folds in parallel.

    Args:
        kf (KFold): K-Fold cross-validator.
        company_indices (array): Array of company indices.
        all_companies (list): List of all company names.
        companies_df (DataFrame): DataFrame of companies.
        company_products (dict): Mapping from companies to products and implementation status.
        company_accelerators (dict): Mapping from companies to accelerators.
        n (int): N for N-Gram model.
        k (float): Smoothing parameter for N-Gram model.
        num_permutations (int): Number of permutations to generate.

    Returns:
        tuple: Metrics for Most Common and N-Gram models.
    """
    metrics_most_common = []
    metrics_ngram = []

    # Use ProcessPoolExecutor to parallelize the fold processing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for fold, (train_index, test_index) in enumerate(kf.split(company_indices), 1):
            futures.append(executor.submit(
                process_fold,
                fold, train_index, test_index, all_companies, companies_df, company_products, company_accelerators, n, k, num_permutations
            ))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            metrics_most_common.append(result['MostCommonMetrics'])
            metrics_ngram.append(result['NGramMetrics'])

    return metrics_most_common, metrics_ngram

def run_tests(n=3, k=0.5, num_permutations=10):
    """
    Run cross-validation tests on both models.

    Args:
        n (int): N for N-Gram model.
        k (float): Smoothing parameter for N-Gram model.
        num_permutations (int): Number of permutations to generate.

    Prints:
        Aggregated metrics for both models.
    """
    companies_df, company_products, company_accelerators, accelerators_df = load_data()
    accelerator_names_with_prefix = ["Accelerator_" + name for name in accelerators_df['Name'].tolist()]


    # Prepare the list of all company names
    all_companies = companies_df['Name'].tolist()
    company_indices = np.arange(len(all_companies))

    # Initialize K-Fold cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    metrics_most_common, metrics_ngram = run_parallel_folds(
        kf, company_indices, all_companies, companies_df, company_products, company_accelerators, n, k, num_permutations
    )

    mean_metrics_most_common = compute_mean_metrics(metrics_most_common)
    mean_metrics_ngram = compute_mean_metrics(metrics_ngram)

    print("\nAggregated Most Common Accelerator Model Metrics:")
    print(mean_metrics_most_common)

    print("\nAggregated N-Gram Model Metrics:")
    print(mean_metrics_ngram)

def train_and_use_ngram_model(n=3, k=0.5, num_permutations=10, sample_context=None):
    """
    Trains the N-Gram model using the entire dataset and makes recommendations on a sample context.

    Args:
        n (int): N for the N-Gram model.
        k (float): Smoothing parameter for the N-Gram model.
        num_permutations (int): Number of permutations to generate for training sequences.
        sample_context (list): Sample context to get recommendations for.

    Returns:
        recommendations (list): List of recommended accelerators.
    """
    if sample_context is None:
        sample_context = ['Industry_Sports Equipment',
                          'Product_Tibco Spotfire',
                          'not_implemented',
                          'Category_Business Intelligence and Analytics']

    companies_df, company_products, company_accelerators, accelerators_df = load_data()
    accelerator_names_with_prefix = ["Accelerator_" + name for name in accelerators_df['Name'].tolist()]
    all_companies = companies_df['Name'].tolist()

    # Generate training sequences with permutations for all companies
    train_sequences = []
    for company in all_companies:
        # Get industry
        industry = companies_df.loc[companies_df['Name'] == company, 'Industry'].values[0]
        industry_token = 'Industry_' + industry

        # Get products tokens and accelerators
        products_impl_list = company_products.get(company, [])  # List of lists of tokens
        accelerators = company_accelerators.get(company, [])  # List of accelerators with 'Accelerator_' prefix

        # Ensure the number of products matches the number of accelerators
        if len(products_impl_list) != len(accelerators):
            continue

        # Build paired_list
        paired_list = list(zip(products_impl_list, [acc.replace('Accelerator_', '') for acc in accelerators]))

        # Generate permutations
        permutations = generate_permutations_poisson(industry_token, paired_list, num_permutations=num_permutations, lambda_poisson=1.0)

        train_sequences.extend(permutations)

    # Train the N-Gram model
    ngram_model = create_ngram_model(n=n, k=k, base_tokens=accelerator_names_with_prefix)
    ngram_model.train(train_sequences)

    # Make recommendations for the sample context
    recommendations = ngram_model.recommend(sample_context, top_n=5)

    return recommendations

if __name__ == '__main__':
    # Run cross-validation tests
    run_tests(n=3, k=0.5, num_permutations=10)

    # Sample context tokens for N-Gram model recommendations
    sample_context = [
        'Industry_Sports Equipment',
        'Product_Tibco Spotfire',
        'implemented',
        'Category_Business Intelligence and Analytics'
    ]

    # Train N-Gram model and get recommendations
    recommendations = train_and_use_ngram_model(n=16, k=0.5, num_permutations=10, sample_context=sample_context)

    # Print the recommendations
    print("\nSample Recommendations from N-Gram Model:")
    print(recommendations)
