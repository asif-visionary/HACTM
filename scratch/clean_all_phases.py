import os
import re

# Comprehensive replacement mappings
REPLACEMENTS = [
    # Full Phase Headings & Titles
    (r"Research Validation, Reproducibility & Publication Readiness", "Research Validation, Reproducibility & Publication Readiness"),
    (r"Research Validation", "Research Validation"),
    (r"Audited & Verified", "Audited & Verified"),
    (r"Research Pipeline", "Research Pipeline"),
    (r"Research Validation", "Research Validation"),
    (r"Research Validation", "Research Validation"),
    (r"RESEARCH VALIDATION", "RESEARCH VALIDATION"),
    (r"RESEARCH_VALIDATION", "RESEARCH_VALIDATION"),

    (r"Evaluation, Scalability & Research Report Generation", "Evaluation, Scalability & Research Report Generation"),
    (r"Evaluation and Scalability Framework", "Evaluation and Scalability Framework"),
    (r"Evaluation & Reports", "Evaluation & Reports"),
    (r"Evaluation Framework", "Evaluation Framework"),
    (r"Evaluation Framework", "Evaluation Framework"),
    (r"Experimental Results", "Experimental Results"),
    (r"Experimental Suite", "Experimental Suite"),
    (r"Evaluation", "Evaluation"),
    (r"EVALUATION", "EVALUATION"),
    (r"EVALUATION", "EVALUATION"),

    (r"Closed-Loop Cyber Trust Feedback, Continuous Learning & Adaptive Policy Optimization", "Closed-Loop Cyber Trust Feedback, Continuous Learning & Adaptive Policy Optimization"),
    (r"Closed-Loop Feedback & Adaptation", "Closed-Loop Feedback & Adaptation"),
    (r"Closed-Loop Feedback", "Closed-Loop Feedback"),
    (r"Closed-Loop Feedback", "Closed-Loop Feedback"),
    (r"Closed-Loop Adaptation", "Closed-Loop Adaptation"),
    (r"CLOSED-LOOP ADAPTATION", "CLOSED-LOOP ADAPTATION"),
    (r"CLOSED_LOOP_ADAPTATION", "CLOSED_LOOP_ADAPTATION"),
    (r"ClosedLoopAdaptation", "ClosedLoopAdaptation"),
    (r"closed_loop_adaptation", "closed_loop_adaptation"),

    (r"Zero-Trust Policy Decision, Dynamic Micro-Segmentation & Security Context Enforcement", "Zero-Trust Policy Decision, Dynamic Micro-Segmentation & Security Context Enforcement"),
    (r"Zero-Trust & Dynamic Micro-Segmentation", "Zero-Trust & Dynamic Micro-Segmentation"),
    (r"Zero-Trust Engine", "Zero-Trust Engine"),
    (r"Zero-Trust Engine", "Zero-Trust Engine"),
    (r"Zero-Trust Engine", "Zero-Trust Engine"),
    (r"ZERO-TRUST ENGINE", "ZERO-TRUST ENGINE"),
    (r"ZERO_TRUST_ENGINE", "ZERO_TRUST_ENGINE"),

    (r"Adaptive Security-Agent Selection, Latency-Budgeted Orchestration & Information-Gain Optimization", "Adaptive Security-Agent Selection, Latency-Budgeted Orchestration & Information-Gain Optimization"),
    (r"Adaptive Agent Selection & Orchestration", "Adaptive Agent Selection & Orchestration"),
    (r"Regional & Global Orchestration", "Regional & Global Orchestration"),
    (r"Orchestration Engine", "Orchestration Engine"),
    (r"Orchestration", "Orchestration"),
    (r"ORCHESTRATION", "ORCHESTRATION"),
    (r"ORCHESTRATION", "ORCHESTRATION"),

    (r"Multi-Domain Reliability Weighting, Uncertainty Estimation & Dynamic Agent Reputation", "Multi-Domain Reliability Weighting, Uncertainty Estimation & Dynamic Agent Reputation"),
    (r"Reliability & Trust Framework", "Reliability & Trust Framework"),
    (r"Reliability Processing", "Reliability Processing"),
    (r"Reliability & Trust", "Reliability & Trust"),
    (r"RELIABILITY & TRUST", "RELIABILITY & TRUST"),
    (r"RELIABILITY_TRUST", "RELIABILITY_TRUST"),

    (r"Adaptive Evidence Memory, Temporal Evidence Correlation & Attack Evidence Graph", "Adaptive Evidence Memory, Temporal Evidence Correlation & Attack Evidence Graph"),
    (r"Adaptive Memory & Attack Evidence Graph", "Adaptive Memory & Attack Evidence Graph"),
    (r"Adaptive Evidence Memory", "Adaptive Evidence Memory"),
    (r"Adaptive Memory & Graph", "Adaptive Memory & Graph"),
    (r"ADAPTIVE MEMORY & GRAPH", "ADAPTIVE MEMORY & GRAPH"),
    (r"ADAPTIVE_MEMORY", "ADAPTIVE_MEMORY"),
    (r"AdaptiveMemory", "AdaptiveMemory"),
    (r"adaptive_memory", "adaptive_memory"),

    (r"Cross-Domain Evidence Fusion & Unified Cyber Risk Assessment", "Cross-Domain Evidence Fusion & Unified Cyber Risk Assessment"),
    (r"Cross-Domain Evidence Fusion", "Cross-Domain Evidence Fusion"),
    (r"Evidence Fusion Engine", "Evidence Fusion Engine"),
    (r"Evidence Fusion", "Evidence Fusion"),
    (r"EVIDENCE FUSION", "EVIDENCE FUSION"),
    (r"EVIDENCE_FUSION", "EVIDENCE_FUSION"),

    (r"Specialized Security Agents & Multi-Domain Evidence Ingestion", "Specialized Security Agents & Multi-Domain Evidence Ingestion"),
    (r"Multi-Domain Telemetry Platform", "Multi-Domain Telemetry Platform"),
    (r"Specialized Security Agents Multi-Domain Security Evidence Generation \(No Cross-Agent Fusion in Specialized Security Agents\)", "Multi-Domain Security Evidence Generation"),
    (r"Specialized Security Agents", "Specialized Security Agents"),
    (r"SPECIALIZED AGENTS", "SPECIALIZED AGENTS"),
    (r"SPECIALIZED_AGENTS", "SPECIALIZED_AGENTS"),

    (r"Network Security Agent", "Network Security Agent"),
    (r"Network Security Agent", "Network Security Agent"),
    (r"Network Security Agent", "Network Security Agent"),
    (r"NETWORK SECURITY AGENT", "NETWORK SECURITY AGENT"),
    (r"NETWORK_AGENT", "NETWORK_AGENT"),

    (r"Ingestion & Core Data Model", "Ingestion & Core Data Model"),
    (r"Foundation Architecture", "Foundation Architecture"),
    (r"Common Security Evidence Data Model", "Common Security Evidence Data Model"),
    (r"Foundation", "Foundation"),
    (r"FOUNDATION", "FOUNDATION"),
    (r"FOUNDATION", "FOUNDATION"),

    # Generic ranges like Foundation–11, Foundation-10
    (r"Foundation–11", "Unified System Architecture"),
    (r"Foundation-11", "Unified System Architecture"),
    (r"Foundation–10", "Full Cybersecurity Platform"),
    (r"Foundation-10", "Full Cybersecurity Platform"),
    (r"All System Layers", "All System Layers"),
    (r"All System Layers", "All System Layers"),
    (r"Core Infrastructure", "Core Infrastructure"),
    (r"Core Infrastructure", "Core Infrastructure"),

    # Badges in Sidebar
    (r"badge:\s*'Ph\s*[0-9]+'", "badge: undefined"),
]

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content = content
        changes_made = 0
        for pattern, replacement in REPLACEMENTS:
            matches = len(re.findall(pattern, new_content))
            if matches > 0:
                changes_made += matches
                new_content = re.sub(pattern, replacement, new_content)

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return changes_made
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return 0

def main():
    total_files = 0
    total_changes = 0
    for root, dirs, files in os.walk('.'):
        if any(skip in root for skip in ['node_modules', '.venv', '.git', '__pycache__', 'dist', 'build', '.tempmediaStorage']):
            continue
        for file in files:
            if file.endswith(('.ts', '.tsx', '.py', '.md', '.json', '.html', '.css', '.txt')):
                filepath = os.path.join(root, file)
                c = clean_file(filepath)
                if c > 0:
                    total_files += 1
                    total_changes += c
                    print(f"Cleaned {filepath}: {c} replacements")

    print(f"\n==========================================")
    print(f"Cleanup complete! Updated {total_files} files with {total_changes} total replacements.")

if __name__ == '__main__':
    main()
