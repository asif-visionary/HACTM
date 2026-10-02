"""
HACTM CLI Entrypoint.
Provides command-line utilities for running the API server, database migration, and batch ingestion.
"""

import argparse
import sys
import uvicorn
from pathlib import Path

from hactm.core.constants import IngestionPolicy
from hactm.core.logging import logger
from hactm.storage.database import SessionLocal, init_db
from hactm.ingestion.pipeline import IngestionPipeline


import json
from hactm.storage.repositories.network_repo import NetworkRepository
from hactm.services.network_service import NetworkService
from hactm.network.benchmark import run_network_benchmark


def run_serve(args):
    """Starts the FastAPI development/production server."""
    logger.info(f"Starting HACTM server on {args.host}:{args.port}...")
    uvicorn.run("hactm.api.app:app", host=args.host, port=args.port, reload=args.reload)


def run_init_db(args):
    """Initializes database tables."""
    logger.info("Initializing HACTM SQLite/PostgreSQL database...")
    init_db()
    logger.info("Database initialized successfully.")


def run_ingest(args):
    """Executes dataset file ingestion."""
    init_db()
    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        policy = IngestionPolicy(args.policy.upper())
        logger.info(f"Ingesting {args.file} with policy={policy.value}, batch_size={args.batch_size}...")
        result = pipeline.ingest_file(
            file_path=args.file,
            policy=policy,
            batch_size=args.batch_size,
            dataset_name=args.dataset
        )
        print(f"\nIngestion Summary for {args.file}:")
        print(f"  Run ID:       {result.run_id}")
        print(f"  Total Rows:   {result.total}")
        print(f"  Inserted:     {result.inserted}")
        print(f"  Duplicates:   {result.duplicates}")
        print(f"  Invalid:      {result.invalid}")
        print(f"  Quarantined:  {result.quarantined}")
        print(f"  Failed:       {result.failed}\n")
    finally:
        db.close()


# Network CLI Handlers
def run_network_ingest(args):
    """Ingests and analyzes network telemetry file."""
    init_db()
    db = SessionLocal()
    try:
        service = NetworkService(db)
        print(f"Ingesting network data: {args.file} (dataset: {args.dataset or 'canonical'})...")
        res = service.ingest_network_file(
            file_path=args.file,
            dataset_name=args.dataset,
            batch_size=args.batch_size,
            run_detection=True
        )
        print("\n--- Network Ingestion & Detection Summary ---")
        print(f"  Dataset:               {res['dataset_name']}")
        print(f"  Events Processed:      {res['events_processed']}")
        print(f"  Detections Generated:  {res['detections_generated']}")
        print(f"  Security Evidence:     {res['security_evidence_created']}\n")
        sys.exit(0)
    finally:
        db.close()


def run_network_train(args):
    """Trains an unsupervised network anomaly model."""
    init_db()
    db = SessionLocal()
    try:
        service = NetworkService(db)
        print(f"Training network anomaly model on {args.training_file} (contamination={args.contamination})...")
        meta = service.train_anomaly_model(
            file_path=args.training_file,
            dataset_name=args.dataset,
            contamination=args.contamination
        )
        print("\n--- Model Training Summary ---")
        print(f"  Model ID:     {meta.model_id}")
        print(f"  Version:      {meta.model_version}")
        print(f"  Algorithm:    {meta.algorithm}")
        print(f"  Samples:      {meta.training_samples}")
        print(f"  Features:     {len(meta.features)}")
        print(f"  Status:       {meta.status}")
        print(f"  Artifact:     {meta.artifact_path}\n")
        if args.activate:
            service.activate_model(meta.model_id)
            print(f"  Active:       Activated {meta.model_id} for inference.\n")
        sys.exit(0)
    finally:
        db.close()


