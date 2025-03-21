import pandas as pd
from datetime import datetime
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)


def load_dataset(filepath):
    """
    Load the dataset and return a pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame: The loaded dataset
    """
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Dataset loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return None


def identify_empty_rows(df):
    """
    Identify completely empty rows.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Series: Boolean mask with True for empty rows
    """
    empty_mask = (df.isna().sum(axis=1) == df.shape[1])
    
    # Also consider rows where all values are empty strings
    empty_string_mask = (df.astype(str).apply(lambda x: x.str.strip() == '').all(axis=1))
    
    combined_mask = empty_mask | empty_string_mask
    logger.info(f"Identified {combined_mask.sum()} empty rows out of {len(df)}.")
    
    return combined_mask


def identify_corrupt_rows(df):
    """
    Identify corrupt or unusable rows based on defined criteria.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Series: Boolean mask with True for corrupt rows
    """
    corrupt_mask = pd.Series(False, index=df.index)
    
    # Critical missing values - company_name is the most critical
    if 'company_name' in df.columns:
        corrupt_mask |= df['company_name'].isna()
    
    # Check consistency between founding dates and years if both exist
    date_columns = [col for col in df.columns if 'found' in col.lower() and 'date' in col.lower()]
    year_columns = [col for col in df.columns if 'found' in col.lower() and 'year' in col.lower()]
    
    if date_columns and year_columns:
        date_col = date_columns[0]
        year_col = year_columns[0]
        
        # Convert dates to datetime
        dates_temp = pd.to_datetime(df[date_col], errors='coerce')
        # Only for rows where both values exist
        valid_mask = (~df[date_col].isna()) & (~df[year_col].isna())
        
        if valid_mask.any():
            year_from_dates = dates_temp[valid_mask].dt.year
            years_from_col = df.loc[valid_mask, year_col].astype(float)
            
            # Check if years match (allowing for string/numeric type differences)
            year_mismatch = abs(year_from_dates - years_from_col) > 1
            corrupt_mask.loc[valid_mask] |= year_mismatch
    
    # Check for invalid founding years (if they exist)
    if year_columns:
        current_year = datetime.now().year
        for col in year_columns:
            year_mask = ~df[col].isna()
            if year_mask.any():
                try:
                    # Try to convert to numeric, coerce errors to NaN
                    years = pd.to_numeric(df.loc[year_mask, col], errors='coerce')
                    invalid_years = (years < 1800) | (years > current_year)
                    corrupt_mask.loc[year_mask] |= invalid_years
                except Exception as e:
                    logger.warning(f"Error validating years in {col}: {e}")
    
    # Check for invalid funding amounts (negative values)
    funding_columns = [col for col in df.columns if 'funding' in col.lower() and 'usd' in col.lower()]
    for col in funding_columns:
        mask = ~df[col].isna()
        if mask.any():
            try:
                # Convert to numeric, coerce errors to NaN
                values = pd.to_numeric(df.loc[mask, col], errors='coerce')
                invalid_values = values < 0
                corrupt_mask.loc[mask] |= invalid_values
            except Exception as e:
                logger.warning(f"Error validating funding in {col}: {e}")
    
    logger.info(f"Identified {corrupt_mask.sum()} corrupt rows beyond empty rows.")
    return corrupt_mask

def fix_urls(df, url_column='homepage_url'):
    """
    Fix common URL issues.
    
    Args:
        df: DataFrame containing URLs
        url_column: Column name containing URLs
        
    Returns:
        DataFrame: DataFrame with fixed URLs
    """
    df_fixed = df.copy()
    
    if url_column not in df.columns:
        logger.warning(f"Column '{url_column}' not found in the dataset.")
        return df_fixed
    
    # Skip NaN values
    mask = ~df[url_column].isna()
    
    # Fix common issues
    for idx in df[mask].index:
        url = df.at[idx, url_column]
        if isinstance(url, str):
            url = url.strip()
            
            # Add http:// if missing
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            # Remove trailing slashes
            url = url.rstrip('/')
            
            # Remove extra spaces
            url = url.strip()
            
            df_fixed.at[idx, url_column] = url
    
    logger.info(f"Fixed URLs for dataset.")
    return df_fixed


