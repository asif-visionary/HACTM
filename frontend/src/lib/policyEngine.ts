export interface ContextualFlags {
  newDevice?: boolean;
  identityAnomaly?: boolean;
  criticalThreatIntel?: boolean;
  confirmedCredentialAttack?: boolean;
  maliciousDevice?: boolean;
  confirmedFraud?: boolean;
  criticalNetworkAttack?: boolean;
  highUncertainty?: boolean;
}

export interface TrustEvaluationInput {
  riskScore: number; // 0-100
  confidence?: number; // 0-100
  uncertainty?: number; // 0-100
  domainRisks?: {
    networkRisk?: number;
    identityRisk?: number;
    deviceRisk?: number;
    behaviourRisk?: number;
    transactionRisk?: number;
    threatIntelRisk?: number;
  };
  contextualFlags?: ContextualFlags;
  eventTitle?: string;
  entityId?: string;
}

export interface TrustDecisionResult {
  decision: 'ALLOW' | 'VERIFY' | 'BLOCK';
  riskScore: number;
  confidence: number;
  uncertainty: number;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  reason: string;
  recommendedAction: string;
  hasOverride: boolean;
  overrideReason?: string;
  whyBreakdown: Array<{
    title: string;
    subtitle: string;
    badge: string;
    badgeColor: string; // 'amber' | 'emerald' | 'rose' | 'cyan' | 'yellow'
  }>;
}

export function evaluateTrustDecision(input: TrustEvaluationInput): TrustDecisionResult {
  const riskScore = Math.max(0, Math.min(100, Math.round(input.riskScore)));
  const confidence = input.confidence !== undefined ? Math.max(0, Math.min(100, Math.round(input.confidence))) : 94;
  const uncertainty = input.uncertainty !== undefined ? Math.max(0, Math.min(100, Math.round(input.uncertainty))) : Math.max(0, 100 - confidence);

  const flags = input.contextualFlags || {};

  // Check for Critical Block Overrides first
  const hasCriticalOverride =
    flags.criticalThreatIntel ||
    flags.confirmedCredentialAttack ||
    flags.maliciousDevice ||
    flags.confirmedFraud ||
    flags.criticalNetworkAttack;

  // Check for Contextual Elevation Overrides (Low Risk elevated to VERIFY)
  const hasElevationOverride =
    !hasCriticalOverride &&
    riskScore < 30 &&
    (flags.newDevice || flags.identityAnomaly || (flags.highUncertainty || uncertainty > 40));

  let decision: 'ALLOW' | 'VERIFY' | 'BLOCK' = 'ALLOW';
  let hasOverride = false;
  let overrideReason = '';

  if (hasCriticalOverride) {
    decision = 'BLOCK';
    hasOverride = true;
    if (flags.criticalThreatIntel) overrideReason = 'Critical Threat Intelligence Match';
    else if (flags.confirmedCredentialAttack) overrideReason = 'Confirmed Credential Stuffing Attack';
    else if (flags.criticalNetworkAttack) overrideReason = 'Critical Intrusion Payload Correlated';
    else if (flags.confirmedFraud) overrideReason = 'High Velocity Financial Fraud Correlated';
    else overrideReason = 'Critical Malicious Endpoint Posture';
  } else if (hasElevationOverride) {
    decision = 'VERIFY';
    hasOverride = true;
    if (flags.newDevice && flags.identityAnomaly) {
      overrideReason = 'Contextual Identity and Device Anomalies';
    } else if (uncertainty > 40) {
      overrideReason = 'High Prediction Uncertainty';
    } else if (flags.newDevice) {
      overrideReason = 'Unrecognized Endpoint Device';
    } else {
      overrideReason = 'Identity Anomalous Pattern';
    }
  } else {
    // Base Risk Policy Thresholds:
    // 0-29: ALLOW
    // 30-79: VERIFY
    // 80-100: BLOCK
    if (riskScore >= 80) {
      decision = 'BLOCK';
    } else if (riskScore >= 30) {
      decision = 'VERIFY';
    } else {
      decision = 'ALLOW';
    }
  }

  // Calculate Severity consistently from Risk Score and Decision
  let severity: TrustDecisionResult['severity'] = 'LOW';
  if (decision === 'BLOCK' || riskScore >= 80) {
    severity = 'CRITICAL';
  } else if (riskScore >= 60) {
    severity = 'HIGH';
  } else if (riskScore >= 30 || decision === 'VERIFY') {
    severity = 'MEDIUM';
  } else if (riskScore <= 15) {
    severity = 'INFO';
  } else {
    severity = 'LOW';
  }

  // Calculate Reasoning & Recommended Action
  let reason = '';
  let recommendedAction = '';

  if (decision === 'ALLOW') {
    reason = 'Low overall risk with high confidence and no critical contextual indicators.';
    recommendedAction = 'Permit activity & background telemetry monitoring';
  } else if (decision === 'VERIFY') {
    if (hasElevationOverride) {
      reason = `Low raw risk elevated to verification due to ${overrideReason.toLowerCase()}.`;
      recommendedAction = 'Require 2FA & Step-up Device Attestation';
    } else if (uncertainty > 40) {
      reason = 'High prediction uncertainty requires human analyst review and step-up auth.';
      recommendedAction = 'Require 2FA & Manual SOC Analyst Review';
    } else {
      reason = 'Moderate risk requires additional verification.';
      recommendedAction = 'Require 2FA verification';
    }
  } else {
    if (hasOverride) {
      reason = `Critical security override triggered: ${overrideReason}.`;
    } else {
      reason = 'Critical risk detected with high confidence.';
    }
    recommendedAction = 'Block activity and initiate incident response';
  }

  // Construct WHY Contextual Breakdown cards
  const whyBreakdown = [
    {
      title: 'DEVICE FINGERPRINT',
      subtitle: flags.newDevice ? 'Unrecognized MAC / Hardware ID' : 'Hardware signature verified',
      badge: flags.newDevice ? 'New Device Detected' : 'Verified Device',
      badgeColor: flags.newDevice ? 'amber' : 'emerald',
    },
    {
      title: 'GEO-LOCATION TELEMETRY',
      subtitle: flags.identityAnomaly ? 'Frankfurt, DE vs Baseline (Tokyo, JP)' : 'Location within normal baseline',
      badge: flags.identityAnomaly ? 'Unusual Location' : 'Normal Geo-Location',
      badgeColor: flags.identityAnomaly ? 'amber' : 'emerald',
    },
    {
      title: 'BEHAVIOUR DEVIATION',
      subtitle: riskScore > 50 ? '+38% Off-hours file access surge' : 'Behavioral variance within 1.2 sigma',
      badge: riskScore > 50 ? '+38% Variance' : 'Normal Baseline',
      badgeColor: riskScore > 50 ? 'rose' : 'emerald',
    },
    {
      title: 'TRANSACTION RISK',
      subtitle: riskScore > 60 ? 'Payload amount: $12,450 (High Velocity)' : 'Payload amount: $4,250 (Verified)',
      badge: riskScore > 60 ? 'High Risk' : riskScore > 30 ? 'Medium Risk' : 'Low Risk',
      badgeColor: riskScore > 60 ? 'rose' : riskScore > 30 ? 'yellow' : 'emerald',
    },
    {
      title: 'IDENTITY CONFIDENCE',
      subtitle: `${confidence}% Confidence Score`,
      badge: `${confidence}% Score`,
      badgeColor: confidence >= 90 ? 'cyan' : 'amber',
    },
    {
      title: 'TEMPORAL CORRELATION',
      subtitle: `${uncertainty}% Uncertainty Factor`,
      badge: `${uncertainty}% Uncertainty`,
      badgeColor: uncertainty > 30 ? 'rose' : 'emerald',
    },
  ];

  return {
    decision,
    riskScore,
    confidence,
    uncertainty,
    severity,
    reason,
    recommendedAction,
    hasOverride,
    overrideReason,
    whyBreakdown,
  };
}

