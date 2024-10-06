# utils/data_manager.py

import os
import pandas as pd
import shutil
import random
import numpy as np
import logging

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
            raise

        # Define accelerator types to add
        accelerator_types = ['Jumpstart', '  Up']

        for acc_type in accelerator_types:
            accelerator_name = f"{acc_type} Your {product_name}"
            short_description = f"Kickstart your adoption of {product_name}!" if acc_type == 'Jumpstart' else f"Tune up your use of {product_name}!"
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
                # Convert to DataFrame
                accel_entry_df = pd.DataFrame([accel_entry])
                # Concatenate
                updated_accelerators_df = pd.concat([accelerators_df, accel_entry_df], ignore_index=True)
                # Save back to accelerators.tsv
                updated_accelerators_df.to_csv(accelerators_path, sep='\t', index=False)
                logger.info(f"Added accelerator '{accelerator_name}' to {accelerators_path}.")

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
