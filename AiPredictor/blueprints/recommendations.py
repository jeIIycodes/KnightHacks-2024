# blueprints/recommendations.py
"""
Example of Interacting with the Accelerator Recommendation API

This script demonstrates how to send a POST request to the
`/recommend/get_recommendations` endpoint of the Flask API and interpret
the JSON response containing accelerator recommendations.

Prerequisites:
- The Flask server must be running locally on port 8000.
- The `products.tsv` and `accelerators.tsv` data files must be properly configured.

Usage:
- You can use the `curl` command in your terminal to interact with the API.
- Alternatively, you can use Python's `requests` library to make the request programmatically.

Below is an example using the `curl` command, followed by the expected response.
"""

# Example `curl` Command to Request Recommendations:

# curl -X POST http://localhost:8000/recommend/get_recommendations \
#      -H "Content-Type: application/json" \
#      -d '{
#            "company_name": "AlphaArt",
#            "implemented_products": ["Alteryx","BetaRix"],
#            "implemented_products_is_implemented": [false, false],
#            "industry": "Art Subscription Box",
#            "program_start_date": "2022-05-09",
#            "company_size": 50,
#            "location": "New York, USA",
#            "Optional Company Description": "Hey, this is what we do and how we do it.",
#            "current_challenges": ["Data analytics automation", "Customer engagement"],
#            "number_of_recommendations": 3
#          }'

# Explanation of the JSON Payload:
# {
#   "company_name": "AlphaArt",                                   // Mandatory: Name of the company
#   "implemented_products": ["Alteryx","BetaRix"],               // List of products used by the company
#   "implemented_products_is_implemented": [false, false],       // Corresponding implementation status of each product
#   "industry": "Art Subscription Box",                           // Mandatory: Industry sector of the company
#   "program_start_date": "2022-05-09",                          // (Optional) Start date of the program
#   "company_size": 50,                                           // (Optional) Number of employees
#   "location": "New York, USA",                                  // (Optional) Geographic location
#   "Optional Company Description": "Hey, this is what we do and how we do it.", // (Optional) Description of the company
#   "current_challenges": ["Data analytics automation", "Customer engagement"], // (Optional) Current challenges faced
#   "number_of_recommendations": 3                                // (Optional) Number of recommendations to return (1-20)
# }

# Expected JSON Response:
# {
#   "company_name": "AlphaArt",
#   "industry": "Art Subscription Box",
#   "recommendations": [
#     {
#       "accelerator": "Jumpstart Your Alteryx",
#       "category": "Category_Business Intelligence and Analytics",
#       "description": "Kickstart your adoption of Alteryx!"
#     },
#     {
#       "accelerator": "Jumpstart Your QlikView",
#       "category": "Category_Business Intelligence and Analytics",
#       "description": "Kickstart your adoption of QlikView!"
#     },
#     {
#       "accelerator": "Jumpstart Your Monday.com",
#       "category": "Category_Project Management",
#       "description": "Kickstart your adoption of Monday.com!"
#     }
#   ]
# }

# Breakdown of the Response:
# {
#   "company_name": "AlphaArt",                                   // Echoes the input company name
#   "industry": "Art Subscription Box",                           // Echoes the input industry
#   "recommendations": [                                          // List of recommended accelerators
#     {
#       "accelerator": "Jumpstart Your Alteryx",                  // Name of the accelerator
#       "category": "Category_Business Intelligence and Analytics", // Category fetched from products.tsv based on the associated product
#       "description": "Kickstart your adoption of Alteryx!"       // Description from accelerators.tsv
#     },
#     {
#       "accelerator": "Jumpstart Your QlikView",
#       "category": "Category_Business Intelligence and Analytics",
#       "description": "Kickstart your adoption of QlikView!"
#     },
#     {
#       "accelerator": "Jumpstart Your Monday.com",
#       "category": "Category_Project Management",
#       "description": "Kickstart your adoption of Monday.com!"
#     }
#   ]
# }

# Additional Notes:
# - The `number_of_recommendations` parameter allows you to specify how many
#   recommendations you want the API to return, within the range of 1 to 20.
# - If `number_of_recommendations` is not provided, the API defaults to returning 5 recommendations.
# - The API validates the input to ensure that `number_of_recommendations` is an integer between 1 and 20.
# - If invalid input is provided (e.g., `number_of_recommendations` is 25), the API responds with an error message and a 400 status code.

# Example of Handling the Response Programmatically Using Python's `requests` Library:

from flask import Blueprint, request, jsonify
import hashlib
import pandas as pd
import os
from AiPredictor.model_factory import create_ngram_model
from AiPredictor.utils.data_loader import load_data
from AiPredictor.Testing import generate_permutations_poisson  # Ensure this import path is correct

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/recommend')

# Load products.tsv and accelerators.tsv
# Ensure these files have 'Name', 'Category', and 'Description' columns for products.tsv
# and 'Name', 'Product', 'ShortDescription', 'Type' for accelerators.tsv
products_file_path = os.path.join('data', 'products.tsv')
accelerators_file_path = os.path.join('data', 'accelerators.tsv')

# Verify that the files exist
if not os.path.exists(products_file_path):
    raise FileNotFoundError(f"{products_file_path} not found.")
if not os.path.exists(accelerators_file_path):
    raise FileNotFoundError(f"{accelerators_file_path} not found.")

products_df = pd.read_csv(products_file_path, sep='\t')
accelerators_df = pd.read_csv(accelerators_file_path, sep='\t')


