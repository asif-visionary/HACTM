"""
Unit tests for deterministic entity resolution.
"""

from hactm.core.constants import EntityType
from hactm.ingestion.entity_resolution import resolve_entity


def test_deterministic_email_resolution():
    # Varying casing and whitespace must resolve to same canonical entity
    rec1 = {"email": "  Analyst.Alice@Corp.NET "}
    rec2 = {"user_email": "analyst.alice@corp.net"}

    id1, type1, name1, attrs1 = resolve_entity(rec1)
    id2, type2, name2, attrs2 = resolve_entity(rec2)

    assert id1 == id2 == "EMAIL:analyst.alice@corp.net"
    assert type1 == type2 == EntityType.EMAIL
    assert name1 == name2 == "analyst.alice@corp.net"


def test_deterministic_ip_resolution():
    # IPv4 resolution
    rec1 = {"src_ip": "10.0.1.25"}
    id1, type1, name1, attrs1 = resolve_entity(rec1)
    assert id1 == "IP:10.0.1.25"
    assert type1 == EntityType.IP
    assert attrs1["ip_version"] == "IPv4"

    # IPv6 resolution
    rec2 = {"ip": "2001:0db8:0000:0000:0000:0000:0000:0001"}
    id2, type2, name2, attrs2 = resolve_entity(rec2)
    assert id2.startswith("IP:2001:db8::1") or id2.startswith("IP:2001:0db8")
    assert type2 == EntityType.IP
    assert attrs2["ip_version"] == "IPv6"


def test_explicit_prefixed_identifiers():
    # Explicit USER
    id_u, type_u, name_u, _ = resolve_entity({"entity_id": "USER:admin_sec"})
    assert id_u == "USER:admin_sec"
    assert type_u == EntityType.USER

    # Explicit HOST
    id_h, type_h, name_h, _ = resolve_entity({"entity_id": "HOST:DC-PRIMARY-01"})
    assert id_h == "HOST:dc-primary-01"
    assert type_h == EntityType.HOST

    # Explicit DEVICE
    id_d, type_d, name_d, _ = resolve_entity({"entity_id": "DEVICE:ATM_BRANCH_44"})
    assert id_d == "DEVICE:ATM_BRANCH_44"
    assert type_d == EntityType.DEVICE
