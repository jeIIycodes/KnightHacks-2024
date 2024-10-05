# Import necessary libraries
import pandas as pd
import numpy as np

# For collaborative filtering
from surprise import Dataset, Reader, SVD, KNNBasic
from surprise.model_selection import cross_validate, train_test_split

# For content-based filtering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# For evaluation
from sklearn.metrics import precision_score, recall_score

# For splitting data
from sklearn.model_selection import KFold

# Load the data
# Assuming the TSV files are in the current directory
accelerators_df = pd.read_csv('data/accelerators.tsv', sep='\t', header=0)
companies_df = pd.read_csv('data/companies.tsv', sep='\t', header=0)
entitlements_df = pd.read_csv('data/entitlements.tsv', sep='\t', header=0)
products_df = pd.read_csv('data/products.tsv', sep='\t', header=0)

# Display the head of each dataframe to check their structure
print("Accelerators DataFrame:")
print(accelerators_df.head(1))
print("\nCompanies DataFrame:")
print(companies_df.head())
print("\nEntitlements DataFrame:")
print(entitlements_df.head())
print("\nProducts DataFrame:")
print(products_df.head())

# Preprocessing and Data Integration
# Merge entitlements with companies to get company details
company_entitlements_df = entitlements_df.merge(companies_df, left_on='Company', right_on='Name', how='left')

# Merge accelerators with products to get product details
accelerators_products_df = accelerators_df.merge(products_df, left_on='Product', right_on='Name', how='left')


# Create a user-item interaction matrix for collaborative filtering
# For simplicity, we will assume that if a company has 'Implemented' a product, they have interacted with the 'TuneUp' accelerator
# If not, they have interacted with the 'Jumpstart' accelerator

# Create a function to assign accelerators based on implementation status
def assign_accelerator(row):
    if row['Implemented']:
        return accelerators_df[(accelerators_df['Product'] == row['Product']) & (accelerators_df['Type'] == 'TuneUp')][
            'Name'].values
    else:
        return \
        accelerators_df[(accelerators_df['Product'] == row['Product']) & (accelerators_df['Type'] == 'Jumpstart')][
            'Name'].values


company_entitlements_df['Accelerators'] = company_entitlements_df.apply(assign_accelerator, axis=1)

# Explode the accelerators column to have one accelerator per row
company_entitlements_df = company_entitlements_df.explode('Accelerators')

# Prepare data for the collaborative filtering model
# Create a DataFrame with columns: 'Company', 'Accelerator', 'Interaction'
# For simplicity, we can set Interaction = 1 (since we don't have explicit ratings)
interaction_df = company_entitlements_df[['Company', 'Accelerators']].copy()
interaction_df['Interaction'] = 1

# Remove duplicates
interaction_df.drop_duplicates(inplace=True)

print("\nInteraction DataFrame:")
print(interaction_df.head())

# Collaborative Filtering using Surprise Library
# Prepare the data in the format required by Surprise
reader = Reader(rating_scale=(0, 1))
data = Dataset.load_from_df(interaction_df[['Company', 'Accelerators', 'Interaction']], reader)


# Define a function to evaluate different collaborative filtering algorithms
def evaluate_collaborative_filtering(algo, data):
    # Perform cross-validation
    print(f"\nEvaluating {algo.__class__.__name__}...")
    cross_validate(algo, data, measures=['rmse', 'mse','mae'], cv=5, verbose=True)


# Evaluate SVD algorithm
svd_algo = SVD()
evaluate_collaborative_filtering(svd_algo, data)

# Evaluate KNNBasic algorithm
knn_algo = KNNBasic()
evaluate_collaborative_filtering(knn_algo, data)

# Content-Based Filtering
# Use the descriptions from accelerators and products to create feature vectors
# Combine product and accelerator descriptions
accelerators_products_df['Combined_Description'] = accelerators_products_df['Type'] + ' ' + \
                                                   accelerators_products_df['Description']

# Create a TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english')

# Fit and transform the combined descriptions
tfidf_matrix = tfidf_vectorizer.fit_transform(accelerators_products_df['Combined_Description'])

# Compute cosine similarity between accelerators
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Map accelerators to indices
accelerator_indices = pd.Series(accelerators_products_df.index,
                                index=accelerators_products_df['Name_x']).drop_duplicates()