# Initialize the N-Gram model
def initialize_ngram_model(n=16, k=0.5, num_permutations=10):
    """
    Initialize and train the N-Gram model with existing data.

    Args:
        n (int): The 'n' in N-Gram.
        k (float): Smoothing parameter.
        num_permutations (int): Number of permutations to generate.

    Returns:
        NGramModel: Trained N-Gram model instance.
    """
    # Load data
    companies_df, company_products, company_accelerators, _ = load_data()
    accelerator_names_with_prefix = ["Accelerator_" + name for name in accelerators_df['Name'].tolist()]
    all_companies = companies_df['Name'].tolist()

    # Generate training sequences with permutations for all companies
    train_sequences = []
    for company in all_companies:
        # Get industry
        industry_series = companies_df.loc[companies_df['Name'] == company, 'Industry']
        if industry_series.empty:
            print(f"Company '{company}' has no industry info, skipping.")
            continue
        industry = industry_series.values[0]
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
        permutations = generate_permutations_poisson(
            industry_token, paired_list, num_permutations=num_permutations, lambda_poisson=1.0
        )

        train_sequences.extend(permutations)

    # Initialize and train N-Gram model
    ngram_model = create_ngram_model(n=n, k=k, base_tokens=accelerator_names_with_prefix)
    ngram_model.train(train_sequences)

    return ngram_model


# Initialize the model at blueprint load
ngram_model = initialize_ngram_model(n=16, k=0.5, num_permutations=10)


@recommendations_bp.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """
    Endpoint to get accelerator recommendations based on company data.

    Expected JSON payload:
    {
      "company_name": "AlphaArt", (mandatory)
      "implemented_products": ["Alteryx","Baseline","App++"],
      "implemented_products_is_implemented": [True,False,True],
      "industry": "Art Subscription Box", (mandatory)
      "program_start_date": "2022-05-09", // calendar select
      "company_size": 50, (for future use)
      "location": "New York, USA", (for future use)
      "Optional Company Description": "Hey this is what we do and how we do it", (for future use)
      "current_challenges": ["Data analytics automation", "Customer engagement"], (for future use)
      "number_of_recommendations": 5 // optional, integer between 1 and 20
    }
    """
    data = request.get_json()

    # Validate mandatory fields
    mandatory_fields = ['company_name', 'industry']
    missing_fields = [field for field in mandatory_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing mandatory field(s): {", ".join(missing_fields)}'}), 400

    company_name = data['company_name']
    industry = data['industry']
    implemented_products = data.get('implemented_products', [])
    implemented_products_is_implemented = data.get('implemented_products_is_implemented', [])

    # Validate implemented_products and their implementation status
    if len(implemented_products) != len(implemented_products_is_implemented):
        return jsonify(
            {'error': 'Length of implemented_products and implemented_products_is_implemented must be equal.'}), 400

    # Handle optional 'number_of_recommendations' parameter
    number_of_recommendations = data.get('number_of_recommendations', 5)  # Default to 5 if not provided

    # Validate 'number_of_recommendations' if provided
    if 'number_of_recommendations' in data:
        if not isinstance(number_of_recommendations, int):
            return jsonify({'error': "'number_of_recommendations' must be an integer."}), 400
        if not (1 <= number_of_recommendations <= 20):
            return jsonify({'error': "'number_of_recommendations' must be between 1 and 20."}), 400

    # Create context tokens
    context_tokens = []
    industry_token = 'Industry_' + industry
    context_tokens.append(industry_token)

    for product, is_implemented in zip(implemented_products, implemented_products_is_implemented):
        product_token = 'Product_' + product
        impl_status = 'implemented' if is_implemented else 'not_implemented'

        # Fetch category from products_df based on Product
        product_info = products_df[products_df['Name'] == product]
        if not product_info.empty:
            category = 'Category_' + product_info.iloc[0]['Category']
        else:
            category = 'Category_Unknown'
            print(f"Product '{product}' not found in products.tsv. Assigning 'Category_Unknown'.")

        context_tokens.extend([product_token, impl_status, category])

    # Use the N-Gram model to get recommendations
    recommendations = ngram_model.recommend(context_tokens, top_n=number_of_recommendations)

    # Fetch category and description for each recommended accelerator
    recommendations_detailed = []
    for accel in recommendations:
        accel_name = accel.replace('Accelerator_', '')  # Remove prefix if necessary

        # Fetch accelerator info from accelerators_df
        accel_info = accelerators_df[accelerators_df['Name'] == accel_name]

        if not accel_info.empty:
            product = accel_info.iloc[0]['Product']
            # Fetch category from products_df based on Product
            product_info = products_df[products_df['Name'] == product]
            if not product_info.empty:
                category = 'Category_' + product_info.iloc[0]['Category']
            else:
                category = 'Category_Unknown'
                print(f"Product '{product}' for accelerator '{accel_name}' not found in products.tsv. Assigning 'Category_Unknown'.")

            description = accel_info.iloc[0].get('ShortDescription', '')
        else:
            category = 'Unknown'
            description = ''
            print(
                f"Accelerator '{accel_name}' not found in accelerators.tsv. Assigning 'Unknown' category and empty description.")

        recommendations_detailed.append({
            'accelerator': accel_name,
            'category': category,
            'description': description
        })

    return jsonify({
        'company_name': company_name,
        'industry': industry,
        'recommendations': recommendations_detailed
    }), 200
