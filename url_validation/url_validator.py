import os
import pandas as pd
import logging
import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging to only show our logs
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Silence OpenAI and other HTTP logs
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

def validate_url(args):
    """Validate if a URL is valid and active using OpenAI.
    
    Args:
        args: Tuple containing (client, idx, url)
        
    Returns:
        Tuple: (idx, result)
    """
    client, idx, url = args
    
    # Skip empty URLs
    if pd.isna(url) or not url:
        return (idx, "No")
    
    try:        
        prompt = f"Is this URL valid and active: {url}? Answer ONLY with Yes or No, NOTHING ELSE."
        
        response = client.responses.create(
            model="gpt-4o-mini",
            tools=[{"type": "web_search_preview", "search_context_size": "low"}],
            input=prompt
        )
        
        result = response.output_text.strip()
        
        return (idx, "Yes" if "YES" in result.upper() else "No")
        
    except Exception as e:
        logger.error(f"Error with {url}: {e}")
        return (idx, "No")

def main():
    """Validate URLs in the dataset and add validation results."""
    # Load API key
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OpenAI API key not found")
        return
    
    # Initialize OpenAI client once
    client = OpenAI(api_key=api_key)
    
    # Define file path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "data", "assignment_output.csv")
    
    # Load the dataset
    try:
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded dataset with {len(df)} rows")
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return
    
    # Add valid_url column if it doesn't exist
    if 'valid_url' not in df.columns:
        df['valid_url'] = None
    
    # Create a list of tasks for URLs that need processing
    tasks = []
    for idx, row in df.iterrows():
        # Skip already processed URLs
        if pd.notna(df.at[idx, 'valid_url']):
            continue
        
        url = row['homepage_url']
        tasks.append((client, idx, url))
    
    # Set up parallel processing
    max_workers = 5  # Adjust based on rate limits
    
    if not tasks:
        logger.info("No URLs to process")
        return
    
    # Process URLs in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and process results as they complete
        for idx, result in executor.map(validate_url, tasks):
            df.at[idx, 'valid_url'] = result
    
    # Save results
    df.to_csv(csv_file, index=False)
    logger.info(f"Finished - results saved")

if __name__ == "__main__":
    main()