def run_network_evaluate(args):
    """Evaluates network security detection performance against ground truth."""
    init_db()
    db = SessionLocal()
    try:
        service = NetworkService(db)
        print(f"Evaluating network agent on {args.test_file} against ground truth...")
        metrics = service.evaluate(
            file_path=args.test_file,
            dataset_name=args.dataset
        )
        print("\n--- Network Detection Evaluation Results ---")
        print(f"  Samples:      {metrics.total_evaluated}")
        print(f"  Class Dist:   {metrics.class_distribution}")
        print(f"  Precision:    {metrics.precision:.4f}")
        print(f"  Recall:       {metrics.recall:.4f}")
        print(f"  F1 Score:     {metrics.f1_score:.4f}")
        print(f"  FPR:          {metrics.false_positive_rate:.4f}")
        print(f"  FNR:          {metrics.false_negative_rate:.4f}")
        if metrics.roc_auc is not None:
            print(f"  ROC-AUC:      {metrics.roc_auc:.4f}")
        if metrics.pr_auc is not None:
            print(f"  PR-AUC:       {metrics.pr_auc:.4f}")
        print(f"  Confusion:    TP={metrics.true_positives}, FP={metrics.false_positives}, TN={metrics.true_negatives}, FN={metrics.false_negatives}\n")
        sys.exit(0)
    finally:
        db.close()


def run_network_detect(args):
    """Runs network detection on single event or file."""
    init_db()
    db = SessionLocal()
    try:
        service = NetworkService(db)
        if args.file:
            res = service.ingest_network_file(file_path=args.file, dataset_name=args.dataset)
            print(f"Detection completed for {args.file}: {res['detections_generated']} detections generated across {res['events_processed']} flows.")
        else:
            print("Please specify --file for detection.")
            sys.exit(1)
    finally:
        db.close()


def run_network_benchmark_cmd(args):
    """Runs performance benchmark suite across specified scales."""
    scales = [int(s) for s in args.scales.split(",")]
    print(f"Starting Network Security Agent benchmark for scales: {scales}...")
    results = run_network_benchmark(scales=scales)
    print("\n--- Network Security Agent Benchmark Results ---")
    print(f"{'Scale':<10} | {'Throughput (evt/s)':<20} | {'Mean Lat (ms)':<15} | {'P95 (ms)':<10} | {'P99 (ms)':<10} | {'RAM (MB)':<10}")
    print("-" * 85)
    for r in results:
        print(f"{r['scale']:<10} | {r['throughput_events_per_sec']:<20} | {r['mean_latency_ms']:<15} | {r['p95_latency_ms']:<10} | {r['p99_latency_ms']:<10} | {r['memory_final_mb']:<10}")
    print("-" * 85 + "\n")
    sys.exit(0)


def run_network_health(args):
    """Outputs live health metrics of Network Security Agent."""
    init_db()
    db = SessionLocal()
    try:
        service = NetworkService(db)
        h = service.get_agent_health()
        print("\n--- Network Security Agent Health ---")
        print(f"  Status:             {h['status']}")
        print(f"  Events Processed:   {h['events_processed']}")
        print(f"  Detections Made:    {h['detections_generated']}")
        print(f"  Errors:             {h.get('errors_count', 0)}")
        print(f"  Processing Rate:    {h.get('processing_rate_events_per_sec', 0.0):.2f} evt/s")
        print(f"  Average Latency:    {h.get('average_latency_ms', 0.0):.4f} ms")
        print(f"  Detectors Active:   {', '.join(h.get('active_detectors', []))}\n")
        sys.exit(0)
    finally:
from hactm.services.phishing_service import PhishingService
from hactm.services.uba_service import UbaService
from hactm.services.identity_service import IdentityService
from hactm.services.transaction_service import TransactionService


# Specialized Security Agents Generic Agents Health
def run_agents_health(args):
    init_db()
    db = SessionLocal()
    try:
        services = {
            "Network Security Agent": NetworkService(db).agent,
            "Phishing Intelligence Agent": PhishingService(db).agent,
            "User Behavior Analytics Agent": UbaService(db).agent,
            "Identity & Authentication Agent": IdentityService(db).agent,
            "Transaction Security Agent": TransactionService(db).agent,
        }
        print("\n--- HACTM Multi-Domain Specialized Security Agents Health ---")
        for name, ag in services.items():
            h = ag.health()
            print(f"  [{h['agent_id']}] {name}:")
            print(f"    Status:         {h['status']}")
            print(f"    Processed:      {h['events_processed']}")
            print(f"    Detections:     {h['detections_generated']}")
            print(f"    Avg Latency:    {h.get('average_latency_ms', 0.0):.3f} ms\n")
        sys.exit(0)
    finally:
        db.close()


