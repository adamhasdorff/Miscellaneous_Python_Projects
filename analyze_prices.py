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

def investigate_price_spike(df):
    """
    looking @ jan 13-17 price spike
    """
    spike_data = df[(df['date'] >= pd.to_datetime('2024-01-13').date()) & 
                    (df['date'] <= pd.to_datetime('2024-01-17').date())]
    normal_data = df[~((df['date'] >= pd.to_datetime('2024-01-13').date()) & 
                       (df['date'] <= pd.to_datetime('2024-01-17').date()))]
    print("\n" + "="*60)
    print("Price Spike Analysis: Jan 13-17")
    print("="*60)

    print("\nSpike Period Stats:")
    print(f" Average Price: ${spike_data['price'].mean():.2f}/MWh")
    print(f" Max Price: ${spike_data['price'].max():.2f}/MWh")
    print(f" Min Price: ${spike_data['price'].min():.2f}/MWh")

    print("\nRest of Month Stats:")
    print(f" Average Price: ${normal_data['price'].mean():.2f}/MWh")
    print(f" Max Price: ${normal_data['price'].max():.2f}/MWh")
    print(f" Min Price: ${normal_data['price'].min():.2f}/MWh")

    print(f"\nPrice Increase: {((spike_data['price'].mean() / normal_data['price'].mean() - 1) *100):.1f}%")

    # Find the highest price hour
    max_price_row = spike_data.loc[spike_data['price'].idxmax()]
    print(f"\nHighest Price Occurred:")
    print(f"  Timestamp: {max_price_row['timestamp']}")
    print(f"  Price: ${max_price_row['price']:.2f}/MWh")
    print(f"  Hour: {max_price_row['hour']}")

    #plot compare
    fig, axes = plt.subplots(2, 1, figsize=(14,10))

    #Spike period detail
    axes[0].plot(spike_data['timestamp'], spike_data ['price'], linewidth = 2, color = 'red', marker = 'o', markersize = 3)
    axes[0].set_title('Price Spike Detail: Jan 13-14, 2024', fontsize = 12, fontweight = 'bold')
    axes[0].set_ylabel('Price ($/MWh)')
    axes[0].grid(True, alpha = 0.3)
    axes[0].axhline(spike_data['price'].mean(), color = 'orange', linestyle='--', label=f'Spike Avg: ${spike_data["price"].mean():.2f}')
    axes[0].legend()

    #hourly compare
    spike_hourly = spike_data.groupby('hour')['price'].mean()
    normal_hourly = normal_data.groupby('hour')['price'].mean()

    x = range(24)
    width = .4
    axes[1].bar([i - width/2 for i in x], normal_hourly, width, label = 'Rest of Month', color="#7a37e6", alpha = 0.8)
    axes[1].bar([i + width/2 for i in x], spike_hourly, width, label = 'Spike Period', color="#ec2d1f", alpha = 0.8)
    axes[1].set_title('Hourly Price Comparison', fontsize = 12, fontweight = 'bold')
    axes[1].set_ylabel('Average Price ($/MWh)')
    axes[1].set_xlabel('Hour of day')
    axes[1].set_xticks(x)
    axes[1].legend()
    axes[1].grid(True, alpha = 0.3, axis = 'y')

    plt.tight_layout()
    plt.savefig('plots/spike_analysis.png', dpi=300, bbox_inches = 'tight')
    print("\nSaved: plots/spike_analysis.png")
    plt.close()

def analyze_evening_valley(df):
    """
    Analyze why 9 PM has lowest prices
    """
    print("\n" + "="*60)
    print("EVENING PRICE VALLEY ANALYSIS")
    print("="*60)
    
    # Calculate average by hour
    hourly_stats = df.groupby('hour')['price'].agg(['mean', 'min', 'max', 'std']).reset_index()
    
    # Find cheapest hours
    cheapest_3 = hourly_stats.nsmallest(3, 'mean')
    most_expensive_3 = hourly_stats.nlargest(3, 'mean')
    
    print("\nCheapest Hours:")
    for _, row in cheapest_3.iterrows():
        print(f"  {int(row['hour']):02d}:00 - Avg: ${row['mean']:.2f}, Min: ${row['min']:.2f}, Max: ${row['max']:.2f}")
    
    print("\nMost Expensive Hours:")
    for _, row in most_expensive_3.iterrows():
        print(f"  {int(row['hour']):02d}:00 - Avg: ${row['mean']:.2f}, Min: ${row['min']:.2f}, Max: ${row['max']:.2f}")
    
    peak_hour = hourly_stats.loc[hourly_stats['mean'].idxmax(), 'hour']
    valley_hour = hourly_stats.loc[hourly_stats['mean'].idxmin(), 'hour']
    
    print(f"\nPeak-to-Valley Ratio: {hourly_stats['mean'].max() / hourly_stats['mean'].min():.2f}x")
    print(f"Peak Hour: {int(peak_hour):02d}:00")
    print(f"Valley Hour: {int(valley_hour):02d}:00")


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
    #generic plots
    plot_time_series(df)
    plot_hourly_pattern(df)
    plot_price_distribution(df)
    plot_daily_heatmap(df)
    #Investigative Plots
    #investigate_price_spike(df)
    #analyze_evening_valley(df)
    
    print("\nAll plots saved to 'plots/' directory!")