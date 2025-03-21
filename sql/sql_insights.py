import os
import pandas as pd
from pandasql import sqldf
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_query(query):
    """
    Execute SQL query on the 'companies' DataFrame in global namespace.
    
    Args:
        query (str): SQL query string to execute
        
    Returns:
        pandas.DataFrame: Query results as a DataFrame
    """
    pysqldf = lambda q: sqldf(q, globals())
    return pysqldf(query)

def main():
    """
    Main function to execute SQL queries on the cleaned dataset.
    
    This function:
    1. Loads the cleaned CSV file into a pandas DataFrame
    2. Executes each SQL query from separate files
    3. Displays and saves the query results
    """
    # Define file paths based on your directory structure
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from the sql directory to the root
    root_dir = os.path.dirname(base_dir)
    
    # Specify the exact input file in the data folder on the root
    csv_file = os.path.join(root_dir, "data", "assignment_output.csv")
    
    # Create results folder if it doesn't exist
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        logging.error(f"File {csv_file} not found. Please ensure it exists.")
        return
    
    df = pd.read_csv(csv_file)
    # Make DataFrame available globally for SQL queries to reference
    globals()['companies'] = df
    
    # Load SQL queries from files - must use the exact filenames from the original files
    query_files = [
        os.path.join(base_dir, "cities_count.sql"),
        os.path.join(base_dir, "extract_domains.sql"),
        os.path.join(base_dir, "funding_extremes.sql"),
        os.path.join(base_dir, "funding_by_year.sql")
    ]
    
    for query_file in query_files:
        try:
            # Check if the SQL file exists before attempting to read it
            if not os.path.exists(query_file):
                logging.warning(f"SQL file {query_file} not found. Skipping this query.")
                continue
                
            query_name = os.path.basename(query_file).replace('.sql', '')
            
            with open(query_file, 'r') as f:
                query = f.read()
                
            result = run_query(query)
            
            logging.info(f"Results for '{query_name}':")
            if len(result) > 10:
                logging.info(f"\n{result.head(10)}")
                logging.info(f"(Showing 10 of {len(result)} rows)")
            else:
                logging.info(f"\n{result}")
            
            output_file = os.path.join(results_dir, f"{query_name}_result.csv")
            result.to_csv(output_file, index=False)
            
        except Exception as e:
            logging.error(f"Error executing query from {query_file}: {e}")

if __name__ == "__main__":
    main()