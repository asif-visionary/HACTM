export type SeverityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type EventType =
  | 'NETWORK'
  | 'EMAIL'
  | 'AUTHENTICATION'
  | 'UBA'
  | 'TRANSACTION'
  | 'SYSTEM'
  | 'IDENTITY'
  | 'OTHER';

export interface SecurityEvidence {
  event_id: string;
  agent_id: string;
  entity_id: string;
  event_type: string;
  timestamp: string;
  risk_score: number;
  confidence: number;
  uncertainty: number;
  severity: SeverityLevel;
  evidence: Record<string, any>;

  source?: string | null;
  source_type?: string | null;
  dataset?: string | null;
  dataset_name?: string | null;
  dataset_version?: string | null;
  schema_version?: string | null;
  preprocessing_version?: string | null;
  source_record_id?: string | null;
  ingestion_run_id?: string | null;

  security_tags: string[];
  security_group?: string | null;
  security_zone?: string | null;

  created_at?: string;
  updated_at?: string;

  // Reserved future extensions
  calibrated_probability?: number | null;
  agent_reliability?: number | null;
  evidence_quality?: number | null;
  recommended_action?: string | null;
}

export interface IngestionRunResult {
  run_id: string;
  inserted: number;
  duplicates: number;
  invalid: number;
  quarantined: number;
  failed: number;
  total: number;
}
