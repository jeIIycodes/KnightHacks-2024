# utils/data_manager.py

import os
import pandas as pd
import shutil
import random
import numpy as np
import logging
import os
import pandas as pd
import shutil
import random
import numpy as np
import logging
import csv
from io import StringIO
from flask import Response, jsonify  # If not already imported

from AiPredictor.db import users_collection, test_connection  # Ensure this is correctly pointing to your DB module

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_tsv(file_path, expected_columns=3):
    """
    Validates that each row in the TSV file has the expected number of columns.

    Args:
        file_path (str): Path to the TSV file.
        expected_columns (int): Number of expected columns.

    Raises:
        ValueError: If any row does not match the expected column count.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            fields = line.strip().split('\t')
            if len(fields) != expected_columns:
                raise ValueError(f"Line {i} in {file_path} does not have {expected_columns} columns. Found {len(fields)}: {fields}")


def sanitize_field(field):
    """
    Sanitizes a field by replacing tab characters with spaces.

    Args:
        field (str): The field to sanitize.

    Returns:
        str: Sanitized field.
    """
    if isinstance(field, str):
        return field.replace('\t', ' ').strip()
    return field


def add_artificial_datapoints(n, product_name, description, category, percent_implemented,
                              company_name="ARTIFICIAL",
                              update_productsTsv=False,
                              update_acceleratorsTsv=False):
    # Validate input parameters
    if not isinstance(n, int) or n < 1:
        raise ValueError("Parameter 'n' must be a positive integer.")

    if not (0 <= percent_implemented <= 100):
        raise ValueError("Parameter 'percent_implemented' must be between 0 and 100.")

    # Define file paths
    data_dir = 'data'
    entitlements_path = os.path.join(data_dir, 'entitlements.tsv')
    products_path = os.path.join(data_dir, 'products.tsv')
    accelerators_path = os.path.join(data_dir, 'accelerators.tsv')

    # Check if entitlements.tsv exists
    if not os.path.exists(entitlements_path):
        raise FileNotFoundError(f"{entitlements_path} not found.")

    # Validate TSV before reading
    validate_tsv(entitlements_path, expected_columns=3)

    # Calculate number of implemented and not implemented entries
    num_implemented = int(round(n * (percent_implemented / 100)))
    num_not_implemented = n - num_implemented

    # Create entries with sanitized fields
    entries = []
    for _ in range(num_implemented):
        entry = {
            'Company': sanitize_field(company_name),
            'Implemented': 'TRUE',
            'Product': sanitize_field(product_name)
        }
        entries.append(entry)

    for _ in range(num_not_implemented):
        entry = {
            'Company': sanitize_field(company_name),
            'Implemented': 'FALSE',
            'Product': sanitize_field(product_name)
        }
        entries.append(entry)

    # Append to entitlements.tsv using pd.concat()
    entitlements_df = pd.DataFrame(entries)
    try:
        # Read existing entitlements
        existing_entitlements_df = pd.read_csv(entitlements_path, sep='\t')
    except pd.errors.ParserError as e:
        logger.error(f"Failed to parse {entitlements_path}: {e}")
        logger.info("Attempting to restore from backup.")
        restore_backup()
        raise

    # Concatenate new entries
    updated_entitlements_df = pd.concat([existing_entitlements_df, entitlements_df], ignore_index=True)

    # Save back to entitlements.tsv
    updated_entitlements_df.to_csv(entitlements_path, sep='\t', index=False)

    # Validate TSV after writing
    validate_tsv(entitlements_path, expected_columns=3)

    logger.info(
        f"Added {n} entries to {entitlements_path} (Implemented: {num_implemented}, Not Implemented: {num_not_implemented}).")

    # Optionally update products.tsv
    if update_productsTsv:
        if not os.path.exists(products_path):
            raise FileNotFoundError(f"{products_path} not found.")

        # Load existing products
        try:
            products_df = pd.read_csv(products_path, sep='\t')
        except pd.errors.ParserError as e:
            logger.error(f"Failed to parse {products_path}: {e}")
            logger.info("Attempting to restore from backup.")
            restore_backup()
            raise

        # Check if product already exists
        if product_name in products_df['Name'].values:
            logger.info(f"Product '{product_name}' already exists in {products_path}. Skipping addition.")
        else:
            # Create new product entry with sanitized fields
            new_product = {
                'Category': sanitize_field(category),
                'Name': sanitize_field(product_name),
                'Description': sanitize_field(description)
            }
            # Convert to DataFrame
            new_product_df = pd.DataFrame([new_product])
            # Concatenate
            updated_products_df = pd.concat([products_df, new_product_df], ignore_index=True)
            # Save back to products.tsv
            updated_products_df.to_csv(products_path, sep='\t', index=False)
            logger.info(f"Added product '{product_name}' to {products_path}.")

    # Optionally update accelerators.tsv
    if update_acceleratorsTsv:
        if not os.path.exists(accelerators_path):
            raise FileNotFoundError(f"{accelerators_path} not found.")

        # Load existing accelerators
        try:
            accelerators_df = pd.read_csv(accelerators_path, sep='\t')
        except pd.errors.ParserError as e:
            logger.error(f"Failed to parse {accelerators_path}: {e}")
            logger.info("Attempting to restore from backup.")
            restore_backup()
            raise

        # Define accelerator types to add
        accelerator_types = ['Jumpstart', 'TuneUp']

        # Collect new accelerator entries
        new_accelerators = []
        for acc_type in accelerator_types:
            accelerator_name = f"{acc_type} Your {product_name}"
            short_description = (
                f"Kickstart your adoption of {product_name}!" if acc_type == 'Jumpstart'
                else f"TuneUp your use of {product_name}!"
            )
            accel_entry = {
                'Name': sanitize_field(accelerator_name),
                'Product': sanitize_field(product_name),
                'ShortDescription': sanitize_field(short_description),
                'Type': acc_type
            }

            # Check if accelerator already exists
            if accelerator_name in accelerators_df['Name'].values:
                logger.info(
                    f"Accelerator '{accelerator_name}' already exists in {accelerators_path}. Skipping addition.")
            else:
                new_accelerators.append(accel_entry)

        # If there are new accelerators, concatenate and update the file
        if new_accelerators:
            new_accel_df = pd.DataFrame(new_accelerators)
            updated_accelerators_df = pd.concat([accelerators_df, new_accel_df], ignore_index=True)
            # Save back to accelerators.tsv
            updated_accelerators_df.to_csv(accelerators_path, sep='\t', index=False)
            logger.info(f"Added new accelerators to {accelerators_path}.")

    logger.info("Artificial datapoints addition complete.")


def restore_backup():
    """
    Restores the backup of .tsv files from data/backups/ to data/.

    Assumes that the backup directory contains the original .tsv files:
    - entitlements.tsv
    - products.tsv
    - accelerators.tsv

    Raises:
        FileNotFoundError: If backup files are missing.
    """
    # Define directories
    data_dir = 'data'
    backup_dir = os.path.join(data_dir, 'backups')

    # List of .tsv files to restore
    tsv_files = ['entitlements.tsv', 'products.tsv', 'accelerators.tsv']

    for file in tsv_files:
        backup_file = os.path.join(backup_dir, file)
        target_file = os.path.join(data_dir, file)

        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file {backup_file} not found.")

        # Copy backup to target location, overwriting existing files
        shutil.copyfile(backup_file, target_file)
        logger.info(f"Restored {file} from backup.")

    logger.info("All backup files have been restored successfully.")


def make_backup():
    """
    Creates a backup of the current .tsv files in data/ by copying them to data/backups/.

    Overwrites existing backup files if they already exist.

    Raises:
        FileNotFoundError: If source .tsv files are missing.
        Exception: If backup directory cannot be created.
    """
    # Define directories
    data_dir = 'data'
    backup_dir = os.path.join(data_dir, 'backups')

    # List of .tsv files to backup
    tsv_files = ['entitlements.tsv', 'products.tsv', 'accelerators.tsv']

    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir)
            logger.info(f"Created backup directory at {backup_dir}.")
        except Exception as e:
            logger.error(f"Failed to create backup directory: {e}")
            raise

    for file in tsv_files:
        source_file = os.path.join(data_dir, file)
        backup_file = os.path.join(backup_dir, file)

        if not os.path.exists(source_file):
            raise FileNotFoundError(f"Source file {source_file} not found.")

        # Copy source file to backup location, overwriting if necessary
        shutil.copyfile(source_file, backup_file)
        logger.info(f"Backed up {file} to {backup_file}.")

    logger.info("Backup of .tsv files completed successfully.")

def import_from_mongodb():
    """
    Imports data from MongoDB and writes to multiple TSV files:
    - companies.tsv
    - company_entitlements.tsv
    - entitlements.tsv
    - products.tsv
    - semantic_info.tsv

    Raises:
        Exception: If any operation fails during the import process.
    """
    try:
        # Step 1: Create a Backup Before Making Changes
        make_backup()

        # Step 2: Define File Paths
        data_dir = 'data'
        companies_path = os.path.join(data_dir, 'companies.tsv')
        company_entitlements_path = os.path.join(data_dir, 'company_entitlements.tsv')
        entitlements_path = os.path.join(data_dir, 'entitlements.tsv')
        products_path = os.path.join(data_dir, 'products.tsv')
        semantic_info_path = os.path.join(data_dir, 'semantic_info.tsv')

        # Step 3: Initialize DataFrames or Create Files if They Don't Exist
        if os.path.exists(companies_path):
            companies_df = pd.read_csv(companies_path, sep='\t')
        else:
            companies_df = pd.DataFrame(columns=['Name', 'Industry', 'programStart'])

        if os.path.exists(company_entitlements_path):
            company_entitlements_df = pd.read_csv(company_entitlements_path, sep='\t')
        else:
            company_entitlements_df = pd.DataFrame(columns=['Company', 'Product', 'Implemented', 'Accelerator'])

        if os.path.exists(entitlements_path):
            entitlements_df = pd.read_csv(entitlements_path, sep='\t')
        else:
            entitlements_df = pd.DataFrame(columns=['Company', 'Implemented', 'Product'])

        if os.path.exists(products_path):
            products_df = pd.read_csv(products_path, sep='\t')
        else:
            products_df = pd.DataFrame(columns=['Name', 'Industry', 'programStart'])

        if os.path.exists(semantic_info_path):
            semantic_info_df = pd.read_csv(semantic_info_path, sep='\t')
        else:
            semantic_info_df = pd.DataFrame(columns=['username_hash', 'company_size', 'challenges'])

        # Step 4: Fetch Data from MongoDB
        logger.info("Fetching data from MongoDB...")
        records = users_collection.find()

        # Step 5: Process Each Record
        for record in records:
            username_hash = record.get('username_hash')
            company_name = record.get('company_name', 'UnknownCompany')
            company_size = record.get('company_size', 'UnknownSize')
            challenges = record.get('challenges', [])
            industry = record.get('industry', 'UnknownIndustry')
            program_start = record.get('programStart', 'UnknownDate')
            products = record.get('products', [])
            accelerators = record.get('accelerators', [])

            # Sanitize username_hash to use as Company identifier
            company_identifier = sanitize_field(username_hash)

            # ---- Update companies.tsv ----
            if company_identifier not in companies_df['Name'].values:
                new_company = pd.DataFrame([{
                    'Name': company_identifier,
                    'Industry': industry,
                    'programStart': program_start
                }])
                companies_df = pd.concat([companies_df, new_company], ignore_index=True)
                logger.info(f"Added company '{company_identifier}' to companies.tsv.")

            # ---- Update semantic_info.tsv ----
            if company_identifier not in semantic_info_df['username_hash'].values:
                challenges_str = '; '.join(challenges) if isinstance(challenges, list) else challenges
                new_semantic_info = pd.DataFrame([{
                    'username_hash': company_identifier,
                    'company_size': company_size,
                    'challenges': challenges_str
                }])
                semantic_info_df = pd.concat([semantic_info_df, new_semantic_info], ignore_index=True)
                logger.info(f"Added semantic info for company '{company_identifier}' to semantic_info.tsv.")

            # ---- Update products.tsv ----
            for product in products:
                product_name = sanitize_field(product.get('product_name', 'UnknownProduct'))
                product_industry = sanitize_field(product.get('industry', industry))  # Use product's industry or company's
                product_program_start = sanitize_field(product.get('programStart', program_start))

                if product_name not in products_df['Name'].values:
                    new_product = pd.DataFrame([{
                        'Name': product_name,
                        'Industry': product_industry,
                        'programStart': product_program_start
                    }])
                    products_df = pd.concat([products_df, new_product], ignore_index=True)
                    logger.info(f"Added product '{product_name}' to products.tsv.")

                # ---- Update entitlements.tsv ----
                implemented = 'TRUE' if product.get('implemented', False) else 'FALSE'
                new_entitlement = pd.DataFrame([{
                    'Company': company_identifier,
                    'Implemented': implemented,
                    'Product': product_name
                }])
                if not ((entitlements_df['Company'] == company_identifier) &
                        (entitlements_df['Product'] == product_name)).any():
                    entitlements_df = pd.concat([entitlements_df, new_entitlement], ignore_index=True)
                    logger.info(
                        f"Added entitlement for product '{product_name}' under company '{company_identifier}' to entitlements.tsv.")

                # ---- Update company_entitlements.tsv ----
                for acc in accelerators:
                    acc_type = sanitize_field(acc.get('type', 'UnknownType'))
                    if acc_type not in ['Jumpstart', 'TuneUp']:
                        logger.warning(f"Unknown accelerator type '{acc_type}' for company '{company_identifier}'. Skipping.")
                        continue

                    accelerator_name = f"{acc_type} Your {product_name}"
                    new_company_entitlement = pd.DataFrame([{
                        'Company': company_identifier,
                        'Product': product_name,
                        'Implemented': implemented,
                        'Accelerator': accelerator_name
                    }])

                    if not ((company_entitlements_df['Company'] == company_identifier) &
                            (company_entitlements_df['Product'] == product_name) &
                            (company_entitlements_df['Accelerator'] == accelerator_name)).any():
                        company_entitlements_df = pd.concat([company_entitlements_df, new_company_entitlement],
                                                            ignore_index=True)
                        logger.info(
                            f"Added company entitlement '{accelerator_name}' for product '{product_name}' under company '{company_identifier}' to company_entitlements.tsv.")

        # Step 6: Save Updated DataFrames Back to TSV Files
        logger.info("Saving updated TSV files...")
        companies_df.to_csv(companies_path, sep='\t', index=False)
        semantic_info_df.to_csv(semantic_info_path, sep='\t', index=False)
        products_df.to_csv(products_path, sep='\t', index=False)
        entitlements_df.to_csv(entitlements_path, sep='\t', index=False)
        company_entitlements_df.to_csv(company_entitlements_path, sep='\t', index=False)
        logger.info("All TSV files have been updated successfully.")

    except Exception as e:
        logger.error(f"Error during MongoDB import: {str(e)}")
        restore_backup()
        raise

