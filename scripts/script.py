# Create sample system resource monitoring data for visualization
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample data for system resource monitoring
np.random.seed(42)

# Create timestamps for 24 hours with 5-minute intervals
start_time = datetime.now() - timedelta(days=1)
timestamps = [start_time + timedelta(minutes=5*i) for i in range(288)]

# Generate realistic CPU and memory usage patterns
cpu_usage = []
memory_usage = []

for i, ts in enumerate(timestamps):
    # Create realistic patterns based on time of day
    hour = ts.hour
    
    # Higher usage during business hours (9-17)
    if 9 <= hour <= 17:
        base_cpu = 45 + np.random.normal(0, 10)
        base_memory = 65 + np.random.normal(0, 8)
    # Lower usage during night (22-6)
    elif hour >= 22 or hour <= 6:
        base_cpu = 15 + np.random.normal(0, 5)
        base_memory = 35 + np.random.normal(0, 5)
    # Moderate usage during other hours
    else:
        base_cpu = 30 + np.random.normal(0, 8)
        base_memory = 50 + np.random.normal(0, 7)
    
    # Add some spikes for realistic behavior
    if np.random.random() < 0.05:  # 5% chance of spike
        base_cpu += np.random.normal(25, 5)
        base_memory += np.random.normal(15, 3)
    
    # Ensure values are within realistic bounds
    cpu_usage.append(max(0, min(100, base_cpu)))
    memory_usage.append(max(0, min(100, base_memory)))

# Create DataFrame
resource_data = pd.DataFrame({
    'timestamp': timestamps,
    'cpu_usage': cpu_usage,
    'memory_usage': memory_usage
})

# Add some derived metrics
resource_data['cpu_threshold_exceeded'] = resource_data['cpu_usage'] > 80
resource_data['memory_threshold_exceeded'] = resource_data['memory_usage'] > 80
resource_data['combined_load'] = (resource_data['cpu_usage'] + resource_data['memory_usage']) / 2

# Display sample data
print("Sample System Resource Monitoring Data:")
print(resource_data.head(10))
print(f"\nTotal data points: {len(resource_data)}")
print(f"CPU Usage - Mean: {resource_data['cpu_usage'].mean():.1f}%, Max: {resource_data['cpu_usage'].max():.1f}%")
print(f"Memory Usage - Mean: {resource_data['memory_usage'].mean():.1f}%, Max: {resource_data['memory_usage'].max():.1f}%")
print(f"Threshold violations - CPU: {resource_data['cpu_threshold_exceeded'].sum()}, Memory: {resource_data['memory_threshold_exceeded'].sum()}")

# Save to CSV for the chart
resource_data.to_csv('system_resource_monitoring_data.csv', index=False)
print("\nData saved to system_resource_monitoring_data.csv")