"""
Script to generate sample network flow datasets for training, evaluation, and integration testing.
Prevents data leakage by strictly separating train and test distributions with temporal sequence.
"""

import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path


def generate_network_datasets():
    output_dir = Path(__file__).resolve().parent.parent.parent / "data" / "sample"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Training set: 500 benign baseline network flows
    train_path = output_dir / "network_train.csv"
    base_time = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)

    headers = [
        "timestamp", "src_ip", "dst_ip", "src_port", "dst_port", "protocol",
        "duration", "flow_bytes", "flow_packets", "forward_bytes", "backward_bytes",
        "forward_packets", "backward_packets", "tcp_flags", "flow_rate", "packet_rate",
        "label"
    ]

    with open(train_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in range(500):
            ts = (base_time + timedelta(seconds=i * 2)).isoformat()
            src_ip = f"192.168.1.{(i % 30) + 10}"
            dst_ip = "10.0.0.5" if i % 2 == 0 else "10.0.0.8"
            dst_port = 443 if i % 3 != 0 else (80 if i % 2 == 0 else 8080)
            writer.writerow([
                ts, src_ip, dst_ip, 30000 + i, dst_port, "TCP",
                0.12 + (i % 5) * 0.02, 1500 + (i % 800), 12 + (i % 6),
                800 + (i % 400), 700 + (i % 400), 6 + (i % 3), 6 + (i % 3),
                "SYN,ACK", 12500.0, 100.0, "benign"
            ])

    # 2. Test / Ingestion set: 300 flows with 250 benign and 50 attacks
    test_path = output_dir / "network_test.csv"
    test_time = datetime(2026, 2, 2, 9, 0, 0, tzinfo=timezone.utc)

    with open(test_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        # 250 Benign flows
        for i in range(250):
            ts = (test_time + timedelta(seconds=i)).isoformat()
            src_ip = f"192.168.1.{(i % 25) + 10}"
            dst_ip = "10.0.0.5" if i % 2 == 0 else "172.16.1.20"
            dst_port = 443 if i % 4 != 0 else 80
            writer.writerow([
                ts, src_ip, dst_ip, 40000 + i, dst_port, "TCP",
                0.15, 1200, 10, 600, 600, 5, 5, "SYN,ACK", 8000.0, 66.6, "benign"
            ])

        # 15 Telnet / cleartext admin attempts (Signature attack)
        for i in range(15):
            ts = (test_time + timedelta(seconds=260 + i)).isoformat()
            writer.writerow([
                ts, "192.168.1.99", "10.0.0.5", 50000 + i, 23, "TCP",
                0.01, 120, 2, 60, 60, 1, 1, "SYN", 12000.0, 200.0, "attack"
            ])

        # 20 Horizontal Port Scan bursts (Heuristic attack: 1 IP scanning 20 distinct ports within 10s)
        for i in range(20):
            ts = (test_time + timedelta(seconds=280 + (i // 5))).isoformat()
            writer.writerow([
                ts, "192.168.1.188", "10.0.0.50", 45000 + i, 1000 + i, "TCP",
                0.001, 64, 1, 64, 0, 1, 0, "SYN", 64000.0, 1000.0, "attack"
            ])

        # 15 High anomaly / volumetric flood flows (Anomaly detector)
        for i in range(15):
            ts = (test_time + timedelta(seconds=300 + i)).isoformat()
            writer.writerow([
                ts, "192.168.1.250", "10.0.0.5", 60000 + i, 80, "UDP",
                0.002, 500000, 4000, 500000, 0, 4000, 0, None, 250000000.0, 2000000.0, "attack"
            ])

    print(f"Generated {train_path} (500 flows) and {test_path} (300 flows, 50 attacks).")


if __name__ == "__main__":
    generate_network_datasets()
