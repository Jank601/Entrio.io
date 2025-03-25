# Entrio GenAI Solutions Technical Assignment

## Project Overview
This project implements a data processing pipeline for startup company data as part of the Entrio GenAI Solutions technical assignment. The pipeline demonstrates capabilities in data analysis, validation, prompt engineering, process automation, and business intelligence.

The solution processes company data from Crunchbase, cleans and enriches it using AI, performs SQL-based analysis, and generates visualizations - showcasing practical applications of data science and AI in business contexts.

## Features
- **Data Cleaning & Validation**: Removes corrupt data and standardizes formats
- **AI-Powered Data Enrichment**: Uses OpenAI's GPT-4o-mini to fill missing values and generate new data
- **SQL Analytics**: Performs business intelligence queries on the processed data
- **Data Visualization**: Creates visual representations of key insights

## Project Structure
```
/
├── data/                      # Data storage
│   ├── entrio_gen_ai_assignment_Q1_2025.csv  # Input dataset
│   └── assignment_output.csv  # Processed output
├── sql/                       # SQL analytics
│   ├── cities_count.sql       # Query: Company count by city
│   ├── extract_domains.sql    # Query: Extract domains from URLs
│   ├── funding_extremes.sql   # Query: Companies with most/least funding
│   ├── funding_by_year.sql    # Query: Funding by founding year
│   ├── sql_insights.py        # Python script to run SQL queries
│   └── results/               # Query results storage
├── src/                       # Source code
│   ├── data_cleaning.py       # Module for data validation and cleaning
│   ├── missing_values_handler.py  # Module to fill missing values with AI
│   ├── add_street_feature.py  # Module to add street addresses with AI
│   └── main.py                # Main execution script
├── url_validation/            # URL validation functionality
│   └── url_validator.py       # Script to validate URLs are active using OpenAI
├── visualization/
│   └── visualization.py       # City distribution visualization script
├── .env                       # Environment variables (API keys)
├── .gitignore                 # Git ignore configuration
└── requirements.txt           # Python dependencies
```

## Requirements
- Python 3.8+
- OpenAI API key (for missing value processing and street feature generation)
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository (if applicable)

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Running the Full Pipeline

To execute the complete data processing pipeline:

```bash
python src/main.py
```

This performs:
1. Data cleaning (Task 1)
2. Missing value handling with AI (Task 2)
3. Street feature addition with AI (Task 3)

### Post-Processing: URL Validation

After completing the main pipeline, run this additional URL validation step:

```bash
python url_validation/url_validator.py
```

This script uses OpenAI's API to check if each company's homepage URL is valid and active, adding a new `valid_url` column to the dataset with "Yes" or "No" values. The validation runs in parallel threads for efficiency while respecting API rate limits.

**Note**: This validation step is separated from the main pipeline to avoid re-running the token-consuming AI steps (Tasks 2 and 3) that have already been completed.

### Running SQL Analysis

After the pipeline has processed the data:

```bash
python sql/sql_insights.py
```

This executes the four SQL queries and saves results to the `sql/results/` directory.

### Generating Visualizations

To create the city distribution visualization:

```bash
python visualization/visualization.py
```

## Tasks Breakdown

### Task 1: Cleaning the Dataset
The data cleaning module:
- Identifies and removes completely empty rows
- Detects corrupt rows with inconsistencies between founding dates and years
- Validates funding amounts (removing negative values)
- Standardizes date formats and company status values

### Additional URL Validation Step
A separate post-processing step to enhance data quality:
- Uses OpenAI's API to determine if each homepage URL is valid and active
- Adds a new `valid_url` column to the dataset with "Yes" or "No" values
- Processes URLs in parallel with proper rate limit handling
- Implemented as a separate step to avoid re-running token-consuming AI operations

### Task 2: Handling Missing Values
Uses OpenAI's GPT-4o-mini to intelligently fill missing values for:
- Company status: Predicts whether a company is operating, closed, acquired, or public
- Homepage URL: Generates the most likely URL based on company information
- City: Determines the probable headquarters city based on region and other location data

### Task 3: Adding Street Feature
Utilizes AI to generate a plausible street address for each company based on:
- Company name
- Country, region, state, and city information
- Industry context

### Task 4: SQL Analytics
Performs four analytical queries:
1. Counts company frequency by city
2. Extracts main domains from company URLs
3. Identifies companies with the highest and lowest funding
4. Calculates funding totals grouped by founding year

### Task 5: Visualization (Bonus)
Creates a bar chart showing the distribution of companies by headquarters city, including:
- Company counts for each city
- Statistical summary of the dataset
- Professional formatting and styling

## Implementation Details

### AI Integration
The project leverages OpenAI's GPT-4o-mini model to:
- Generate synthetically plausible data for missing values
- Create high-quality street address data based on limited location information
- Each API call is carefully designed with prompts optimized for factual responses

### Data Processing Approach
- **Robust Error Handling**: Comprehensive exception management throughout the pipeline
- **Logging**: Detailed operation logs for monitoring and debugging
- **Data Validation**: Multiple validation steps ensure data quality

### SQL Implementation
- Uses PandasSQL to execute SQL queries directly on DataFrame objects
- Query results are saved as CSV files for easy review and sharing

## Performance Considerations
- Batch processing is implemented where appropriate
- The pipeline is designed to be resilient against common errors

## Author
Eli Yagel

---

*Note: This README provides a comprehensive overview of the project. For specific implementation details, please refer to the code comments within each file.*