# Phishing Handlers
def run_phishing_cmd(args):
    init_db()
    db = SessionLocal()
    try:
        svc = PhishingService(db)
        if args.phish_sub == "ingest" or args.phish_sub == "detect":
            print("Ingesting phishing emails...")
            data = svc.evaluate().model_dump()
            print(f"Phishing detection execution completed. Evaluated {data['total_evaluated']} samples.")
        elif args.phish_sub == "evaluate":
            m = svc.evaluate()
            print("\n--- Phishing Agent Evaluation Results ---")
            print(f"  Precision: {m.precision:.4f} | Recall: {m.recall:.4f} | F1: {m.f1_score:.4f}")
            print(f"  FPR: {m.false_positive_rate:.4f} | FNR: {m.false_negative_rate:.4f}")
        elif args.phish_sub == "train":
            from hactm.phishing.loader import generate_synthetic_phishing_dataset
            dataset = generate_synthetic_phishing_dataset(count=100)
            res = svc.train_nlp_model(dataset)
            print(f"Trained NLP phishing classifier: {res}")
        sys.exit(0)
    finally:
        db.close()


# UBA Handlers
def run_uba_cmd(args):
    init_db()
    db = SessionLocal()
    try:
        svc = UbaService(db)
        if args.uba_sub in {"ingest", "detect"}:
            print("Processing UBA events...")
            m = svc.evaluate()
            print(f"UBA detection completed for {m.total_evaluated} activity events.")
        elif args.uba_sub == "evaluate":
            m = svc.evaluate()
            print("\n--- UBA Agent Evaluation Results ---")
            print(f"  Precision: {m.precision:.4f} | Recall: {m.recall:.4f} | F1: {m.f1_score:.4f}")
            print(f"  False Alerts/User: {m.false_alerts_per_user:.2f} | Insufficient Baseline: {m.pct_users_insufficient_baseline:.1f}%")
        elif args.uba_sub == "train":
            from hactm.uba.loader import generate_synthetic_uba_dataset
            dataset = generate_synthetic_uba_dataset(count=100)
            res = svc.train_baseline(dataset)
            print(f"Trained UBA profile baseline: {res}")
        sys.exit(0)
    finally:
        db.close()


# Identity Handlers
def run_identity_cmd(args):
    init_db()
    db = SessionLocal()
    try:
        svc = IdentityService(db)
        if args.id_sub in {"ingest", "detect"}:
            print("Processing Identity & Authentication events...")
            m = svc.evaluate()
            print(f"Identity detection completed for {m.total_evaluated} authentication events.")
        elif args.id_sub == "evaluate":
            m = svc.evaluate()
            print("\n--- Identity Agent Evaluation Results ---")
            print(f"  Precision: {m.precision:.4f} | Recall: {m.recall:.4f} | F1: {m.f1_score:.4f}")
            print(f"  False Alerts/Auth Event: {m.false_alerts_per_auth_event:.4f}")
        sys.exit(0)
    finally:
        db.close()


# Transaction Handlers
def run_transaction_cmd(args):
    init_db()
    db = SessionLocal()
    try:
        svc = TransactionService(db)
        if args.tx_sub in {"ingest", "detect"}:
            print("Processing financial transaction events...")
            m = svc.evaluate()
            print(f"Transaction detection completed for {m.total_evaluated} transactions.")
        elif args.tx_sub == "evaluate":
            m = svc.evaluate()
            print("\n--- Transaction Agent Evaluation Results ---")
            print(f"  Precision: {m.precision:.4f} | Recall: {m.recall:.4f} | F1: {m.f1_score:.4f}")
            print(f"  False Alerts/1K Tx: {m.false_alerts_per_1000_transactions:.2f}")
        elif args.tx_sub == "train":
            from hactm.transaction.loader import generate_synthetic_transaction_dataset
            dataset = generate_synthetic_transaction_dataset(count=100)
            res = svc.train_baseline(dataset)
            print(f"Trained Transaction account baselines: {res}")
        sys.exit(0)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="HACTM - Hierarchical Adaptive Cyber Trust Mesh CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Server command
    server_parser = subparsers.add_parser("serve", help="Run the HACTM REST API server")
    server_parser.add_argument("--host", default="127.0.0.1", help="Host address")
    server_parser.add_argument("--port", type=int, default=8080, help="Port number")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    server_parser.set_defaults(func=run_serve)

    # Init DB command
    init_parser = subparsers.add_parser("init-db", help="Initialize database schema and tables")
    init_parser.set_defaults(func=run_init_db)

    # Ingestion command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a dataset file (.csv, .json, .jsonl)")
    ingest_parser.add_argument("file", help="Path to dataset file")
    ingest_parser.add_argument("--policy", default="QUARANTINE_INVALID", choices=["STRICT", "SKIP_INVALID", "QUARANTINE_INVALID"])
    ingest_parser.add_argument("--batch-size", type=int, default=1000, help="Batch record size")
    ingest_parser.add_argument("--dataset", help="Optional dataset name override")
    ingest_parser.set_defaults(func=run_ingest)

    # Network Agent command suite
    net_parser = subparsers.add_parser("network", help="Network Security Agent operations")
    net_subparsers = net_parser.add_subparsers(dest="subcommand", required=True)

    net_ingest = net_subparsers.add_parser("ingest", help="Ingest and detect network flow telemetry")
    net_ingest.add_argument("file", help="Path to network data file (.csv, .json, .jsonl)")
    net_ingest.add_argument("--dataset", help="Dataset schema identifier (cic_ids2017, unsw_nb15, etc.)")
    net_ingest.add_argument("--policy", default="quarantine", choices=["strict", "skip", "quarantine"])
    net_ingest.add_argument("--batch-size", type=int, default=1000)
    net_ingest.set_defaults(func=run_network_ingest)

