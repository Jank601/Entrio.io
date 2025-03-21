import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec


def main():
    """Execute the visualization pipeline for city frequency analysis.
    
    Locates the CSV file, processes the data and creates a comprehensive
    dashboard visualizing company distribution by city.
    
    Returns:
        None
    
    Raises:
        SystemExit: If the CSV file cannot be found.
    """
    # Set up file paths
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    base_dir = script_dir.parent
    
    # Try multiple potential locations for the CSV file
    csv_paths = [
        base_dir / "data" / "assignment_output.csv",
        script_dir / "assignment_output.csv",
        base_dir / "assignment_output.csv"
    ]
    
    csv_file = None
    for path in csv_paths:
        if path.exists():
            csv_file = path
            print(f"Found CSV file at: {csv_file}")
            break
    
    if not csv_file:
        print("Error: Could not find the CSV file.")
        sys.exit(1)
    
    # Define output paths
    output_dir = base_dir / "visualizations"
    output_dir.mkdir(exist_ok=True)
    
    dashboard_path = output_dir / "city_dashboard.png"
    
    # Load and process the data
    df = pd.read_csv(csv_file)
    df['city'] = df['city'].fillna('Unknown')
    
    # Create the dashboard
    create_focused_dashboard(df, dashboard_path)
    
    print(f"Dashboard saved to: {dashboard_path}")


def create_focused_dashboard(df, output_path):
    """Create a focused dashboard with multiple visualizations of city data.
    
    Args:
        df: DataFrame containing the company data.
        output_path: Path where the dashboard image will be saved.
        
    Returns:
        None
    """
    # Set up the figure with appropriate sizing
    plt.figure(figsize=(12, 10), dpi=100)
    gs = GridSpec(2, 2, figure=plt.gcf(), height_ratios=[1, 1.2])
    
    # Add dashboard title
    plt.suptitle('Company Distribution by City', fontsize=16, fontweight='bold', y=0.98)
    
    # Create individual panels
    ax1 = plt.subplot(gs[0, 0])
    create_top_cities_chart(df, ax1)
    
    ax2 = plt.subplot(gs[0, 1])
    create_countries_cities_chart(df, ax2)
    
    ax3 = plt.subplot(gs[1, :])
    create_city_table(df, ax3)
    
    # Finalize layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()


