"""
Unit tests for CSV, JSON, and JSONL dataset loaders.
"""

from pathlib import Path
import pytest

from hactm.ingestion.loaders.csv_loader import CSVLoader
from hactm.ingestion.loaders.json_loader import JSONLoader
from hactm.ingestion.loaders.jsonl_loader import JSONLLoader


def test_missing_file_raises_not_found(tmp_path):
    missing_file = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError):
        CSVLoader(missing_file)


def test_empty_files_stream_empty(tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("", encoding="utf-8")
    loader_csv = CSVLoader(empty_csv)
    batches_csv = list(loader_csv.stream_batches(batch_size=10))
    assert len(batches_csv) == 0

    empty_json = tmp_path / "empty.json"
    empty_json.write_text("", encoding="utf-8")
    loader_json = JSONLoader(empty_json)
    batches_json = list(loader_json.stream_batches(batch_size=10))
    assert len(batches_json) == 0

    empty_jsonl = tmp_path / "empty.jsonl"
    empty_jsonl.write_text("", encoding="utf-8")
    loader_jsonl = JSONLLoader(empty_jsonl)
    batches_jsonl = list(loader_jsonl.stream_batches(batch_size=10))
    assert len(batches_jsonl) == 0


def test_csv_loader_quoted_and_embedded_json(tmp_path):
    csv_file = tmp_path / "sample.csv"
    content = (
        'event_id,risk_score,evidence,notes\n'
        'EVT-CSV-1,0.5,"{""port"": 80, ""proto"": ""TCP""}","Quoted string with, comma"\n'
        'EVT-CSV-2,0.9,"{""flag"": true}","Simple note"\n'
    )
    csv_file.write_text(content, encoding="utf-8-sig")

    loader = CSVLoader(csv_file)
    batches = list(loader.stream_batches(batch_size=1))
    assert len(batches) == 2
    row1_num, row1_data = batches[0][0]
    assert row1_num == 2
    assert row1_data["event_id"] == "EVT-CSV-1"
    assert isinstance(row1_data["evidence"], dict)
    assert row1_data["evidence"]["port"] == 80
    assert row1_data["notes"] == "Quoted string with, comma"


def test_json_loader_array_and_object(tmp_path):
    # Top-level array
    json_array = tmp_path / "array.json"
    json_array.write_text('[{"event_id": "J1", "risk_score": 0.2}, {"event_id": "J2", "risk_score": 0.4}]', encoding="utf-8")
    loader_arr = JSONLoader(json_array)
    batches = list(loader_arr.stream_batches(batch_size=10))
    assert len(batches) == 1
    assert len(batches[0]) == 2

    # Wrapped object under 'data'
    json_wrapped = tmp_path / "wrapped.json"
    json_wrapped.write_text('{"data": [{"event_id": "W1", "risk_score": 0.1}]}', encoding="utf-8")
    loader_wr = JSONLoader(json_wrapped)
    batches_wr = list(loader_wr.stream_batches(batch_size=10))
    assert len(batches_wr[0]) == 1
    assert batches_wr[0][0][1]["event_id"] == "W1"


def test_jsonl_loader_with_malformed_line(tmp_path):
    jsonl_file = tmp_path / "test.jsonl"
    content = (
        '{"event_id": "L1", "risk_score": 0.1}\n'
        '\n'  # empty line should be skipped
        'INVALID_JSON_LINE\n'
        '{"event_id": "L2", "risk_score": 0.8}\n'
    )
    jsonl_file.write_text(content, encoding="utf-8")

    loader = JSONLLoader(jsonl_file)
    batches = list(loader.stream_batches(batch_size=10))
    records = batches[0]
    assert len(records) == 3
    # Second item is marked malformed
    assert "__malformed_json_error__" in records[1][1]
    assert records[2][1]["event_id"] == "L2"