def run_fusion_cmd(args):
    """Executes Evidence Fusion Evidence Fusion CLI commands."""
    sub = getattr(args, "fusion_sub", "")
    db = next(get_db())
    service = FusionService(db)

    if sub == "run":
        entity_id = getattr(args, "entity", "USER-103")
        window = getattr(args, "window", 1800.0)
        res = service.run_fusion_for_entity(entity_id=entity_id, window_seconds=window)
        print(json.dumps(res, indent=2))
    elif sub == "evaluate":
        res = service.evaluate_fusion()
        print(json.dumps(res, indent=2))
    elif sub == "conflicts":
        res = service.get_conflicts()
        print(json.dumps(res, indent=2))
    elif sub == "coverage":
        res = service.get_metrics()
        print(json.dumps(res, indent=2))
    else:
        print(f"Unknown fusion subcommand: {sub}")


def main():
    parser = argparse.ArgumentParser(
        prog="hactm",
        description="HACTM - Hierarchical Adaptive Cyber Trust Mesh CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ingestion command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest raw security dataset into Foundation evidence store")
    ingest_parser.add_argument("file_path", help="Path to input data file (CSV, JSON)")
    ingest_parser.add_argument("--source", required=True, help="Canonical source identifier (e.g. cic_ids_2017)")
    ingest_parser.add_argument("--policy", default="quarantine", choices=["strict", "quarantine", "lenient"])
    ingest_parser.add_argument("--dataset", help="Optional dataset format mapping override")
    ingest_parser.add_argument("--batch-size", type=int, default=1000)
    ingest_parser.set_defaults(func=run_ingest)

    # Evidence query command
    evidence_parser = subparsers.add_parser("evidence", help="Query and inspect SecurityEvidence lineage")
    evidence_parser.add_argument("--entity-id", help="Filter by entity ID")
    evidence_parser.add_argument("--event-type", help="Filter by event type")
    evidence_parser.add_argument("--min-risk", type=float, help="Filter by minimum risk score")
    evidence_parser.add_argument("--agent-id", help="Filter by producing agent ID")
    evidence_parser.add_argument("--limit", type=int, default=20)
    evidence_parser.set_defaults(func=run_evidence_query)

    # Entity query command
    entity_parser = subparsers.add_parser("entity", help="Inspect entity resolution and state")
    entity_parser.add_argument("entity_id", help="Entity identifier to inspect")
    entity_parser.set_defaults(func=run_entity_inspect)

    # Network Security Agent command suite
    net_parser = subparsers.add_parser("network", help="Network Security Agent operations")
    net_subparsers = net_parser.add_subparsers(dest="net_sub", required=True)

    net_train = net_subparsers.add_parser("train", help="Train network anomaly detection model")
    net_train.add_argument("training_file", help="Path to benign/baseline training data file")
    net_train.add_argument("--dataset", help="Dataset format mapping")
    net_train.add_argument("--contamination", type=float, default=0.01)
    net_train.add_argument("--model-id", default="net_iso_forest_v1")
    net_train.add_argument("--activate", action="store_true", help="Immediately activate candidate model")
    net_train.set_defaults(func=run_network_train)

    net_eval = net_subparsers.add_parser("evaluate", help="Evaluate network detection against labeled dataset")
    net_eval.add_argument("test_file", help="Path to labeled test data file")
    net_eval.add_argument("--label-col", default="label", help="Ground truth column name")
    net_eval.add_argument("--attack-label", default="attack", help="Label value indicating attack")
    net_eval.add_argument("--dataset", help="Dataset format mapping")
    net_eval.add_argument("--model-id", help="Optional specific model ID to test")
    net_eval.set_defaults(func=run_network_evaluate)

    net_detect = net_subparsers.add_parser("detect", help="Run detection on network events")
    net_detect.add_argument("--file", help="Path to file for batch detection")
    net_detect.add_argument("--dataset", help="Dataset format mapping")
    net_detect.set_defaults(func=run_network_detect)

    net_bm = net_subparsers.add_parser("benchmark", help="Benchmark network agent throughput and latency")
    net_bm.add_argument("--scales", default="1000,10000", help="Comma-separated event counts (e.g. 1000,10000)")
    net_bm.set_defaults(func=run_network_benchmark_cmd)

    net_health = net_subparsers.add_parser("health", help="Check Network Security Agent live health")
    net_health.set_defaults(func=run_network_health)

    # Phishing Agent command suite
    phish_parser = subparsers.add_parser("phishing", help="Phishing Intelligence Agent operations")
    phish_sub = phish_parser.add_subparsers(dest="phish_sub", required=True)
    for cmd in ["ingest", "train", "evaluate", "detect"]:
        p = phish_sub.add_parser(cmd)
        p.set_defaults(func=run_phishing_cmd)

    # UBA Agent command suite
    uba_parser = subparsers.add_parser("uba", help="User Behavior Analytics Agent operations")
    uba_sub = uba_parser.add_subparsers(dest="uba_sub", required=True)
    for cmd in ["ingest", "train", "evaluate", "detect"]:
        u = uba_sub.add_parser(cmd)
        u.set_defaults(func=run_uba_cmd)

    # Identity Agent command suite
    id_parser = subparsers.add_parser("identity", help="Identity & Authentication Agent operations")
    id_sub = id_parser.add_subparsers(dest="id_sub", required=True)
    for cmd in ["ingest", "evaluate", "detect"]:
        i = id_sub.add_parser(cmd)
        i.set_defaults(func=run_identity_cmd)

    # Transaction Agent command suite
    tx_parser = subparsers.add_parser("transaction", help="Transaction Security Agent operations")
    tx_sub = tx_parser.add_subparsers(dest="tx_sub", required=True)
    for cmd in ["ingest", "train", "evaluate", "detect"]:
        t = tx_sub.add_parser(cmd)
        t.set_defaults(func=run_transaction_cmd)

    # Evidence Fusion Fusion command suite
    fusion_parser = subparsers.add_parser("fusion", help="Evidence Fusion Cross-Domain Evidence Fusion operations")
    fusion_sub = fusion_parser.add_subparsers(dest="fusion_sub", required=True)
    f_run = fusion_sub.add_parser("run", help="Run cross-domain evidence fusion for an entity")
    f_run.add_argument("--entity", default="USER-103", help="Target entity ID to evaluate fusion for")
    f_run.add_argument("--window", type=float, default=1800.0, help="Correlation window in seconds")
    f_run.set_defaults(func=run_fusion_cmd)

    f_eval = fusion_sub.add_parser("evaluate", help="Run Evidence Fusion fusion evaluation & ablation suite")
    f_eval.set_defaults(func=run_fusion_cmd)

    f_conf = fusion_sub.add_parser("conflicts", help="List detected evidence conflicts")
    f_conf.set_defaults(func=run_fusion_cmd)

    f_cov = fusion_sub.add_parser("coverage", help="Output evidence domain coverage metrics")
    f_cov.set_defaults(func=run_fusion_cmd)

    # Common Agents Health
    agents_parser = subparsers.add_parser("agents", help="Multi-domain agent management and health")
    agents_sub = agents_parser.add_subparsers(dest="agents_sub", required=True)
    agents_h = agents_sub.add_parser("health", help="Outputs health of all specialized security agents")
    agents_h.set_defaults(func=run_agents_health)

    # Adaptive Memory & Graph Adaptive Memory command suite
    mem_parser = subparsers.add_parser("memory", help="Adaptive Evidence Memory operations")
    mem_sub = mem_parser.add_subparsers(dest="mem_sub", required=True)
    m_h = mem_sub.add_parser("health", help="Check adaptive memory tier utilization and health")
    m_h.set_defaults(func=run_memory_cmd)
    m_r = mem_sub.add_parser("retrieve", help="Retrieve historical memory entries")
    m_r.add_argument("--entity", help="Target entity ID filter")
    m_r.add_argument("--domain", help="Target domain filter")
    m_r.set_defaults(func=run_memory_cmd)
    m_c = mem_sub.add_parser("compact", help="Run memory compaction and lifecycle tier expiration")
    m_c.set_defaults(func=run_memory_cmd)
    m_b = mem_sub.add_parser("benchmark", help="Benchmark memory storage and retrieval latency")
    m_b.set_defaults(func=run_memory_cmd)

    # Adaptive Memory & Graph Attack Evidence Graph command suite
    graph_parser = subparsers.add_parser("graph", help="Attack Evidence Graph operations")
    graph_sub = graph_parser.add_subparsers(dest="graph_sub", required=True)
    g_b = graph_sub.add_parser("build", help="Build attack graph from stored evidence")
    g_b.set_defaults(func=run_graph_cmd)
    g_i = graph_sub.add_parser("inspect", help="Inspect graph node details")
    g_i.add_argument("node_id", help="Node ID to inspect")
    g_i.set_defaults(func=run_graph_cmd)
    g_s = graph_sub.add_parser("subgraph", help="Extract bounded k-hop subgraph")
    g_s.add_argument("node_id", help="Center node ID")
    g_s.add_argument("--k-hop", type=int, default=2, help="Graph traversal depth (1-4)")
    g_s.set_defaults(func=run_graph_cmd)
    g_c = graph_sub.add_parser("attack-chains", help="Detect candidate multi-stage attack chains")
    g_c.add_argument("--entity", help="Target entity ID filter")
    g_c.set_defaults(func=run_graph_cmd)

    # Adaptive Memory & Graph Temporal Analysis
    temp_parser = subparsers.add_parser("temporal", help="Temporal evidence correlation analysis")
    temp_sub = temp_parser.add_subparsers(dest="temp_sub", required=True)
    t_a = temp_sub.add_parser("analyze", help="Analyze entity temporal timeline and sequence order")
    t_a.add_argument("--entity", default="USER-103", help="Target entity ID")
    t_a.set_defaults(func=run_temporal_cmd)

    # Adaptive Memory & Graph Full Research Evaluation
    p5_parser = subparsers.add_parser("adaptive_memory", help="Adaptive Memory & Graph Memory, Temporal, and Graph research evaluation")
    p5_sub = p5_parser.add_subparsers(dest="p5_sub", required=True)
    p5_e = p5_sub.add_parser("evaluate", help="Run baseline comparison (Session-local, Fixed, Time, Adaptive) and ablation suite")
    p5_e.set_defaults(func=run_adaptive_memory_eval_cmd)

    args = parser.parse_args()
    args.func(args)


