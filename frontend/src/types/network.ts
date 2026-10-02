export interface NetworkEvent {
  event_id: string;
  timestamp: string;
  src_ip: string;
  dst_ip: string;
  src_port: number | null;
  dst_port: number | null;
  protocol: string;
  duration: number | null;
  flow_bytes: number | null;
  flow_packets: number | null;
  forward_bytes?: number | null;
  backward_bytes?: number | null;
  forward_packets?: number | null;
  backward_packets?: number | null;
  tcp_flags?: string | null;
  connection_state?: string | null;
  flow_rate?: number | null;
  packet_rate?: number | null;
  dataset?: string | null;
  dataset_version?: string | null;
  source_record_id?: string | null;
  metadata?: Record<string, any>;
}

export type DetectorType = 'SIGNATURE' | 'HEURISTIC' | 'ANOMALY';
export type SeverityLevel = 'INFORMATIONAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface NetworkDetection {
  detection_id: string;
  event_id: string;
  detector_type: DetectorType;
  detector_id: string;
  detector_version: string;
  category: string;
  risk_score: number;
  confidence: number;
  uncertainty: number;
  severity: SeverityLevel;
  reason_codes: string[];
  explanation: string;
  features_used: Record<string, any>;
  timestamp: string;
  model_version?: string | null;
  signature_id?: string | null;
  processing_time_ms?: number | null;
  created_at: string;
  // Denormalized/enriched metadata if present
  src_ip?: string;
  dst_ip?: string;
}

export interface NetworkModel {
  model_id: string;
  model_version: string;
  algorithm: string;
  training_dataset?: string | null;
  training_timestamp: string;
  feature_schema_version: string;
  parameters: Record<string, any>;
  random_seed: number;
  is_active: boolean;
  created_at: string;
}

export interface NetworkHealth {
  status: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
  events_processed: number;
  detections_generated: number;
  errors: number;
  last_event_time: string | null;
  last_success_time: string | null;
  processing_rate: number;
  average_latency: number;
  active_model_id: string | null;
  active_model_version: string | null;
}

export interface NetworkMetrics {
  total_events: number;
  total_detections: number;
  high_risk_detections: number;
  detection_rate: number;
  processing_rate: number;
  detector_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  recent_events_timeline: { timestamp: string; count: number }[];
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
}

export interface ConfusionMatrix {
  tp: number;
  fp: number;
  tn: number;
  fn: number;
}

export interface EvaluationResult {
  precision: number;
  recall: number;
  f1: number;
  fpr: number;
  fnr: number;
  roc_auc: number | null;
  pr_auc: number | null;
  confusion_matrix: ConfusionMatrix;
  sample_count: number;
}

export type FeedbackLabel = 'TRUE_POSITIVE' | 'FALSE_POSITIVE' | 'TRUE_NEGATIVE' | 'FALSE_NEGATIVE' | 'UNKNOWN';

export interface DetectionFeedback {
  feedback_id?: string;
  detection_id: string;
  label: FeedbackLabel;
  analyst_note?: string;
  created_at?: string;
}