# Function to get recommendations based on content
def get_content_recommendations(accelerator_name, cosine_sim=cosine_sim):
    idx = accelerator_indices[accelerator_name]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:4]  # Get top 3 similar accelerators
    accelerator_indices_list = [i[0] for i in sim_scores]
    return accelerators_products_df['Name_x'].iloc[accelerator_indices_list]


# Example usage
print("\nContent-Based Recommendations for 'Jumpstart Your ActiveCampaign':")
print(get_content_recommendations('Jumpstart Your ActiveCampaign'))

# Hybrid Approach
# Combine Collaborative Filtering and Content-Based Filtering
# For demonstration, we will average the scores from both methods

# First, get the list of all companies and accelerators
companies_list = interaction_df['Company'].unique()
accelerators_list = accelerators_df['Name'].unique()

# Build user profiles based on content
company_profiles = {}

for company in companies_list:
    # Get accelerators the company has interacted with
    company_accelerators = interaction_df[interaction_df['Company'] == company]['Accelerators']
    # Get the indices of these accelerators
    indices = [accelerator_indices[acc] for acc in company_accelerators if acc in accelerator_indices]
    # Compute the mean of their TF-IDF vectors
    if indices:
        company_profiles[company] = np.mean(tfidf_matrix[indices], axis=0)
    else:
        company_profiles[company] = np.zeros(tfidf_matrix.shape[1])


# Function to recommend accelerators to a company
def hybrid_recommendations(company, top_n=3):
    # Get the company profile
    company_profile = company_profiles[company]
    if company_profile.sum() == 0:
        # If the company has no interactions, recommend top accelerators based on popularity
        popular_accelerators = interaction_df['Accelerators'].value_counts().index[:top_n]
        return popular_accelerators
    # Compute similarity between company profile and all accelerators
    sim_scores = cosine_similarity(np.asarray(company_profile),  tfidf_matrix)
    sim_scores = list(enumerate(sim_scores[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # Get accelerators the company hasn't interacted with
    company_accelerators = set(interaction_df[interaction_df['Company'] == company]['Accelerators'])
    recommendations = []
    for idx, score in sim_scores:
        accelerator = accelerators_products_df['Name_x'].iloc[idx]
        if accelerator not in company_accelerators:
            recommendations.append((accelerator, score))
        if len(recommendations) == top_n:
            break
    return recommendations


# Example usage
print("\nHybrid Recommendations for 'AlphaArt':")
print(hybrid_recommendations('AlphaArt'))

# Evaluation of the Hybrid Model
# We can perform leave-one-out cross-validation

# Add a unique identifier for each interaction
interaction_df['Interaction_ID'] = range(len(interaction_df))

# Prepare the evaluation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

precision_list = []
recall_list = []

for train_index, test_index in kf.split(interaction_df):
    # Split the data
    train_df = interaction_df.iloc[train_index]
    test_df = interaction_df.iloc[test_index]

    # Build company profiles using train data
    companies_list = train_df['Company'].unique()
    company_profiles = {}
    for company in companies_list:
        company_accelerators = train_df[train_df['Company'] == company]['Accelerators']
        indices = [accelerator_indices[acc] for acc in company_accelerators if acc in accelerator_indices]
        if indices:
            company_profiles[company] = np.mean(tfidf_matrix[indices], axis=0)
        else:
            company_profiles[company] = np.zeros(tfidf_matrix.shape[1])

    # Test the model
    y_true = []
    y_pred = []
    for idx, row in test_df.iterrows():
        company = row['Company']
        actual_accelerator = row['Accelerators']
        # Get recommendations
        recommendations = hybrid_recommendations(company, top_n=3)
        recommended_accelerators = [rec[0] for rec in recommendations]
        # Record the true and predicted values
        y_true.append(1)
        if actual_accelerator in recommended_accelerators:
            y_pred.append(1)
        else:
            y_pred.append(0)

    # Calculate precision and recall
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    precision_list.append(precision)
    recall_list.append(recall)

print(f"\nHybrid Model Precision: {np.mean(precision_list)}")
print(f"Hybrid Model Recall: {np.mean(recall_list)}")