def run_memory_cmd(args):
    """Executes memory CLI subcommands."""
    init_db()
    db = SessionLocal()
    try:
        from hactm.services.adaptive_memory_service import AdaptiveMemoryService
        from hactm.memory.models import MemoryRetrievalQuery
        svc = AdaptiveMemoryService(db)

        if args.mem_sub == "health":
            h = svc.memory.health()
            print("\n--- Adaptive Evidence Memory Health ---")
            print(f"  Status:             {h['status']}")
            print(f"  Total Entries:      {h['total_entries']}")
            print(f"  HOT Entries:        {h['hot_entries']} ({h['hot_utilization_pct']}%)")
            print(f"  WARM Entries:       {h['warm_entries']} ({h['warm_utilization_pct']}%)")
            print(f"  COLD Entries:       {h['cold_entries']}\n")
        elif args.mem_sub == "retrieve":
            entries = svc.memory.retrieve(MemoryRetrievalQuery(entity_id=getattr(args, 'entity', None), domain=getattr(args, 'domain', None)))
            print(f"\nRetrieved {len(entries)} memory entries:")
            for e in entries[:10]:
                print(f"  [{e.memory_tier.value}] {e.memory_id} - Entity: {e.entity_ids}, Domain: {e.domain}, Risk: {e.risk_score}, Imp: {e.importance_score}")
        elif args.mem_sub == "compact":
            res = svc.memory.compact()
            print(f"\nMemory Compaction Result: {res}\n")
        elif args.mem_sub == "benchmark":
            from hactm.eval.adaptive_memory_eval import AdaptiveMemoryEvaluator
            ev = AdaptiveMemoryEvaluator(db)
            res = ev.run_baseline_comparison()
            print(json.dumps(res, indent=2))
    finally:
        db.close()


