import pandas as pd
import logging
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

def generate_prompt_for_status(company_info):
    """Generate a prompt to determine a company's status.
    
    Args:
        company_info (dict): Dictionary containing company information.
        
    Returns:
        str: Prompt for OpenAI API.
    """
    prompt = f"""
You are tasked with determining the current operational status of a company.
Based on the following information, predict the most likely status of the company.

Company Information:
- Name: {company_info.get('company_name', 'Unknown')}
- Market: {company_info.get('market', 'Unknown')}
- Country: {company_info.get('country_code', 'Unknown')}
- Region: {company_info.get('region', 'Unknown')}
- Founded Year: {company_info.get('founded_year', 'Unknown')}
- Homepage URL: {company_info.get('homepage_url', 'Unknown')}
- Funding Info: Total USD ${company_info.get('funding_total_usd', 'Unknown')}, Rounds: {company_info.get('funding_rounds', 'Unknown')}
- Last Funding: {company_info.get('last_funding_round_at', 'Unknown')}

Respond with ONLY one of these options: 'operating', 'closed', 'acquired', or 'public'.
No explanation or additional text.
"""
    return prompt

def generate_prompt_for_homepage_url(company_info):
    """Generate a prompt to determine a company's homepage URL.
    
    Args:
        company_info (dict): Dictionary containing company information.
        
    Returns:
        str: Prompt for OpenAI API.
    """
    prompt = f"""
You are tasked with finding the most likely homepage URL for a company.
Based on the following information, predict the most likely homepage URL.

Company Information:
- Name: {company_info.get('company_name', 'Unknown')}
- Market: {company_info.get('market', 'Unknown')}
- Country: {company_info.get('country_code', 'Unknown')}
- Permalink: {company_info.get('permalink', 'Unknown')}

Respond with ONLY a complete URL (starting with http:// or https://). 
For example: https://www.companyname.com
No explanation or additional text.
"""
    return prompt

def generate_prompt_for_city(company_info):
    """Generate a prompt to determine a company's headquarters city.
    
    Args:
        company_info (dict): Dictionary containing company information.
        
    Returns:
        str: Prompt for OpenAI API.
    """
    prompt = f"""
You are tasked with determining the most likely headquarters city for a company.
Based on the following information, predict the city where the company's headquarters is located.

Company Information:
- Name: {company_info.get('company_name', 'Unknown')}
- Market: {company_info.get('market', 'Unknown')}
- Country: {company_info.get('country_code', 'Unknown')}
- Region: {company_info.get('region', 'Unknown')}
- State: {company_info.get('state_code', 'Unknown')}

Respond with ONLY the city name. For example: 'San Francisco' or 'London'.
No explanation or additional text.
"""
    return prompt

def call_openai_api(client, prompt, model="gpt-4o-mini"):
    """Call the OpenAI API with a prompt.
    
    Args:
        client (OpenAI): OpenAI client.
        prompt (str): String prompt to send to API.
        model (str): String model name to use.
        
    Returns:
        str or None: API response if successful, None if fails.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful business research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  
            max_tokens=30  # Adequate for city names, status, etc.
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return None
    

def fill_missing_values(df, client):
    """Fill missing values in status, homepage_url, and city columns.
    
    Args:
        df (pandas.DataFrame): DataFrame with missing values.
        client (OpenAI): OpenAI client.
        
    Returns:
        pandas.DataFrame: DataFrame with filled values.
    """
    df_filled = df.copy()
    
    # Columns to fill
    columns_to_fill = ['status', 'homepage_url', 'city']
    
    # Get missing values per column
    missing_counts = {col: df[col].isna().sum() for col in columns_to_fill}
    logger.info(f"Missing values to fill: {missing_counts}")
    
    # Process each column
    for column in columns_to_fill:
        missing_mask = df[column].isna()
        missing_indices = df[missing_mask].index
        
        if len(missing_indices) == 0:
            logger.info(f"No missing values in column '{column}'")
            continue
        
        logger.info(f"Processing {len(missing_indices)} missing {column} values...")
        
        for idx in missing_indices:
            # Convert row to dictionary for prompt generation
            row_dict = df.loc[idx].to_dict()
            
            # Generate appropriate prompt
            if column == 'status':
                prompt = generate_prompt_for_status(row_dict)
            elif column == 'homepage_url':
                prompt = generate_prompt_for_homepage_url(row_dict)
            elif column == 'city':
                prompt = generate_prompt_for_city(row_dict)
            
            # Call OpenAI API (without excessive logging)
            response = call_openai_api(client, prompt)
            
            # Process response
            if response:
                # Simple validation
                if column == 'status':
                    valid_statuses = ['operating', 'closed', 'acquired', 'public']
                    response = response.lower()
                    if response in valid_statuses:
                        df_filled.at[idx, column] = response
                    else:
                        df_filled.at[idx, column] = 'operating'
                
                elif column == 'homepage_url':
                    if response.startswith(('http://', 'https://')):
                        df_filled.at[idx, column] = response
                    else:
                        df_filled.at[idx, column] = 'https://' + response.lstrip('www.')
                
                elif column == 'city':
                    df_filled.at[idx, column] = response
                
                logger.info(f"  - Added {column} for {row_dict.get('company_name', 'Unknown')}: {response}")
    
    return df_filled

def handle_missing_values(input_file, output_file, api_key):
    """Main function to handle missing values task.
    
    Args:
        input_file (str): Path to input CSV file.
        output_file (str): Path to output CSV file.
        api_key (str): OpenAI API key.
    
    Returns:
        pandas.DataFrame or None: DataFrame with filled missing values, or None if operation failed.
    """
    # Load the dataset
    df = load_dataset(input_file)
    if df is None:
        logger.error("Failed to load dataset.")
        return None
    
    # Setup OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Fill missing values
    df_filled = fill_missing_values(df, client)
    
    # Save to output file
    try:
        df_filled.to_csv(output_file, index=False)
        logger.info(f"Dataset with filled missing values saved to {output_file}")
    except Exception as e:
        error_msg = f"Error saving dataset to {output_file}: {e}"
        logger.error(error_msg)
        return None
    
    return df_filled