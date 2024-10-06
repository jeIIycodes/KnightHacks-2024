# utils/data_loader.py

import pandas as pd

def load_data():
    """
    Load and preprocess the datasets. Returns the preprocessed data needed for the models.

    Returns:
        companies_df: DataFrame of companies.
        company_products: Mapping from companies to products and implementation status.
        company_accelerators: Mapping from companies to accelerators.
        accelerators_df: DataFrame of accelerators.
    """
    # Load the data
    accelerators_df = pd.read_csv('data/accelerators.tsv', sep='\t', header=0)
    companies_df = pd.read_csv('data/companies.tsv', sep='\t', header=0)
    entitlements_df = pd.read_csv('data/company_entitlements.tsv', sep='\t', header=0)
    products_df = pd.read_csv('data/products.tsv', sep='\t', header=0)

    # Merge products with entitlements to get product details including Category
    entitlements_df = entitlements_df.merge(
        products_df[['Name', 'Category']],
        left_on='Product',
        right_on='Name',
        how='left',
        suffixes=('', '_Product')
    )

    # Merge entitlements with companies to get company name and industry
    entitlements_df = entitlements_df.merge(
        companies_df[['Name', 'Industry']],
        left_on='Company',
        right_on='Name',
        how='left',
        suffixes=('', '_Company')
    )

    # Create a mapping from Company to their products, implementation status, and categories as separate tokens
    company_products = entitlements_df.groupby('Company').apply(
        lambda x: [
            ['Product_' + row['Product'], 'implemented' if row['Implemented'] else 'not_implemented', 'Category_' + row['Category']]
            for idx, row in x.iterrows()
        ]
    ).to_dict()

    # Create a mapping from Company to their accelerators
    company_accelerators = entitlements_df.groupby('Company')['Accelerator'].apply(
        lambda accelerators: ['Accelerator_' + acc for acc in accelerators]
    ).to_dict()

    return companies_df, company_products, company_accelerators, accelerators_df