def run_graph_cmd(args):
    """Executes graph CLI subcommands."""
    init_db()
    db = SessionLocal()
    try:
        from hactm.services.adaptive_memory_service import AdaptiveMemoryService
        svc = AdaptiveMemoryService(db)

        if args.graph_sub == "build":
            print("Constructing Attack Evidence Graph from historical evidence...")
            entries = svc.memory.retrieve(MemoryRetrievalQuery(max_results=100))
            for e in entries:
                svc.graph_builder.add_evidence(e.dict())
            print("Graph build complete.")
        elif args.graph_sub == "inspect":
            node = svc.graph_builder.repo.get_node(args.node_id)
            if node:
                print(f"\nGraph Node [{node.node_id}]:")
                print(f"  Type: {node.node_type}, Canonical ID: {node.canonical_id}, Display: {node.display_name}")
            else:
                print(f"Node '{args.node_id}' not found.")
        elif args.graph_sub == "subgraph":
            sub = svc.graph_builder.get_subgraph(args.node_id, k_hop=args.k_hop)
            print(f"\nSubgraph centered at '{args.node_id}' (k={args.k_hop}):")
            print(f"  Nodes ({sub.total_nodes}): {[n.node_id for n in sub.nodes]}")
            print(f"  Edges ({sub.total_edges}): {[e.edge_id for e in sub.edges]}\n")
        elif args.graph_sub == "attack-chains":
            cands = svc.pattern_matcher.evaluate_evidence_sequence([], primary_entity_id=getattr(args, 'entity', 'USER-103'))
            print(f"\nCandidate Attack Chains ({len(cands)}):")
            for c in cands:
                print(f"  Chain ID: {c.chain_id}, Pattern: {c.pattern_id}, Completeness: {c.completeness*100}%, Conf: {c.confidence}")
    finally:
        db.close()