// -------------------------------------------------------------
// DETERMINISTIC DEMO SCENARIOS
// -------------------------------------------------------------
export interface DemoScenario {
  id: string;
  name: string;
  label: string;
  input: TrustEvaluationInput;
}

export const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: 'SCENARIO_1',
    name: 'SCENARIO 1: Normal Trusted Activity',
    label: '🟢 ALLOW (Risk 18)',
    input: {
      riskScore: 18,
      confidence: 96,
      uncertainty: 4,
      contextualFlags: { newDevice: false, identityAnomaly: false },
    },
  },
  {
    id: 'SCENARIO_2',
    name: 'SCENARIO 2: Suspicious Login',
    label: '🟡 VERIFY (Risk 48)',
    input: {
      riskScore: 48,
      confidence: 91,
      uncertainty: 9,
      contextualFlags: { identityAnomaly: true },
    },
  },
  {
    id: 'SCENARIO_3',
    name: 'SCENARIO 3: High-Risk Device',
    label: '🟡 VERIFY (Risk 76)',
    input: {
      riskScore: 76,
      confidence: 94,
      uncertainty: 6,
      contextualFlags: { newDevice: true },
    },
  },
  {
    id: 'SCENARIO_4',
    name: 'SCENARIO 4: Confirmed Attack',
    label: '🔴 BLOCK (Risk 94)',
    input: {
      riskScore: 94,
      confidence: 98,
      uncertainty: 2,
      contextualFlags: { criticalNetworkAttack: true, criticalThreatIntel: true },
    },
  },
  {
    id: 'SCENARIO_5',
    name: 'SCENARIO 5: Low Raw Risk + Suspicious Context',
    label: '🟡 VERIFY Override (Risk 27)',
    input: {
      riskScore: 27,
      confidence: 90,
      uncertainty: 10,
      contextualFlags: { newDevice: true, identityAnomaly: true },
    },
  },
];
