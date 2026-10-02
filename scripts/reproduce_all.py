#!/usr/bin/env python3
"""
Master Reproduction Script for All HACTM Experiments (EXP-001 through EXP-025).
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "src")))

from reproduce_experiment import reproduce_experiment


def main():
    print("==================================================")
    print("      REPRODUCING ALL HACTM EXPERIMENTS (1-25)    ")
    print("==================================================")
    experiments = [f"EXP-{i:03d}" for i in range(1, 26)]
    for exp_id in experiments:
        print(f"\n---> Starting Reproduction for {exp_id}...")
        reproduce_experiment(exp_id)

    print("\n==================================================")
    print("  ALL 25 EXPERIMENTS SUCCESSFULLY REPRODUCED!    ")
    print("==================================================")


if __name__ == "__main__":
    main()