def run_temporal_cmd(args):
    """Executes temporal analysis CLI subcommands."""
    init_db()
    db = SessionLocal()
    try:
        from hactm.services.adaptive_memory_service import AdaptiveMemoryService
        svc = AdaptiveMemoryService(db)
        ctx = svc.get_entity_context(args.entity)
        print(f"\n--- Temporal Timeline & Context for {args.entity} ---")
        print(f"  Memory Coverage:        {ctx['memory']['coverage']}")
        print(f"  Historical Events:      {ctx['memory']['entry_count']}")
        print(f"  Attack Chain Candidates: {len(ctx['attack_chain_candidates'])}\n")
    finally:
        db.close()


def run_adaptive_memory_eval_cmd(args):
    """Runs Adaptive Memory & Graph research baseline comparison and ablation evaluation."""
    init_db()
    db = SessionLocal()
    try:
        from hactm.eval.adaptive_memory_eval import AdaptiveMemoryEvaluator
        evaluator = AdaptiveMemoryEvaluator(db)
        print("\n============================================================")
        print("ADAPTIVE MEMORY & GRAPH RESEARCH BENCHMARK: ADAPTIVE MEMORY & GRAPH REASONING")
        print("============================================================")
        print("\n[1/2] Evaluating Baselines (No Memory vs Fixed vs Time vs Adaptive)...")
        baselines = evaluator.run_baseline_comparison()
        print(json.dumps(baselines, indent=2))

        print("\n[2/2] Evaluating Ablation Studies (Memory & Graph Components)...")
        ablations = evaluator.run_ablation_study()
        print(json.dumps(ablations, indent=2))
        print("\nAdaptive Memory & Graph Evaluation Complete.\n")
    finally:
        db.close()


if __name__ == "__main__":
    main()




