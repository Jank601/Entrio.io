import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


def load_dataset(filepath):
    """Load the dataset from CSV file.
    
    Args:
        filepath (str): Path to the CSV file
        
    Returns:
        DataFrame: Loaded pandas DataFrame or None if failed
    """
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Dataset loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return None


def remove_empty_rows(df):
    """Remove completely empty rows.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with empty rows removed
    """
    empty_mask = df.isna().all(axis=1) | (df.astype(str).apply(lambda x: x.str.strip()).eq('').all(axis=1))
    clean_df = df[~empty_mask].copy()
    logger.info(f"Removed {sum(empty_mask)} completely empty rows")
    return clean_df


def validate_company_name(df):
    """Validate and clean company names.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with validated company names
    """
    # Clean up company names - strip whitespace
    mask = ~df['company_name'].isna()
    df.loc[mask, 'company_name'] = df.loc[mask, 'company_name'].apply(
        lambda x: str(x).strip()
    )
    
    return df


def validate_urls(df, url_column='homepage_url'):
    """Validate and fix URLs.
    
    Args:
        df (DataFrame): Input DataFrame
        url_column (str): Name of the URL column
        
    Returns:
        DataFrame: DataFrame with fixed URLs
    """
    if url_column not in df.columns:
        logger.warning(f"Column '{url_column}' not found in the dataset")
        return df
    
    # Fix URLs that exist
    mask = ~df[url_column].isna()
    
    # Add http:// if missing and fix common URL issues
    df.loc[mask, url_column] = df.loc[mask, url_column].apply(
        lambda x: f"http://{x.strip()}" if not x.startswith(('http://', 'https://')) else x.rstrip('/').strip()
    )
    
    logger.info(f"Fixed URLs for {sum(mask)} rows")
    return df


def validate_status(df):
    """Validate and standardize company status values.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with standardized status values
    """
    if 'status' not in df.columns:
        return df
        
    # Define mapping for status standardization
    status_map = {
        'operating': 'operating',
        'active': 'operating',
        'closed': 'closed',
        'shutdown': 'closed',
        'out of business': 'closed',
        'acquired': 'acquired',
        'merged': 'acquired',
        'ipo': 'public',
        'public': 'public',
        'initial public offering': 'public'
    }
    
    # Standardize status values where they exist
    mask = ~df['status'].isna()
    if mask.any():
        # Convert to lowercase and strip whitespace
        df.loc[mask, 'status'] = df.loc[mask, 'status'].str.lower().str.strip()
        
        # Apply the mapping
        for idx in df[mask].index:
            current_status = df.at[idx, 'status']
            for key, value in status_map.items():
                if key in current_status:
                    df.at[idx, 'status'] = value
                    break
    
    logger.info(f"Standardized status values for {sum(mask)} rows")
    return df


def validate_date_column(df, date_column):
    """Validate and standardize date format for a specific column.
    
    Args:
        df (DataFrame): Input DataFrame
        date_column (str): Name of the date column to validate
        
    Returns:
        DataFrame: DataFrame with validated dates
    """
    if date_column not in df.columns:
        return df
    
    # Count non-empty dates
    mask = ~df[date_column].isna()
    
    try:
        # Convert to datetime, keeping as datetime objects
        df.loc[mask, date_column] = pd.to_datetime(df.loc[mask, date_column], errors='coerce')
        logger.info(f"Standardized {sum(mask)} dates in {date_column}")
    except Exception as e:
        logger.warning(f"Error standardizing {date_column}: {e}")
    
    return df


def validate_founded_month(df):
    """Validate and standardize founded_month column.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with validated founded_month
    """
    if 'founded_month' not in df.columns:
        return df
    
    # Process non-empty values
    mask = ~df['founded_month'].isna()
    
    try:
        # Convert to proper datetime objects
        df.loc[mask, 'founded_month'] = pd.to_datetime(df.loc[mask, 'founded_month'], errors='coerce')
        logger.info(f"Standardized {sum(mask)} founded_month values")
    except Exception as e:
        logger.warning(f"Error standardizing founded_month: {e}")
    
    return df


