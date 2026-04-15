import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class SovereignCloudWorkloadGenerator:
    """
    Generates synthetic cloud workload events simulating:
    - Normal workloads (legitimate user activity)
    - Anomalous workloads (data exfiltration, unauthorized access)
    - Geo-fencing violations (data residency breaches)
    """
    
    def __init__(self, num_events=10000):
        self.num_events = num_events
        self.events = []
        self.allowed_regions = ['ap-south-1', 'ap-south-2']  # Sovereign India regions only
        
    def generate_normal_workload(self, count):
        """Generate normal, compliant workload events"""
        events = []
        for _ in range(count):
            event = {
                'timestamp': datetime.now() - timedelta(seconds=random.randint(0, 86400)),
                'workload_id': f'wl_{random.randint(1000,9999)}',
                'cpu_usage_percent': np.random.normal(45, 15),  # Normal CPU: 30-60%
                'memory_usage_percent': np.random.normal(55, 12),  # Normal RAM: 40-70%
                'network_egress_mb': np.random.exponential(50),  # Normal egress: 0-200 MB
                'api_call_frequency': np.random.poisson(10),  # Normal API calls: 5-15/min
                'region': random.choice(self.allowed_regions),
                'user_role': random.choice(['viewer', 'operator', 'admin']),
                'data_classification': random.choice(['public', 'internal', 'confidential']),
                'is_anomaly': 0,
                'anomaly_type': 'none'
            }
            # Clamp values to realistic ranges
            event['cpu_usage_percent'] = min(100, max(0, event['cpu_usage_percent']))
            event['memory_usage_percent'] = min(100, max(0, event['memory_usage_percent']))
            events.append(event)
        return events
    
    def generate_data_exfiltration_events(self, count):
        """Simulate data exfiltration attempts (high egress, unusual hours)"""
        events = []
        for _ in range(count):
            event = {
                'timestamp': datetime.now() - timedelta(seconds=random.randint(0, 86400)),
                'workload_id': f'wl_{random.randint(1000,9999)}',
                'cpu_usage_percent': np.random.normal(70, 10),  # High CPU
                'memory_usage_percent': np.random.normal(75, 8),  # High memory
                'network_egress_mb': np.random.exponential(500),  # MASSIVE egress (500MB-2GB)
                'api_call_frequency': np.random.poisson(30),  # High API frequency
                'region': random.choice(self.allowed_regions),
                'user_role': random.choice(['viewer', 'operator']),  # Unauthorized role for data access
                'data_classification': random.choice(['confidential', 'restricted']),
                'is_anomaly': 1,
                'anomaly_type': 'data_exfiltration'
            }
            event['cpu_usage_percent'] = min(100, max(0, event['cpu_usage_percent']))
            event['memory_usage_percent'] = min(100, max(0, event['memory_usage_percent']))
            events.append(event)
        return events
    
    def generate_unauthorized_access_events(self, count):
        """Simulate unauthorized access attempts (role violations, weird hours)"""
        events = []
        for _ in range(count):
            # Unusual access hour (2 AM - 5 AM)
            unusual_hour = random.choice([2, 3, 4, 5])
            event = {
                'timestamp': datetime.now().replace(hour=unusual_hour, minute=random.randint(0,59)) - timedelta(days=random.randint(0,7)),
                'workload_id': f'wl_{random.randint(1000,9999)}',
                'cpu_usage_percent': np.random.normal(35, 10),  # Normal-ish CPU
                'memory_usage_percent': np.random.normal(40, 10),  # Normal-ish memory
                'network_egress_mb': np.random.exponential(30),  # Low egress
                'api_call_frequency': np.random.poisson(25),  # High frequency for probing
                'region': random.choice(self.allowed_regions),
                'user_role': 'viewer',  # Attempting to access restricted data
                'data_classification': 'restricted',  # Can't access this
                'is_anomaly': 1,
                'anomaly_type': 'unauthorized_access'
            }
            events.append(event)
        return events
    
    def generate_geo_fencing_violations(self, count):
        """Simulate data residency violations (access from non-sovereign regions)"""
        non_compliant_regions = ['us-east-1', 'eu-west-1', 'ap-northeast-1']
        events = []
        for _ in range(count):
            event = {
                'timestamp': datetime.now() - timedelta(seconds=random.randint(0, 86400)),
                'workload_id': f'wl_{random.randint(1000,9999)}',
                'cpu_usage_percent': np.random.normal(50, 15),
                'memory_usage_percent': np.random.normal(55, 12),
                'network_egress_mb': np.random.exponential(100),
                'api_call_frequency': np.random.poisson(15),
                'region': random.choice(non_compliant_regions),  # VIOLATION!
                'user_role': random.choice(['viewer', 'operator', 'admin']),
                'data_classification': random.choice(['confidential', 'restricted']),
                'is_anomaly': 1,
                'anomaly_type': 'geo_fencing_violation'
            }
            events.append(event)
        return events
    
    def generate_dataset(self):
        """Generate complete dataset with 70% normal, 30% anomalies"""
        normal_count = int(self.num_events * 0.70)
        exfil_count = int(self.num_events * 0.12)
        unauth_count = int(self.num_events * 0.10)
        geo_count = int(self.num_events * 0.08)
        
        print(f"Generating {self.num_events} workload events...")
        print(f"  - Normal: {normal_count}")
        print(f"  - Data Exfiltration: {exfil_count}")
        print(f"  - Unauthorized Access: {unauth_count}")
        print(f"  - Geo-fencing Violations: {geo_count}")
        
        self.events = []
        self.events.extend(self.generate_normal_workload(normal_count))
        self.events.extend(self.generate_data_exfiltration_events(exfil_count))
        self.events.extend(self.generate_unauthorized_access_events(unauth_count))
        self.events.extend(self.generate_geo_fencing_violations(geo_count))
        
        # Shuffle events
        random.shuffle(self.events)
        
        df = pd.DataFrame(self.events)
        return df

if __name__ == "__main__":
    generator = SovereignCloudWorkloadGenerator(num_events=10000)
    df = generator.generate_dataset()
    print(f"\nDataset shape: {df.shape}")
    print(df.head())
    print(f"\nAnomaly distribution:\n{df['anomaly_type'].value_counts()}")