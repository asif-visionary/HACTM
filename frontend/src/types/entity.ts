import { SecurityEvidence } from './evidence';

export type EntityType = 'IP' | 'EMAIL' | 'USER' | 'HOST' | 'DEVICE' | 'ACCOUNT' | 'UNKNOWN';

export interface Entity {
  entity_id: string;
  entity_type: EntityType | string;
  canonical_name: string;
  attributes: Record<string, any>;
  first_seen: string;
  last_seen: string;
  event_count: number;
}

export interface EntityDetail extends Entity {
  associated_evidence: SecurityEvidence[];
}
