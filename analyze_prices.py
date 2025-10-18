import pandas as pd
import matplotlib.pyplot as plt

def load_and_clean_data(filepath='data/caiso_prices.csv'):
    """
    Load the CAISO data and clean it up
    """
    df = pd.read_csv(filepath)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['INTERVALSTARTTIME_GMT'])
    
    # Filter for just total LMP prices (not components)
    lmp_data = df[df['LMP_TYPE'] == 'LMP'].copy()
    
    # Rename MW column to price for clarity
    lmp_data['price'] = lmp_data['MW']
    
    # Extract useful time features
    lmp_data['date'] = lmp_data['timestamp'].dt.date
    lmp_data['hour'] = lmp_data['timestamp'].dt.hour
    lmp_data['day_of_week'] = lmp_data['timestamp'].dt.dayofweek
    
    # Sort by timestamp
    lmp_data = lmp_data.sort_values('timestamp').reset_index(drop=True)
    
    return lmp_data

def calculate_statistics(df):
    """
    Calculate basic price statistics
    """
    stats = {
        'mean': df['price'].mean(),
        'median': df['price'].median(),
        'std': df['price'].std(),
        'min': df['price'].min(),
        'max': df['price'].max(),
        'count': len(df)
    }
    
    return stats

def plot_time_series(df):
    """
    Plot prices over time
    """
    plt.figure(figsize=(14, 6))
    plt.plot(df['timestamp'], df['price'], linewidth=1, color='#2563eb')
    plt.title('CAISO Day-Ahead LMP Prices - January 2024', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Price ($/MWh)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('plots/price_timeseries.png', dpi=300, bbox_inches='tight')
    print("Saved: plots/price_timeseries.png")
    plt.close()

def plot_hourly_pattern(df):
    """
    Plot average price by hour of day
    """
    hourly_avg = df.groupby('hour')['price'].agg(['mean', 'std']).reset_index()
    
    plt.figure(figsize=(12, 6))
    plt.bar(hourly_avg['hour'], hourly_avg['mean'], color='#10b981', alpha=0.7, edgecolor='black')
    plt.errorbar(hourly_avg['hour'], hourly_avg['mean'], yerr=hourly_avg['std'], 
                 fmt='none', color='black', capsize=3, alpha=0.5)
    plt.title('Average Price by Hour of Day', fontsize=14, fontweight='bold')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Price ($/MWh)')
    plt.xticks(range(0, 24))
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('plots/hourly_pattern.png', dpi=300, bbox_inches='tight')
    print("Saved: plots/hourly_pattern.png")
    plt.close()

def plot_price_distribution(df):
    """
    Plot histogram of prices
    """
    plt.figure(figsize=(10, 6))
    plt.hist(df['price'], bins=50, color='#8b5cf6', alpha=0.7, edgecolor='black')
    plt.axvline(df['price'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${df["price"].mean():.2f}')
    plt.axvline(df['price'].median(), color='green', linestyle='--', linewidth=2, label=f'Median: ${df["price"].median():.2f}')
    plt.title('Price Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Price ($/MWh)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('plots/price_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: plots/price_distribution.png")
    plt.close()

def plot_daily_heatmap(df):
    """
    Create a heatmap showing prices by day and hour
    """
    # Create pivot table
    pivot = df.pivot_table(values='price', index='hour', columns='date', aggfunc='mean')
    
    plt.figure(figsize=(14, 8))
    im = plt.imshow(pivot.values, aspect='auto', cmap='RdYlGn_r', interpolation='nearest')
    plt.colorbar(im, label='Price ($/MWh)')
    plt.title('Price Heatmap: Hour vs Day', fontsize=14, fontweight='bold')
    plt.ylabel('Hour of Day')
    plt.xlabel('Date')
    plt.yticks(range(24), range(24))
    
    # Show every 3rd date on x-axis
    dates = [str(d) for d in pivot.columns]
    plt.xticks(range(0, len(dates), 3), dates[::3], rotation=45)
    
    plt.tight_layout()
    plt.savefig('plots/price_heatmap.png', dpi=300, bbox_inches='tight')
    print("Saved: plots/price_heatmap.png")
    plt.close()

if __name__ == "__main__":
    # Create plots directory
    import os
    os.makedirs('plots', exist_ok=True)
    
    # Load and clean
    df = load_and_clean_data()
    
    print("Cleaned Data Preview:")
    print(df[['timestamp', 'price', 'hour', 'date']].head(10))
    print("\nData shape:", df.shape)
    
    # Calculate stats
    stats = calculate_statistics(df)
    print("\nPrice Statistics:")
    for key, value in stats.items():
        print(f"  {key}: ${value:.2f}")
    
    # Create all plots
    print("\nGenerating plots...")
    plot_time_series(df)
    plot_hourly_pattern(df)
    plot_price_distribution(df)
    plot_daily_heatmap(df)
    
    print("\nAll plots saved to 'plots/' directory!")