import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

from data_cleaning import clean_dataset
from missing_values_handler import handle_missing_values
from add_street_feature import add_street_column

def main():
    """
    Main function to execute the data processing pipeline:
    Task 1: Clean the dataset
    Task 2: Handle missing values using OpenAI
    Task 3: Add street feature using OpenAI
    """
    # Define file paths - restoring the original structure
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, "data", "entrio_gen_ai_assignment_Q1_2025.csv")
    output_file = os.path.join(base_dir, "data", "assignment_output.csv")
    
     # Get API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable in a .env file.")
        sys.exit(1)
        
    # Task 1: Clean the dataset
    print("\n=== Task 1: Cleaning the Dataset ===")
    cleaned_df = clean_dataset(input_file, output_file)
    
    if cleaned_df is None:
        print("Error: Dataset cleaning failed.")
        sys.exit(1)
    
    print("\nTask 1 completed successfully!")
    
    # Task 2: Handle missing values
    print("\n=== Task 2: Handling Missing Values ===")
    print(f"Filling missing values in status, homepage_url, and city columns...")
    
    # Use the same output file as both input and output for Task 2
    filled_df = handle_missing_values(output_file, output_file, openai_api_key)
    
    if filled_df is None:
        print("Error: Handling missing values failed.")
        sys.exit(1)
    
    print(f"\nTask 2 completed successfully!")
    
     # Task 3: Add street feature
    print("\n=== Task 3: Adding Street Feature ===")
    print(f"Adding street feature using generative AI...")
    
    # Use the same output file as both input and output for Task 3
    updated_df = add_street_column(output_file, output_file, openai_api_key)
    
    if updated_df is None:
        print("Error: Adding street feature failed.")
        sys.exit(1)
    
    print(f"\nTask 3 completed successfully!")
    print(f"Final data saved to: {output_file}")

if __name__ == "__main__":
    main()