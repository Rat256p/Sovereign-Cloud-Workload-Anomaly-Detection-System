import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import warnings
warnings.filterwarnings('ignore')

class IsolationForestDetector:
    """Isolation Forest for anomaly detection - fast and interpretable"""
    
    def __init__(self, contamination=0.25, random_state=42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            max_samples='auto'
        )
        self.scaler = StandardScaler()
        
    def prepare_features(self, df):
        """Extract numerical features for anomaly detection"""
        features = df[['cpu_usage_percent', 'memory_usage_percent', 
                       'network_egress_mb', 'api_call_frequency']].copy()
        
        # Add derived features
        features['cpu_memory_ratio'] = features['cpu_usage_percent'] / (features['memory_usage_percent'] + 1e-5)
        features['egress_per_api_call'] = features['network_egress_mb'] / (features['api_call_frequency'] + 1e-5)
        
        return features
    
    def fit(self, df):
        features = self.prepare_features(df)
        scaled_features = self.scaler.fit_transform(features)
        self.model.fit(scaled_features)
        return self
    
    def predict(self, df):
        features = self.prepare_features(df)
        scaled_features = self.scaler.transform(features)
        predictions = self.model.predict(scaled_features)
        # Convert: 1 = normal, -1 = anomaly -> 0 = normal, 1 = anomaly
        return (predictions == -1).astype(int)


class AutoencoderDetector(nn.Module):
    """Deep Autoencoder for anomaly detection - captures complex patterns"""
    
    def __init__(self, input_dim=6, hidden_dims=[32, 16, 8]):
        super(AutoencoderDetector, self).__init__()
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, h_dim))
            encoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder
        decoder_layers = []
        prev_dim = hidden_dims[-1]
        for h_dim in reversed(hidden_dims[:-1]):
            decoder_layers.append(nn.Linear(prev_dim, h_dim))
            decoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
    
    def fit_model(self, train_data, epochs=50, batch_size=64, lr=0.001):
        """Train the autoencoder on normal data only"""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.to(device)
        
        dataset = TensorDataset(torch.FloatTensor(train_data))
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        optimizer = optim.Adam(self.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                data = batch[0].to(device)
                optimizer.zero_grad()
                reconstructed = self(data)
                loss = criterion(reconstructed, data)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.6f}")
    
    def detect_anomalies(self, data, threshold_percentile=95):
        """Detect anomalies based on reconstruction error"""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.to(device)
        self.eval()
        
        with torch.no_grad():
            data_tensor = torch.FloatTensor(data).to(device)
            reconstructed = self(data_tensor)
            mse = torch.mean((data_tensor - reconstructed) ** 2, dim=1).cpu().numpy()
        
        # Anomalies have high reconstruction error
        threshold = np.percentile(mse, threshold_percentile)
        predictions = (mse > threshold).astype(int)
        
        return predictions, mse


class SovereignCloudAnomalyDetector:
    """Ensemble detector combining Isolation Forest and Autoencoder"""
    
    def __init__(self):
        self.isolation_forest = IsolationForestDetector()
        self.autoencoder = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, df):
        """Prepare features for both models"""
        features = df[['cpu_usage_percent', 'memory_usage_percent', 
                       'network_egress_mb', 'api_call_frequency']].copy()
        
        # Add derived security-relevant features
        features['cpu_memory_ratio'] = features['cpu_usage_percent'] / (features['memory_usage_percent'] + 1e-5)
        features['egress_per_api_call'] = features['network_egress_mb'] / (features['api_call_frequency'] + 1e-5)
        
        # Add hour of day for temporal anomaly detection
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            features['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            features['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        return features.fillna(0)
    
    def fit(self, df):
        """Train both detectors"""
        print("Training Isolation Forest...")
        self.isolation_forest.fit(df)
        
        print("\nTraining Autoencoder on normal data only...")
        features = self.prepare_features(df)
        scaled_features = self.scaler.fit_transform(features)
        
        # Autoencoder should be trained on NORMAL data only
        if 'is_anomaly' in df.columns:
            normal_data = scaled_features[df['is_anomaly'] == 0]
        else:
            normal_data = scaled_features
        
        self.autoencoder = AutoencoderDetector(input_dim=scaled_features.shape[1])
        self.autoencoder.fit_model(normal_data, epochs=50)
        
        return self
    
    def predict(self, df):
        """Ensemble prediction (weighted voting)"""
        features = self.prepare_features(df)
        scaled_features = self.scaler.transform(features)
        
        # Get predictions from both models
        if_predictions = self.isolation_forest.predict(df)
        
        ae_predictions, ae_scores = self.autoencoder.detect_anomalies(scaled_features)
        
        # Ensemble: anomaly if either model detects it (conservative)
        ensemble_predictions = (if_predictions + ae_predictions) > 0
        ensemble_predictions = ensemble_predictions.astype(int)
        
        return {
            'isolation_forest': if_predictions,
            'autoencoder': ae_predictions,
            'ensemble': ensemble_predictions,
            'autoencoder_scores': ae_scores
        }
    
    def evaluate(self, df, predictions):
        """Calculate accuracy and detailed metrics"""
        if 'is_anomaly' not in df.columns:
            print("No ground truth labels found")
            return None
        
        y_true = df['is_anomaly'].values
        
        print("\n" + "="*60)
        print("MODEL EVALUATION RESULTS")
        print("="*60)
        
        for model_name, y_pred in predictions.items():
            if model_name == 'autoencoder_scores':
                continue
            acc = accuracy_score(y_true, y_pred)
            print(f"\n{model_name.upper()}:")
            print(f"  Accuracy: {acc*100:.2f}%")
            print(f"  Classification Report:")
            print(classification_report(y_true, y_pred, 
                                        target_names=['Normal', 'Anomaly']))
        
        return accuracy_score(y_true, predictions['ensemble'])


if __name__ == "__main__":
    # Test the detector
    from workload_generator import SovereignCloudWorkloadGenerator
    
    print("Generating workload data...")
    generator = SovereignCloudWorkloadGenerator(num_events=10000)
    df = generator.generate_dataset()
    
    print("\nInitializing Anomaly Detector...")
    detector = SovereignCloudAnomalyDetector()
    
    print("\nTraining detector...")
    detector.fit(df)
    
    print("\nMaking predictions...")
    predictions = detector.predict(df)
    
    print("\nEvaluating performance...")
    accuracy = detector.evaluate(df, predictions)