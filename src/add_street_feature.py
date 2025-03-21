import pandas as pd
import logging
import time
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)

def load_dataset(filepath):
    """Load the dataset from a CSV file.
    
    Args:
        filepath (str): Path to the CSV file.
        
    Returns:
        pandas.DataFrame or None: The loaded dataset if successful, None otherwise.
    """
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return None

def generate_prompt_for_street(company_info):
    """
    Generate a prompt to determine a company's street address.
    
    Args:
        company_info: Dictionary containing company information
        
    Returns:
        String: Prompt for OpenAI API
    """
    prompt = f"""
You are tasked with determining the most likely street address for a company's headquarters.
Based on the following information, predict the street address where the company is located.

Company Information:
- Name: {company_info.get('company_name', 'Unknown')}
- Country: {company_info.get('country_code', 'Unknown')}
- Region: {company_info.get('region', 'Unknown')}
- State: {company_info.get('state_code', 'Unknown')}
- City: {company_info.get('city', 'Unknown')}

Respond with ONLY the street address (street name and number). For example: '18 Main Street' or '2 Technology Drive'.
Do not include city, state, or country in your response. Do not include apartment/suite numbers.
No explanation or additional text.
"""
    return prompt

def call_openai_api(client, prompt, model="gpt-4o-mini", max_retries=3):
    """
    Call the OpenAI API with a prompt and handle rate limiting.
    
    Args:
        client: OpenAI client
        prompt: String prompt to send to API
        model: String model name to use
        max_retries: Maximum number of retry attempts for rate limiting
        
    Returns:
        String: API response or None if all retries fail
    """
    retries = 0
    while retries <= max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful business location research assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  
                max_tokens=50  # Keep 50 tokens for street addresses
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            
            if "rate limit" in str(e).lower() and retries < max_retries:
                wait_time = 20 * (2 ** retries)  # Exponential backoff
                logger.warning(f"Rate limited. Retry {retries+1}/{max_retries}. Backing off for {wait_time} seconds.")
                time.sleep(wait_time)
                retries += 1
                continue
            else:
                return None
    
    logger.error(f"Failed to call OpenAI API after {max_retries} retries")
    return None

def add_street_feature(df, client):
    """
    Add street feature to the dataset using OpenAI.
    
    Args:
        df: DataFrame to process
        client: OpenAI client
        
    Returns:
        DataFrame: DataFrame with new street feature
    """
    df_with_street = df.copy()
    
    # Add the new street column
    df_with_street['street'] = None
    
    # Process each row
    total_rows = len(df_with_street)
    logger.info(f"Adding street feature to {total_rows} rows...")
    
    for idx in df_with_street.index:
        # Convert row to dictionary for prompt generation
        row_dict = df_with_street.loc[idx].to_dict()
        
        # Generate prompt for street address
        prompt = generate_prompt_for_street(row_dict)
        
        # Call OpenAI API
        response = call_openai_api(client, prompt)
        
        # Process response
        if response:
            df_with_street.at[idx, 'street'] = response
        else:
            # If API fails, use a placeholder value
            df_with_street.at[idx, 'street'] = ""
        
        # Add minimal delay to avoid rate limiting
        time.sleep(1)
    
    logger.info("Street feature added successfully.")
    return df_with_street

def add_street_column(input_file, output_file, api_key):
    """Main function to add street feature to the dataset.
    
    Args:
        input_file (str): Path to input CSV file.
        output_file (str): Path to output CSV file.
        api_key (str): OpenAI API key.
    
    Returns:
        pandas.DataFrame or None: DataFrame with new street feature, or None if operation failed.
    """
    # Load the dataset
    df = load_dataset(input_file)
    if df is None:
        logger.error("Failed to load dataset.")
        return None
    
    # Setup OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Add street feature
    df_with_street = add_street_feature(df, client)
    
    # Save to output file
    try:
        df_with_street.to_csv(output_file, index=False)
        logger.info(f"Dataset with added street feature saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving dataset: {e}")
        return None