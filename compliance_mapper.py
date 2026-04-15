import pandas as pd
import numpy as np

class SovereignComplianceMapper:
    """
    Maps detection results to sovereign cloud compliance requirements
    for India's regulated sectors (BFSI, Government)
    """
    
    def __init__(self):
        self.allowed_regions = ['ap-south-1', 'ap-south-2']  # India sovereign regions
        self.compliance_framework = {
            'data_residency': {
                'requirement': 'All data must remain within Indian sovereign boundaries',
                'violation_if': 'region not in allowed_regions',
                'severity': 'CRITICAL'
            },
            'geo_fencing': {
                'requirement': 'Access only from approved Indian IP ranges',
                'violation_if': 'region outside ap-south-*',
                'severity': 'HIGH'
            },
            'rbac_enforcement': {
                'requirement': 'Role-based access control for confidential data',
                'violation_if': "user_role == 'viewer' and data_classification in ['confidential', 'restricted']",
                'severity': 'HIGH'
            },
            'data_exfiltration_prevention': {
                'requirement': 'Monitor and block unusual data egress patterns',
                'violation_if': 'network_egress_mb > 500',
                'severity': 'CRITICAL'
            },
            'audit_trail': {
                'requirement': 'All access to restricted data must be logged',
                'violation_if': "data_classification == 'restricted'",
                'severity': 'MEDIUM'
            }
        }
    
    def check_compliance_violations(self, df, anomaly_predictions):
        """
        Identify specific compliance violations based on detection results
        """
        violations = []
        
        for idx, row in df.iterrows():
            row_violations = []
            
            # Check data residency
            if row['region'] not in self.allowed_regions:
                row_violations.append({
                    'type': 'DATA_RESIDENCY_VIOLATION',
                    'requirement': self.compliance_framework['data_residency']['requirement'],
                    'severity': 'CRITICAL',
                    'details': f"Access from non-sovereign region: {row['region']}"
                })
            
            # Check geo-fencing
            if not row['region'].startswith('ap-south'):
                row_violations.append({
                    'type': 'GEO_FENCING_VIOLATION',
                    'requirement': self.compliance_framework['geo_fencing']['requirement'],
                    'severity': 'HIGH',
                    'details': f"Region {row['region']} outside approved sovereign boundary"
                })
            
            # Check RBAC
            if row['user_role'] == 'viewer' and row['data_classification'] in ['confidential', 'restricted']:
                row_violations.append({
                    'type': 'RBAC_VIOLATION',
                    'requirement': self.compliance_framework['rbac_enforcement']['requirement'],
                    'severity': 'HIGH',
                    'details': f"User role '{row['user_role']}' accessing {row['data_classification']} data"
                })
            
            # Check data exfiltration
            if row['network_egress_mb'] > 500:
                row_violations.append({
                    'type': 'DATA_EXFILTRATION_ALERT',
                    'requirement': self.compliance_framework['data_exfiltration_prevention']['requirement'],
                    'severity': 'CRITICAL',
                    'details': f"High egress detected: {row['network_egress_mb']:.2f} MB"
                })
            
            # Check if anomaly detected by ML
            if anomaly_predictions[idx] == 1:
                row_violations.append({
                    'type': 'ML_ANOMALY_DETECTED',
                    'requirement': 'Continuous monitoring for anomalous patterns',
                    'severity': 'HIGH',
                    'details': f"ML model flagged as anomaly (Type: {row.get('anomaly_type', 'unknown')})"
                })
            
            if row_violations:
                violations.append({
                    'timestamp': row['timestamp'],
                    'workload_id': row['workload_id'],
                    'violations': row_violations,
                    'max_severity': max([v['severity'] for v in row_violations])
                })
        
        return violations
    
    def generate_compliance_report(self, violations):
        """Generate a structured compliance report for auditors"""
        report = {
            'total_violations': len(violations),
            'by_severity': {
                'CRITICAL': len([v for v in violations if v['max_severity'] == 'CRITICAL']),
                'HIGH': len([v for v in violations if v['max_severity'] == 'HIGH']),
                'MEDIUM': len([v for v in violations if v['max_severity'] == 'MEDIUM'])
            },
            'by_type': {},
            'affected_workloads': set(),
            'detailed_violations': violations[:50]  # Top 50 for report
        }
        
        # Count by violation type
        for v in violations:
            for violation in v['violations']:
                v_type = violation['type']
                report['by_type'][v_type] = report['by_type'].get(v_type, 0) + 1
            report['affected_workloads'].add(v['workload_id'])
        
        report['affected_workloads'] = list(report['affected_workloads'])
        
        return report
    
    def print_compliance_summary(self, report):
        """Print human-readable compliance summary"""
        print("\n" + "="*60)
        print("SOVEREIGN CLOUD COMPLIANCE REPORT")
        print("="*60)
        print(f"Total Compliance Violations: {report['total_violations']}")
        print(f"Affected Workloads: {len(report['affected_workloads'])}")
        
        print("\nViolations by Severity:")
        for severity, count in report['by_severity'].items():
            print(f"  {severity}: {count}")
        
        print("\nViolations by Type:")
        for v_type, count in report['by_type'].items():
            print(f"  {v_type}: {count}")
        
        print("\nSample Critical Violations:")
        critical_violations = [v for v in report['detailed_violations'] if v['max_severity'] == 'CRITICAL'][:5]
        for v in critical_violations:
            print(f"\n  [{v['timestamp']}] Workload: {v['workload_id']}")
            for violation in v['violations']:
                if violation['severity'] == 'CRITICAL':
                    print(f"    ⚠️ {violation['type']}: {violation['details']}")


if __name__ == "__main__":
    from workload_generator import SovereignCloudWorkloadGenerator
    from anomaly_detector import SovereignCloudAnomalyDetector
    
    # Generate data
    generator = SovereignCloudWorkloadGenerator(num_events=10000)
    df = generator.generate_dataset()
    
    # Detect anomalies
    detector = SovereignCloudAnomalyDetector()
    detector.fit(df)
    predictions = detector.predict(df)
    
    # Check compliance
    compliance_mapper = SovereignComplianceMapper()
    violations = compliance_mapper.check_compliance_violations(df, predictions['ensemble'])
    report = compliance_mapper.generate_compliance_report(violations)
    compliance_mapper.print_compliance_summary(report)