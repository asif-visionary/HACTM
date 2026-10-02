"""
Master Dataset Processing & Preprocessing Orchestrator.
Executes dataset ingestion pipelines for:
1. Network Datasets (ToN-IoT & BoT-IoT) -> Network Security Agent
2. Phishing Email Dataset -> Phishing Intelligence Agent
3. NIST FRTE/FATE -> Identity & Authentication Agent evaluation adapter
4. MISP Galaxy -> Threat Intelligence Enrichment
5. LLM Agent Failure Benchmark -> Agent Reliability & Adaptive Orchestrator
"""

import json
import logging
from pathlib import Path

from hactm.ingestion.datasets.network_pipeline import NetworkDatasetPipeline
from hactm.ingestion.datasets.phishing_pipeline import PhishingEmailPipeline
from hactm.ingestion.datasets.identity_adapter import IdentityBiometricAdapter
from hactm.ingestion.datasets.misp_galaxy_pipeline import MISPGalaxyPipeline
from hactm.ingestion.datasets.agent_failure_pipeline import AgentFailurePipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("hactm.datasets.process_all")


def process_all_datasets():
    results = {}

    # 1. ToN-IoT & BoT-IoT Network Pipeline
    logger.info("--- Processing Network Security Datasets (ToN-IoT & BoT-IoT) ---")
    net_pipe = NetworkDatasetPipeline()
    try:
        results["ToN-IoT"] = net_pipe.process_ton_iot()
    except Exception as e:
        logger.error(f"ToN-IoT processing failed: {e}")
        results["ToN-IoT"] = {"status": "failed", "error": str(e)}

    try:
        results["BoT-IoT"] = net_pipe.process_bot_iot()
    except Exception as e:
        logger.error(f"BoT-IoT processing failed: {e}")
        results["BoT-IoT"] = {"status": "failed", "error": str(e)}

    # 2. Phishing Emails Pipeline
    logger.info("--- Processing Phishing Email Dataset ---")
    phish_pipe = PhishingEmailPipeline()
    try:
        results["Phishing_Emails"] = phish_pipe.process_phishing_emails()
    except Exception as e:
        logger.error(f"Phishing email processing failed: {e}")
        results["Phishing_Emails"] = {"status": "failed", "error": str(e)}

    # 3. NIST FRTE/FATE Identity Adapter
    logger.info("--- Processing NIST FRTE/FATE Identity Benchmarks ---")
    identity_adapter = IdentityBiometricAdapter()
    try:
        results["NIST_FRTE_FATE"] = identity_adapter.load_nist_benchmarks()
    except Exception as e:
        logger.error(f"NIST identity processing failed: {e}")
        results["NIST_FRTE_FATE"] = {"status": "failed", "error": str(e)}

    # 4. MISP Galaxy Pipeline
    logger.info("--- Processing MISP Galaxy Threat Intelligence ---")
    misp_pipe = MISPGalaxyPipeline()
    try:
        results["MISP_Galaxy"] = misp_pipe.process_clusters()
    except Exception as e:
        logger.error(f"MISP Galaxy processing failed: {e}")
        results["MISP_Galaxy"] = {"status": "failed", "error": str(e)}

    # 5. LLM Agent Failure Benchmark
    logger.info("--- Processing LLM Agent Failure Benchmark ---")
    agent_pipe = AgentFailurePipeline()
    try:
        results["LLM_Agent_Failure"] = agent_pipe.process_agent_failures()
    except Exception as e:
        logger.error(f"Agent failure processing failed: {e}")
        results["LLM_Agent_Failure"] = {"status": "failed", "error": str(e)}

    print("\n=== Dataset Processing Complete ===")
    print(json.dumps(results, indent=2, default=str))
    return results

if __name__ == "__main__":
    process_all_datasets()
