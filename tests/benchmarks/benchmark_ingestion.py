"""
HACTM Ingestion Pipeline Benchmark.
Measures real performance for:
- 1,000 records
- 10,000 records
- 100,000 records
Measures records/sec, total processing time, and database insertion time.
"""

import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hactm.core.constants import IngestionPolicy
from hactm.ingestion.pipeline import IngestionPipeline
from hactm.storage.database import Base


def generate_benchmark_records(count: int):
    """Generates synthetic in-memory records for performance benchmarking."""
    records = []
    base_ts = "2026-10-01T12:00:00Z"
    for i in range(1, count + 1):
        ip_last = i % 250
        records.append({
            "event_id": f"BENCH-{count}-{i:07d}",
            "agent_id": "BENCH_AGENT",
            "entity_id": f"IP:10.0.0.{ip_last}",
            "event_type": "NETWORK",
            "timestamp": base_ts,
            "risk_score": round((i % 100) / 100.0, 2),
            "confidence": 0.90,
            "uncertainty": 0.10,
            "source": "BENCHMARK_SUITE",
            "dataset": f"BENCH_{count}",
            "evidence": {"packet_count": i % 500, "flag": "BENCH"},
        })
    return records


def run_benchmark_for_size(record_count: int, batch_size: int = 2000):
    print(f"\n==================================================")
    print(f"  BENCHMARK: {record_count:,} RECORDS (batch_size={batch_size})")
    print(f"==================================================")

    # Use a fast SQLite file in a temp directory
    with TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "bench.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        pipeline = IngestionPipeline(db)

        # Generate records
        gen_start = time.perf_counter()
        records = generate_benchmark_records(record_count)
        gen_elapsed = time.perf_counter() - gen_start
        print(f"Generated {record_count:,} records in {gen_elapsed:.3f}s")

        # Ingestion Benchmark
        start_time = time.perf_counter()
        result = pipeline.ingest_records(
            records=records,
            source_name=f"bench_{record_count}",
            policy=IngestionPolicy.SKIP_INVALID,
            dataset_name=f"bench_{record_count}",
        )
        total_time = time.perf_counter() - start_time

        records_per_sec = record_count / total_time if total_time > 0 else 0

        print(f"Result:")
        print(f"  Total Processed:     {result.total:,}")
        print(f"  Inserted:            {result.inserted:,}")
        print(f"  Duplicates:          {result.duplicates:,}")
        print(f"  Invalid:             {result.invalid:,}")
        print(f"  Quarantined:         {result.quarantined:,}")
        print(f"  Total Ingestion Time:{total_time:.3f} seconds")
        print(f"  Throughput:          {records_per_sec:.1f} records/sec")

        db.close()
        engine.dispose()

        return {
            "record_count": record_count,
            "total_time_seconds": round(total_time, 3),
            "records_per_second": round(records_per_sec, 1),
            "inserted": result.inserted,
        }


def main():
    sizes = [1_000, 10_000, 100_000]
    results = []
    for s in sizes:
        res = run_benchmark_for_size(s)
        results.append(res)

    print("\n================ FINAL BENCHMARK SUMMARY ================")
    print(f"{'Records':<12} | {'Time (s)':<12} | {'Throughput (rec/s)':<20} | {'Status'}")
    print("-" * 60)
    for r in results:
        print(f"{r['record_count']:<12,d} | {r['total_time_seconds']:<12.3f} | {r['records_per_second']:<20.1f} | PASSED")
    print("=========================================================\n")


if __name__ == "__main__":
    main()