def validate_founded_quarter(df):
    """Validate founded_quarter column.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with validated founded_quarter
    """
    if 'founded_quarter' not in df.columns:
        return df
    
    # Check non-empty values
    mask = ~df['founded_quarter'].isna()
    logger.info(f"Checked {sum(mask)} founded_quarter values")
    
    return df


def validate_founded_year(df):
    """Validate founded_year column.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with validated founded_year
    """
    if 'founded_year' not in df.columns:
        return df
    
    # Check for invalid years - only reject future years
    current_year = datetime.now().year
    mask = ~df['founded_year'].isna()
    
    # Convert to numeric and only reject future years
    df.loc[mask, 'founded_year'] = pd.to_numeric(df.loc[mask, 'founded_year'], errors='coerce')
    future_mask = df['founded_year'] > current_year
    
    if sum(future_mask) > 0:
        df.loc[future_mask, 'founded_year'] = np.nan
        logger.info(f"Removed {sum(future_mask)} future years from founded_year")
    
    return df


def validate_country_state_codes(df):
    """Validate country and state codes.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with validated codes
    """
    # Ensure country codes are uppercase
    if 'country_code' in df.columns:
        mask = ~df['country_code'].isna()
        df.loc[mask, 'country_code'] = df.loc[mask, 'country_code'].str.upper()
        logger.info(f"Standardized {sum(mask)} country_code values")
    
    # Ensure state codes are uppercase
    if 'state_code' in df.columns:
        mask = ~df['state_code'].isna()
        df.loc[mask, 'state_code'] = df.loc[mask, 'state_code'].str.upper()
        logger.info(f"Standardized {sum(mask)} state_code values")
    
    return df


def validate_numeric_columns(df):
    """Validate numeric columns like funding_rounds and funding_total_usd.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with validated numeric columns
    """
    numeric_columns = ['funding_rounds', 'funding_total_usd']
    
    for column in numeric_columns:
        if column not in df.columns:
            continue
        
        # Ensure values are numeric and valid
        mask = ~df[column].isna()
        
        # Convert to numeric, coerce errors to NaN
        df.loc[mask, column] = pd.to_numeric(df.loc[mask, column], errors='coerce')
        
        # Check for negative values (invalid for these columns)
        negative_mask = (df[column] < 0)
        if sum(negative_mask) > 0:
            logger.warning(f"Found {sum(negative_mask)} negative values in {column} (converting to NaN)")
            df.loc[negative_mask, column] = np.nan
    
    return df


def clean_dataset(input_file, output_file):
    """Main function to clean the dataset.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        
    Returns:
        DataFrame: Cleaned DataFrame or None if operation failed
    """
    # Load the dataset
    df = load_dataset(input_file)
    if df is None:
        logger.error("Failed to load dataset.")
        return None
    
    # Initial dataset stats
    logger.info(f"Initial dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Step 1: Remove completely empty rows
    df = remove_empty_rows(df)
    
    # Step 2: Validate company names
    df = validate_company_name(df)
    
    # Step 3: Validate and fix URLs
    df = validate_urls(df, url_column='homepage_url')
    
    # Step 4: Validate status values
    df = validate_status(df)
    
    # Step 5: Validate date columns
    date_columns = ['company_founding_date', 'first_funding_round_at', 'last_funding_round_at']
    for column in date_columns:
        df = validate_date_column(df, column)
    
    # Step 6: Validate founded year, month, quarter
    df = validate_founded_year(df)
    df = validate_founded_month(df)
    df = validate_founded_quarter(df)
    
    # Step 7: Validate country and state codes
    df = validate_country_state_codes(df)
    
    # Step 8: Validate numeric columns
    df = validate_numeric_columns(df)
    
    # Final dataset stats
    logger.info(f"Final cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Save the cleaned dataset
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.realpath(output_file)), exist_ok=True)
        df.to_csv(output_file, index=False)
        logger.info(f"Cleaned dataset saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving cleaned dataset: {e}")
        return None
    
    return df