def create_top_cities_chart(df, ax):
    """Create a horizontal bar chart of top 15 cities by company count.
    
    Args:
        df: DataFrame containing the company data.
        ax: Matplotlib axis to plot on.
        
    Returns:
        None
    """
    # Get top 15 cities
    city_counts = df['city'].value_counts().head(15)
    
    # Create horizontal bar chart with color gradient
    colors = sns.color_palette("Blues_d", len(city_counts))
    bars = ax.barh(y=city_counts.index[::-1], width=city_counts.values[::-1], 
                  color=colors[::-1], height=0.7)
    
    # Add count labels inside the bars for better readability
    for i, bar in enumerate(bars):
        width = bar.get_width()
        if width > 0:
            ax.text(width/2, bar.get_y() + bar.get_height()/2, 
                   str(int(width)), ha='center', va='center', 
                   color='white', fontweight='bold')
    
    # Customize appearance for clean, professional look
    ax.set_title('Top 15 Cities by Number of Companies', fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('')
    ax.tick_params(axis='y', labelsize=9)
    ax.grid(axis='x', linestyle='--', alpha=0.6)


def create_countries_cities_chart(df, ax):
    """Create a nested bar chart showing top cities within top countries.
    
    Shows the top 3 cities in each of the top 5 countries by company count.
    
    Args:
        df: DataFrame containing the company data.
        ax: Matplotlib axis to plot on.
        
    Returns:
        None
    """
    # Get top 5 countries
    top_countries = df['country_code'].value_counts().head(5).index
    
    # Prepare data for plotting
    plot_data = []
    
    for country in top_countries:
        country_df = df[df['country_code'] == country]
        top_cities = country_df['city'].value_counts().head(3)
        
        for city, count in top_cities.items():
            plot_data.append({
                'Country': country,
                'City': city,
                'Count': count
            })
    
    # Convert to DataFrame for plotting
    plot_df = pd.DataFrame(plot_data)
    
    # Create color palette for countries
    colors = sns.color_palette("Blues", len(top_countries))
    country_color_map = {country: colors[i] for i, country in enumerate(top_countries)}
    
    # Prepare y-tick positions and labels
    ytick_positions = []
    ytick_labels = []
    
    # Plot each country-city combination with spacing between groups
    for i, (country, group) in enumerate(plot_df.groupby('Country')):
        group = group.sort_values('Count', ascending=False)
        
        positions = []
        start_pos = i * 4  # Space between country groups
        for j in range(len(group)):
            pos = start_pos + j * 0.8  # Space between cities in a country
            positions.append(pos)
            ytick_positions.append(pos)
            ytick_labels.append(f"{group.iloc[j]['City']} ({country})")
        
        # Plot bars with consistent color per country
        bars = ax.barh(
            positions,
            group['Count'].values,
            color=country_color_map[country],
            height=0.6
        )
        
        # Add count labels for each bar
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                       str(int(width)), ha='left', va='center', 
                       color='black', fontweight='bold', fontsize=8)
    
    # Apply labels to y-axis
    ax.set_yticks(ytick_positions)
    ax.set_yticklabels(ytick_labels, fontsize=8)
    
    # Customize appearance
    ax.set_title('Top 3 Cities in Each of the Top 5 Countries', fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('')
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    ax.set_xlim(0, None)  # Ensure x-axis starts at 0


def create_city_table(df, ax):
    """Create a detailed statistics table for the top 15 cities.
    
    Shows city, country, company count, average funding, most common status,
    and most common market for each city.
    
    Args:
        df: DataFrame containing the company data.
        ax: Matplotlib axis to place the table.
        
    Returns:
        None
    """
    # Calculate city statistics
    city_stats = []
    top_cities = df['city'].value_counts().head(15)
    
    for city, count in top_cities.items():
        city_df = df[df['city'] == city]
        
        # Extract key statistics
        country = city_df['country_code'].iloc[0] if not city_df.empty else 'Unknown'
        avg_funding = city_df['funding_total_usd'].mean() if not city_df.empty else 0
        
        # Format funding amount for readability
        funding_display = f"${avg_funding/1000000:.1f}M" if avg_funding >= 1000000 else f"${avg_funding/1000:.1f}K"
        
        # Find most common values
        most_common_status = city_df['status'].value_counts().index[0] if not city_df.empty else 'Unknown'
        markets = city_df['market'].value_counts()
        most_common_market = markets.index[0] if not markets.empty else 'Unknown'
        
        city_stats.append([
            city, 
            country, 
            count, 
            funding_display,
            most_common_status,
            most_common_market
        ])
    
    # Create the table
    table = ax.table(
        cellText=city_stats,
        colLabels=['City', 'Country', 'Companies', 'Avg Funding', 'Most Common Status', 'Most Common Market'],
        loc='center',
        cellLoc='center'
    )
    
    # Format and position the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    
    # Center table in available space
    num_columns = len(city_stats[0])
    total_width = num_columns
    ax_bbox = ax.get_position()
    table_width = total_width / 12
    ax.set_position([0.5 - table_width/2, ax_bbox.y0, table_width, ax_bbox.height])
    
    # Apply styles to the table cells
    for key, cell in table.get_celld().items():
        if key[0] == 0:  # Header row
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#08519c')
        else:
            cell.set_facecolor('#e6f2ff' if key[0] % 2 == 0 else 'white')
    
    # Hide axis elements
    ax.axis('off')
    ax.set_title('Top 15 Cities: Detailed Statistics', fontsize=12, pad=10)


if __name__ == "__main__":
    main()