def standardize_date_formats(df):
    """
    Standardize date formats in the dataset.
    
    Args:
        df: DataFrame containing date columns
        
    Returns:
        DataFrame: DataFrame with standardized dates
    """
    df_fixed = df.copy()
    
    # Detect date columns based on name and content
    potential_date_columns = [
        col for col in df.columns 
        if any(term in col.lower() for term in ['date', '_at', 'founding'])
    ]
    
    for col in potential_date_columns:
        non_null_mask = ~df[col].isna()
        if non_null_mask.any():
            try:
                # Try to convert to datetime
                dates = pd.to_datetime(df.loc[non_null_mask, col], errors='coerce')
                # Only update if conversion was successful
                valid_dates_mask = ~dates.isna()
                if valid_dates_mask.any():
                    # Format as YYYY-MM-DD
                    df_fixed.loc[non_null_mask, col] = dates.dt.strftime('%Y-%m-%d')
                    logger.info(f"Standardized {valid_dates_mask.sum()} dates in column '{col}'")
            except Exception as e:
                logger.warning(f"Error standardizing dates in column '{col}': {e}")
    
    return df_fixed


def standardize_status(df, status_column='status'):
    """
    Standardize company status values.
    
    Args:
        df: DataFrame containing status column
        status_column: Column name with status
        
    Returns:
        DataFrame: DataFrame with standardized status values
    """
    df_fixed = df.copy()
    
    if status_column not in df.columns:
        logger.warning(f"Column '{status_column}' not found in the dataset.")
        return df_fixed
    
    # Skip NaN values
    mask = ~df[status_column].isna()
    
    # Lowercase and strip whitespace
    df_fixed.loc[mask, status_column] = df.loc[mask, status_column].astype(str).str.lower().str.strip()
    
    # Map variations to standard terms
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
    
    # Apply mapping where possible
    for idx in df_fixed[mask].index:
        status = df_fixed.at[idx, status_column]
        for key, value in status_map.items():
            if key in status:
                df_fixed.at[idx, status_column] = value
                break
    
    logger.info(f"Standardized status values in the dataset.")
    return df_fixed


def clean_dataset(input_file, output_file):
    """
    Clean the dataset by removing empty/corrupt rows and standardizing values.
    
    Args:
        input_file: Path to the input CSV file
        output_file: Path to save the cleaned CSV file
        
    Returns:
        DataFrame: The cleaned dataset
    """
    # Load the dataset
    df = load_dataset(input_file)
    if df is None:
        logger.error("Failed to load dataset.")
        return None
    
    # Basic dataset information
    logger.info(f"Dataset has {df.shape[0]} rows and {df.shape[1]} columns.")
    duplicates_count = df.duplicated().sum()
    logger.info(f"Dataset has {duplicates_count} duplicate rows.")
    
    # Identify empty and corrupt rows
    empty_mask = identify_empty_rows(df)
    corrupt_mask = identify_corrupt_rows(df)
    
    # Remove empty and corrupt rows
    df_cleaned = df[~(empty_mask | corrupt_mask)].copy()
    removed_count = df.shape[0] - df_cleaned.shape[0]
    logger.info(f"Removed {removed_count} problematic rows ({removed_count/df.shape[0]:.2%} of the dataset).")
    
    # Fix URLs if homepage_url column exists
    if 'homepage_url' in df_cleaned.columns:
        df_cleaned = fix_urls(df_cleaned, url_column='homepage_url')
    
    # Standardize date formats
    df_cleaned = standardize_date_formats(df_cleaned)
    
    # Standardize status if status column exists
    if 'status' in df_cleaned.columns:
        df_cleaned = standardize_status(df_cleaned)
    
    # Reset index
    df_cleaned.reset_index(drop=True, inplace=True)
    
    # Save to output file
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_cleaned.to_csv(output_file, index=False)
        logger.info(f"Cleaned dataset saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving cleaned dataset: {e}")
    
    return df_cleaned