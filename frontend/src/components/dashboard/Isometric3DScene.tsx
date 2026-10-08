import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export interface Agent3DData {
  id: string;
  name: string;
  type: 'NETWORK' | 'IDENTITY' | 'DEVICE' | 'BEHAVIOUR' | 'TRANSACTION' | 'THREAT_INTEL';
  status: 'ONLINE' | 'ANALYZING' | 'WARNING' | 'OFFLINE';
  eventsPerSec: number;
  riskScore: number; // 0-100
  confidence: number; // 0-100
  modelVersion: string;
  color: string;
  position: [number, number, number];
  description: string;
  activeAnomalies: number;
  lastEvent: string;
  evidenceList: string[];
}

export const INITIAL_AGENTS_DATA: Agent3DData[] = [
  {
    id: 'agent-network',
    name: 'Network Security Agent',
    type: 'NETWORK',
    status: 'ONLINE',
    eventsPerSec: 428,
    riskScore: 24,
    confidence: 96,
    modelVersion: 'NetworkGuard v2.4',
    color: '#00f0ff', // Cyan
    position: [0, 0, -5.5],
    description: 'Monitors flow anomalies, ingress/egress spikes & intrusion telemetry',
    activeAnomalies: 1,
    lastEvent: '19:48:09',
    evidenceList: ['Unusual traffic spike on port 8443', 'Destination IP anomaly', 'Historical payload deviation'],
  },
  {
    id: 'agent-identity',
    name: 'Identity & Auth Agent',
    type: 'IDENTITY',
    status: 'ONLINE',
    eventsPerSec: 312,
    riskScore: 68,
    confidence: 91,
    modelVersion: 'IdentityAuth v3.1',
    color: '#a855f7', // Purple/Violet
    position: [-5.2, 0, -2.2],
    description: 'Detects brute-force, impossible travel & credential stuffing attacks',
    activeAnomalies: 3,
    lastEvent: '19:48:06',
    evidenceList: ['Impossible velocity travel (Frankfurt -> Tokyo in 12m)', 'Unrecognized device token', 'Passkey 2FA pending'],
  },
  {
    id: 'agent-device',
    name: 'Device Agent',
    type: 'DEVICE',
    status: 'ONLINE',
    eventsPerSec: 184,
    riskScore: 42,
    confidence: 94,
    modelVersion: 'DeviceShield v1.8',
    color: '#10b981', // Emerald Green
    position: [-5.2, 0, 2.2],
    description: 'Endpoint compliance, process execution anomalies & hardware integrity',
    activeAnomalies: 2,
    lastEvent: '19:48:03',
    evidenceList: ['Hardware MAC fingerprint mismatch', 'Unsigned DLL process execution', 'Endpoint compliance check passed'],
  },
  {
    id: 'agent-uba',
    name: 'Behaviour / UBA Agent',
    type: 'BEHAVIOUR',
    status: 'ONLINE',
    eventsPerSec: 156,
    riskScore: 74,
    confidence: 89,
    modelVersion: 'BehaviorX v4.0',
    color: '#f59e0b', // Amber/Gold
    position: [0, 0, 5.5],
    description: 'Tracks user behavioral baseline, temporal deviations & privilege abuse',
    activeAnomalies: 4,
    lastEvent: '19:47:58',
    evidenceList: ['+38% burst in sensitive file reads', 'Off-hours database query burst', 'Privilege elevation request'],
  },
  {
    id: 'agent-transaction',
    name: 'Transaction Agent',
    type: 'TRANSACTION',
    status: 'ONLINE',
    eventsPerSec: 112,
    riskScore: 38,
    confidence: 97,
    modelVersion: 'FinGuard AI v2.2',
    color: '#f43f5e', // Rose/Red
    position: [5.2, 0, 2.2],
    description: 'Evaluates transaction velocity, high-value transfers & payment risk',
    activeAnomalies: 1,
    lastEvent: '19:47:50',
    evidenceList: ['Wire transfer $4,250 within historical limit', 'Card velocity normal', 'Beneficiary account verified'],
  },
  {
    id: 'agent-threat',
    name: 'Threat Intelligence Agent',
    type: 'THREAT_INTEL',
    status: 'ONLINE',
    eventsPerSec: 92,
    riskScore: 18,
    confidence: 98,
    modelVersion: 'GlobalIntel v5.6',
    color: '#06b6d4', // Sky Blue/Teal
    position: [5.2, 0, -2.2],
    description: 'Correlates global IOCs, CVE feeds & zero-day threat patterns',
    activeAnomalies: 0,
    lastEvent: '19:47:42',
    evidenceList: ['Ingested 1,420 fresh malicious IOC IPs', 'CVE-2026-1082 signature match', 'Tor exit node correlation'],
  },
];

export interface Node3DData {
  id: string;
  name: string;
  type: string;
  position: [number, number, number];
  color: string;
}

export const INFRASTRUCTURE_NODES: Node3DData[] = [
  { id: 'node-gw1', name: 'Edge Gateway Alpha', type: 'Gateway', position: [0, 0, -14], color: '#00f0ff' },
  { id: 'node-cloud', name: 'AWS Cloud Region 1', type: 'Cloud Infrastructure', position: [-12.5, 0, -9.5], color: '#3b82f6' },
  { id: 'node-auth-db', name: 'Primary Auth Vault', type: 'Identity Node', position: [13, 0, -8], color: '#a855f7' },
  { id: 'node-ep-cluster', name: 'Workstation Segment B', type: 'Workstation', position: [13.5, 0, 8.5], color: '#10b981' },
  { id: 'node-uba-monitor', name: 'Log Pipeline Kafka', type: 'Data Pipeline', position: [0, 0, 14], color: '#f59e0b' },
  { id: 'node-fin-sw', name: 'SWIFT Terminal', type: 'Transaction Terminal', position: [-13, 0, 9], color: '#f43f5e' },
  { id: 'node-radar', name: 'Security Sensor North', type: 'Security Sensor', position: [-12.5, 0, -5], color: '#06b6d4' },
];

interface Isometric3DSceneProps {
  agentsData?: Agent3DData[];
  selectedAgentId?: string | null;
  selectedDecision?: 'ALLOW' | 'VERIFY' | 'BLOCK';
  onSelectAgent?: (agent: Agent3DData) => void;
  cameraPreset?: 'ISO_45' | 'TOP_DOWN' | 'FRONT' | 'FREE';
  showDataStreams?: boolean;
  showGrid?: boolean;
  showNodes?: boolean;
}

export const Isometric3DScene: React.FC<Isometric3DSceneProps> = ({
  agentsData = INITIAL_AGENTS_DATA,
  selectedAgentId = null,
  selectedDecision = 'VERIFY',
  onSelectAgent,
  cameraPreset = 'ISO_45',
  showDataStreams = true,
  showGrid = true,
  showNodes = true,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hoveredAgent, setHoveredAgent] = useState<Agent3DData | null>(null);
  const [hoveredNode, setHoveredNode] = useState<Node3DData | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Refs for animation loop & interactive controls
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const coreMeshRef = useRef<THREE.Mesh | null>(null);
  const ring1Ref = useRef<THREE.Mesh | null>(null);
  const ring2Ref = useRef<THREE.Mesh | null>(null);
  const ring3Ref = useRef<THREE.Mesh | null>(null);
  const fusionRingRef = useRef<THREE.Mesh | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const streamParticlesRef = useRef<{ mesh: THREE.Mesh; path: THREE.CatmullRomCurve3; speed: number; progress: number }[]>([]);
  const agentMeshesRef = useRef<Map<string, THREE.Group>>(new Map());
  const tubeMeshesRef = useRef<Map<string, THREE.Mesh>>(new Map());
  const isDraggingRef = useRef<boolean>(false);
  const previousMousePositionRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const cameraTargetLookAtRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 1, 0));
  const targetRadiusRef = useRef<number>(26);
  const cameraRotationRef = useRef<{ theta: number; phi: number; radius: number }>({
    theta: Math.PI / 4,
    phi: Math.PI / 4.2,
    radius: 26,
  });

  // Responsive scene fitting function to dynamically calculate camera distance
  const fitIsometricScene = () => {
    if (!mountRef.current || !cameraRef.current) return;
    const container = mountRef.current;
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w === 0 || h === 0) return;

    const aspect = w / h;
    const camera = cameraRef.current;
    camera.aspect = aspect;
    camera.updateProjectionMatrix();

    const { theta, phi } = cameraRotationRef.current;
    const target = cameraTargetLookAtRef.current;

    // Bounding box strictly enclosing the 6 compact agents and central AI core
    const bbox = {
      minX: -5.8, maxX: 5.8,
      minY: 0.0,  maxY: 3.5,
      minZ: -6.0, maxZ: 6.0,
    };

    const corners: THREE.Vector3[] = [
      new THREE.Vector3(bbox.minX, bbox.minY, bbox.minZ),
      new THREE.Vector3(bbox.minX, bbox.minY, bbox.maxZ),
      new THREE.Vector3(bbox.minX, bbox.maxY, bbox.minZ),
      new THREE.Vector3(bbox.minX, bbox.maxY, bbox.maxZ),
      new THREE.Vector3(bbox.maxX, bbox.minY, bbox.minZ),
      new THREE.Vector3(bbox.maxX, bbox.minY, bbox.maxZ),
      new THREE.Vector3(bbox.maxX, bbox.maxY, bbox.minZ),
      new THREE.Vector3(bbox.maxX, bbox.maxY, bbox.maxZ),
    ];

    const sinPhi = Math.sin(phi);
    const cosPhi = Math.cos(phi);
    const sinTheta = Math.sin(theta);
    const cosTheta = Math.cos(theta);

    // Unit vectors for camera orientation
    const dir = new THREE.Vector3(sinPhi * cosTheta, cosPhi, sinPhi * sinTheta).normalize();
    const right = new THREE.Vector3(-sinTheta, 0, cosTheta).normalize();
    const up = new THREE.Vector3().crossVectors(dir, right).normalize();

    const halfFovRad = (camera.fov * Math.PI) / 360;
    const tanHalfFov = Math.tan(halfFovRad);
    const padding = 1.25; // ~25% padding margin to comfortably clear top/bottom HUD overlays

    let maxReqRadius = 0;

    corners.forEach((corner) => {
      const pRel = new THREE.Vector3().subVectors(corner, target);
      const distForward = pRel.dot(dir);
      const distRight = Math.abs(pRel.dot(right));
      const distUp = Math.abs(pRel.dot(up));

      const reqV = distForward + (distUp * padding) / tanHalfFov;
      const reqH = distForward + (distRight * padding) / (aspect * tanHalfFov);

      maxReqRadius = Math.max(maxReqRadius, reqV, reqH);
    });

    const calculatedRadius = Math.max(26, Math.min(50, maxReqRadius));
    targetRadiusRef.current = calculatedRadius;
  };

  // Dynamic status color depending on decision
  const getDecisionColorHex = (dec: 'ALLOW' | 'VERIFY' | 'BLOCK') => {
    if (dec === 'ALLOW') return '#10b981'; // Green
    if (dec === 'VERIFY') return '#f59e0b'; // Amber/Yellow
    return '#ef4444'; // Red
  };

  // 1. Initialize Three.js Scene
  useEffect(() => {
    if (!mountRef.current) return;
    const container = mountRef.current;
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    // Create Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#050811');
    scene.fog = new THREE.FogExp2('#050811', 0.018);
    sceneRef.current = scene;

    // Create Camera (Low FOV Perspective for Isometric Feel)
    const camera = new THREE.PerspectiveCamera(35, width / height, 0.1, 1000);
    cameraRef.current = camera;

    const updateCameraPos = () => {
      const { theta, phi, radius } = cameraRotationRef.current;
      const target = cameraTargetLookAtRef.current;
      camera.position.x = target.x + radius * Math.sin(phi) * Math.cos(theta);
      camera.position.y = target.y + radius * Math.cos(phi);
      camera.position.z = target.z + radius * Math.sin(phi) * Math.sin(theta);
      camera.lookAt(target);
    };
    updateCameraPos();

    // Create Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    container.appendChild(renderer.domElement);

    // Enhanced Cyber Lighting for High Visibility
    const ambientLight = new THREE.AmbientLight('#182642', 2.6);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight('#00f0ff', 2.2);
    dirLight1.position.set(20, 35, 20);
    dirLight1.castShadow = true;
    dirLight1.shadow.mapSize.width = 2048;
    dirLight1.shadow.mapSize.height = 2048;
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight('#a855f7', 1.4);
    dirLight2.position.set(-20, 25, -20);
    scene.add(dirLight2);

    const fillLight = new THREE.DirectionalLight('#38bdf8', 1.0);
    fillLight.position.set(0, 15, -25);
    scene.add(fillLight);

    // Central Core PointLight
    const corePointLight = new THREE.PointLight(getDecisionColorHex(selectedDecision), 5.5, 30);
    corePointLight.position.set(0, 2, 0);
    scene.add(corePointLight);

    // Ground Grid & Base Floor
    if (showGrid) {
      const gridHelper = new THREE.GridHelper(52, 52, '#00f0ff', '#1e293b');
      gridHelper.position.y = -0.05;
      (gridHelper.material as THREE.Material).opacity = 0.35;
      (gridHelper.material as THREE.Material).transparent = true;
      scene.add(gridHelper);

      // Glowing Base Disk
      const baseGeo = new THREE.CircleGeometry(23, 64);
      const baseMat = new THREE.MeshBasicMaterial({
        color: '#070f20',
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.6,
      });
      const baseMesh = new THREE.Mesh(baseGeo, baseMat);
      baseMesh.rotation.x = -Math.PI / 2;
      baseMesh.position.y = -0.1;
      scene.add(baseMesh);

      // Hexagonal Outer Border Ring
      const hexRingGeo = new THREE.RingGeometry(22.5, 23, 6);
      const hexRingMat = new THREE.MeshBasicMaterial({
        color: '#00f0ff',
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.4,
      });
      const hexRingMesh = new THREE.Mesh(hexRingGeo, hexRingMat);
      hexRingMesh.rotation.x = -Math.PI / 2;
      hexRingMesh.position.y = -0.08;
      scene.add(hexRingMesh);
    }

    // -------------------------------------------------------------
    // CENTRAL AI TRUST ORCHESTRATOR CORE
    // -------------------------------------------------------------
    const coreGroup = new THREE.Group();
    coreGroup.position.set(0, 1.5, 0);
    scene.add(coreGroup);

    // Core Sphere
    const coreGeo = new THREE.IcosahedronGeometry(1.3, 3);
    const coreMat = new THREE.MeshStandardMaterial({
      color: getDecisionColorHex(selectedDecision),
      emissive: getDecisionColorHex(selectedDecision),
      emissiveIntensity: 0.8,
      roughness: 0.2,
      metalness: 0.8,
      wireframe: false,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    coreGroup.add(coreMesh);
    coreMeshRef.current = coreMesh;

    // Core Inner Wireframe Glow
    const coreWireMat = new THREE.MeshBasicMaterial({
      color: '#ffffff',
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const coreWireMesh = new THREE.Mesh(coreGeo, coreWireMat);
    coreWireMesh.scale.set(1.02, 1.02, 1.02);
    coreGroup.add(coreWireMesh);

    // Holographic Rotating Ring 1
    const ring1Geo = new THREE.TorusGeometry(2.3, 0.04, 16, 64);
    const ring1Mat = new THREE.MeshBasicMaterial({ color: '#00f0ff', wireframe: true, transparent: true, opacity: 0.8 });
    const ring1Mesh = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1Mesh.rotation.x = Math.PI / 3;
    coreGroup.add(ring1Mesh);
    ring1Ref.current = ring1Mesh;

    // Holographic Rotating Ring 2
    const ring2Geo = new THREE.TorusGeometry(3.1, 0.03, 16, 64);
    const ring2Mat = new THREE.MeshBasicMaterial({ color: '#a855f7', wireframe: true, transparent: true, opacity: 0.7 });
    const ring2Mesh = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2Mesh.rotation.y = Math.PI / 4;
    coreGroup.add(ring2Mesh);
    ring2Ref.current = ring2Mesh;

    // Holographic Rotating Ring 3
    const ring3Geo = new THREE.TorusGeometry(3.9, 0.02, 16, 64);
    const ring3Mat = new THREE.MeshBasicMaterial({ color: '#3b82f6', wireframe: true, transparent: true, opacity: 0.6 });
    const ring3Mesh = new THREE.Mesh(ring3Geo, ring3Mat);
    ring3Mesh.rotation.z = Math.PI / 6;
    coreGroup.add(ring3Mesh);
    ring3Ref.current = ring3Mesh;

    // EVIDENCE FUSION RING
    const fusionRingGeo = new THREE.RingGeometry(4.8, 5.2, 64);
    const fusionRingMat = new THREE.MeshBasicMaterial({
      color: '#00f0ff',
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.4,
    });
    const fusionRingMesh = new THREE.Mesh(fusionRingGeo, fusionRingMat);
    fusionRingMesh.rotation.x = -Math.PI / 2;
    fusionRingMesh.position.y = -0.04;
    scene.add(fusionRingMesh);
    fusionRingRef.current = fusionRingMesh;

    // Core Rising Particles
    const particleCount = 180;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      particlePositions[i * 3] = (Math.random() - 0.5) * 4.5;
      particlePositions[i * 3 + 1] = Math.random() * 6.5;
      particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 4.5;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: '#00f0ff',
      size: 0.12,
      transparent: true,
      opacity: 0.8,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);
    particlesRef.current = particles;

    // -------------------------------------------------------------
    // BUILD EXACTLY 6 ISOMETRIC SECURITY AGENT MODULES
    // -------------------------------------------------------------
    agentsData.forEach((agent) => {
      const agentGroup = new THREE.Group();
      const [x, y, z] = agent.position;
      agentGroup.position.set(x, y, z);
      (agentGroup as any).userData = { agentData: agent };

      // Base Pedestal
      const pedGeo = new THREE.CylinderGeometry(1.8, 2.0, 0.4, 6);
      const pedMat = new THREE.MeshStandardMaterial({
        color: '#0e1726',
        metalness: 0.8,
        roughness: 0.3,
      });
      const pedMesh = new THREE.Mesh(pedGeo, pedMat);
      pedMesh.position.y = 0.2;
      pedMesh.receiveShadow = true;
      agentGroup.add(pedMesh);

      // Glowing Pedestal Ring
      const pedRingGeo = new THREE.TorusGeometry(1.9, 0.06, 16, 6);
      const pedRingMat = new THREE.MeshBasicMaterial({ color: agent.color });
      const pedRingMesh = new THREE.Mesh(pedRingGeo, pedRingMat);
      pedRingMesh.rotation.x = Math.PI / 2;
      pedRingMesh.position.y = 0.41;
      agentGroup.add(pedRingMesh);

      // -------------------------------------------------------------
      // CUSTOM ISOMETRIC CYBERSECURITY INFRASTRUCTURE ASSET CREATION
      // -------------------------------------------------------------
      const colorThree = new THREE.Color(agent.color);
      const mainChassisMat = new THREE.MeshStandardMaterial({
        color: '#0e1726',
        emissive: colorThree,
        emissiveIntensity: 0.25,
        roughness: 0.25,
        metalness: 0.85,
      });

      const accentMat = new THREE.MeshStandardMaterial({
        color: agent.color,
        emissive: agent.color,
        emissiveIntensity: 0.8,
        roughness: 0.2,
        metalness: 0.5,
      });

      const glassMat = new THREE.MeshPhysicalMaterial({
        color: colorThree,
        transparent: true,
        opacity: 0.75,
        roughness: 0.1,
        metalness: 0.2,
        transmission: 0.5,
      });

      // Status Indicator Light (Color depends on Risk Score: Low = Green/Cyan, Med = Amber, High = Red)
      const statusColor = agent.riskScore >= 70 ? '#ef4444' : agent.riskScore >= 40 ? '#f59e0b' : '#10b981';
      const statusLedMat = new THREE.MeshBasicMaterial({ color: statusColor });

      if (agent.type === 'NETWORK') {
        // -----------------------------------------------------------
        // 1. NETWORK AGENT: Enterprise Router & Firewall Appliance
        // -----------------------------------------------------------
        // Main Router Chassis
        const routerGeo = new THREE.BoxGeometry(1.8, 0.6, 1.2);
        const routerMesh = new THREE.Mesh(routerGeo, mainChassisMat);
        routerMesh.position.y = 0.7;
        routerMesh.castShadow = true;
        agentGroup.add(routerMesh);

        // Front Faceplate Display Bar
        const faceGeo = new THREE.BoxGeometry(1.7, 0.18, 0.04);
        const faceMesh = new THREE.Mesh(faceGeo, accentMat);
        faceMesh.position.set(0, 0.7, 0.61);
        agentGroup.add(faceMesh);

        // Ethernet Port Slots (6 RJ45 Ports)
        for (let i = -0.6; i <= 0.6; i += 0.24) {
          const portGeo = new THREE.BoxGeometry(0.14, 0.12, 0.05);
          const portMat = new THREE.MeshBasicMaterial({ color: '#050914' });
          const portMesh = new THREE.Mesh(portGeo, portMat);
          portMesh.position.set(i, 0.68, 0.62);
          agentGroup.add(portMesh);
        }

        // Dual Antenna Masts
        const antLeftGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.2, 8);
        const antLeft = new THREE.Mesh(antLeftGeo, mainChassisMat);
        antLeft.position.set(-0.7, 1.5, -0.4);
        antLeft.rotation.z = -0.15;
        agentGroup.add(antLeft);

        const antRight = new THREE.Mesh(antLeftGeo, mainChassisMat);
        antRight.position.set(0.7, 1.5, -0.4);
        antRight.rotation.z = 0.15;
        agentGroup.add(antRight);

        // Glowing Signal Tip Spheres
        const tipGeo = new THREE.SphereGeometry(0.08, 8, 8);
        const tipLeft = new THREE.Mesh(tipGeo, accentMat);
        tipLeft.position.set(-0.8, 2.1, -0.4);
        agentGroup.add(tipLeft);

        const tipRight = new THREE.Mesh(tipGeo, accentMat);
        tipRight.position.set(0.8, 2.1, -0.4);
        agentGroup.add(tipRight);

        // Status LED Array
        const led1 = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), statusLedMat);
        led1.position.set(-0.75, 0.88, 0.55);
        agentGroup.add(led1);
      } else if (agent.type === 'IDENTITY') {
        // -----------------------------------------------------------
        // 2. IDENTITY AGENT: Biometric Auth Terminal & Key Vault
        // -----------------------------------------------------------
        // Pedestal Column
        const colGeo = new THREE.CylinderGeometry(0.35, 0.55, 1.2, 8);
        const colMesh = new THREE.Mesh(colGeo, mainChassisMat);
        colMesh.position.y = 1.0;
        colMesh.castShadow = true;
        agentGroup.add(colMesh);

        // Angled Screen Slab (Tilted 25 degrees)
        const screenGeo = new THREE.BoxGeometry(1.4, 0.9, 0.12);
        const screenMesh = new THREE.Mesh(screenGeo, mainChassisMat);
        screenMesh.position.set(0, 1.85, 0.1);
        screenMesh.rotation.x = -Math.PI / 7;
        agentGroup.add(screenMesh);

        // Glowing Holographic Display Screen
        const displayGeo = new THREE.BoxGeometry(1.3, 0.8, 0.02);
        const displayMesh = new THREE.Mesh(displayGeo, glassMat);
        displayMesh.position.set(0, 1.85, 0.17);
        displayMesh.rotation.x = -Math.PI / 7;
        agentGroup.add(displayMesh);

        // Biometric Fingerprint Scanner Sensor Pad
        const fingerPadGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.06, 16);
        const fingerPad = new THREE.Mesh(fingerPadGeo, accentMat);
        fingerPad.position.set(0, 1.5, 0.35);
        fingerPad.rotation.x = Math.PI / 6;
        agentGroup.add(fingerPad);

        // Floating Rotating Holographic Security Ring
        const holoRingGeo = new THREE.TorusGeometry(0.45, 0.04, 12, 32);
        const holoRing = new THREE.Mesh(holoRingGeo, accentMat);
        holoRing.position.set(0, 2.75, 0);
        holoRing.rotation.x = Math.PI / 3;
        agentGroup.add(holoRing);
        (agentGroup as any).userData.holoRing = holoRing;
      } else if (agent.type === 'DEVICE') {
        // -----------------------------------------------------------
        // 3. DEVICE AGENT: Endpoint Workstation & Laptop Cluster
        // -----------------------------------------------------------
        // Workstation Desk Platform
        const deskGeo = new THREE.BoxGeometry(1.9, 0.18, 1.2);
        const desk = new THREE.Mesh(deskGeo, mainChassisMat);
        desk.position.y = 0.6;
        desk.castShadow = true;
        agentGroup.add(desk);

        // Desk Support Legs
        const leg1Geo = new THREE.CylinderGeometry(0.06, 0.06, 0.5, 8);
        const leg1 = new THREE.Mesh(leg1Geo, mainChassisMat);
        leg1.position.set(-0.8, 0.25, -0.4);
        agentGroup.add(leg1);
        const leg2 = new THREE.Mesh(leg1Geo, mainChassisMat);
        leg2.position.set(0.8, 0.25, -0.4);
        agentGroup.add(leg2);

        // Laptop Base Keyboard
        const laptopBaseGeo = new THREE.BoxGeometry(0.9, 0.05, 0.6);
        const laptopBase = new THREE.Mesh(laptopBaseGeo, mainChassisMat);
        laptopBase.position.set(-0.35, 0.72, 0.1);
        agentGroup.add(laptopBase);

        // Laptop Tilted Screen
        const laptopScreenGeo = new THREE.BoxGeometry(0.9, 0.6, 0.04);
        const laptopScreen = new THREE.Mesh(laptopScreenGeo, glassMat);
        laptopScreen.position.set(-0.35, 1.05, -0.2);
        laptopScreen.rotation.x = -Math.PI / 12;
        agentGroup.add(laptopScreen);

        // Endpoint PC Tower Unit
        const towerGeo = new THREE.BoxGeometry(0.4, 1.0, 0.7);
        const tower = new THREE.Mesh(towerGeo, mainChassisMat);
        tower.position.set(0.65, 1.2, 0.0);
        agentGroup.add(tower);

        // Tower Glowing Status Strip
        const stripGeo = new THREE.BoxGeometry(0.04, 0.8, 0.04);
        const strip = new THREE.Mesh(stripGeo, accentMat);
        strip.position.set(0.44, 1.2, 0.34);
        agentGroup.add(strip);
      } else if (agent.type === 'BEHAVIOUR') {
        // -----------------------------------------------------------
        // 4. BEHAVIOUR / UBA AGENT: Analytics Workstation & Chart Console
        // -----------------------------------------------------------
        // Main Console Console Deck
        const deckGeo = new THREE.BoxGeometry(1.8, 0.35, 1.0);
        const deck = new THREE.Mesh(deckGeo, mainChassisMat);
        deck.position.y = 0.7;
        deck.castShadow = true;
        agentGroup.add(deck);

        // Panoramic Display Monitor
        const monGeo = new THREE.BoxGeometry(1.6, 0.85, 0.08);
        const mon = new THREE.Mesh(monGeo, mainChassisMat);
        mon.position.set(0, 1.35, -0.3);
        agentGroup.add(mon);

        // Glowing Screen Face
        const screenFaceGeo = new THREE.BoxGeometry(1.5, 0.75, 0.02);
        const screenFace = new THREE.Mesh(screenFaceGeo, glassMat);
        screenFace.position.set(0, 1.35, -0.25);
        agentGroup.add(screenFace);

        // 3D Floating Graph Bars (4 vertical behavior bars)
        const barHeights = [0.4, 0.7, 0.5, 0.9];
        barHeights.forEach((h, idx) => {
          const barGeo = new THREE.BoxGeometry(0.16, h, 0.16);
          const barMesh = new THREE.Mesh(barGeo, accentMat);
          barMesh.position.set(-0.5 + idx * 0.33, 1.2 + h / 2, -0.22);
          agentGroup.add(barMesh);
        });

        // Floating User Profile Hologram Avatar Sphere
        const avatarGeo = new THREE.SphereGeometry(0.32, 16, 16);
        const avatarMesh = new THREE.Mesh(avatarGeo, glassMat);
        avatarMesh.position.set(0, 2.3, 0);
        agentGroup.add(avatarMesh);
        (agentGroup as any).userData.avatar = avatarMesh;
      } else if (agent.type === 'TRANSACTION') {
        // -----------------------------------------------------------
        // 5. TRANSACTION AGENT: Payment Gateway Terminal & Vault
        // -----------------------------------------------------------
        // Terminal Main Block
        const terminalGeo = new THREE.BoxGeometry(1.4, 1.2, 1.1);
        const terminal = new THREE.Mesh(terminalGeo, mainChassisMat);
        terminal.position.y = 1.0;
        terminal.castShadow = true;
        agentGroup.add(terminal);

        // Angled Top Pinpad & Screen Block
        const topBlockGeo = new THREE.BoxGeometry(1.2, 0.5, 0.8);
        const topBlock = new THREE.Mesh(topBlockGeo, glassMat);
        topBlock.position.set(0, 1.7, 0.1);
        topBlock.rotation.x = Math.PI / 8;
        agentGroup.add(topBlock);

        // Recessed Payment Card Reader Slot
        const slotGeo = new THREE.BoxGeometry(0.8, 0.06, 0.05);
        const slot = new THREE.Mesh(slotGeo, accentMat);
        slot.position.set(0, 1.1, 0.56);
        agentGroup.add(slot);

        // Floating Secure Transaction Flow Rings ($ / transaction ring)
        const txRingGeo1 = new THREE.TorusGeometry(0.4, 0.04, 8, 24);
        const txRing1 = new THREE.Mesh(txRingGeo1, accentMat);
        txRing1.position.set(0, 2.4, 0);
        txRing1.rotation.x = Math.PI / 3;
        agentGroup.add(txRing1);

        const txRingGeo2 = new THREE.TorusGeometry(0.25, 0.03, 8, 24);
        const txRing2 = new THREE.Mesh(txRingGeo2, glassMat);
        txRing2.position.set(0, 2.4, 0);
        txRing2.rotation.y = Math.PI / 4;
        agentGroup.add(txRing2);
        (agentGroup as any).userData.txRing = txRing2;
      } else {
        // -----------------------------------------------------------
        // 6. THREAT INTELLIGENCE AGENT: SOC Threat Radar & Scanner
        // -----------------------------------------------------------
        // Octagonal Base Tower
        const towerGeo = new THREE.CylinderGeometry(0.65, 0.85, 1.3, 8);
        const tower = new THREE.Mesh(towerGeo, mainChassisMat);
        tower.position.y = 1.05;
        tower.castShadow = true;
        agentGroup.add(tower);

        // Tower Mid Ring
        const midRingGeo = new THREE.CylinderGeometry(0.72, 0.72, 0.12, 8);
        const midRing = new THREE.Mesh(midRingGeo, accentMat);
        midRing.position.y = 1.1;
        agentGroup.add(midRing);

        // Rotating Threat Radar Dish
        const dishGeo = new THREE.SphereGeometry(0.6, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2.3);
        const dish = new THREE.Mesh(dishGeo, glassMat);
        dish.position.set(0, 2.0, 0);
        dish.rotation.x = Math.PI / 4;
        agentGroup.add(dish);
        (agentGroup as any).userData.radarDish = dish;

        // Radar Center Feed Horn
        const hornGeo = new THREE.ConeGeometry(0.12, 0.4, 8);
        const horn = new THREE.Mesh(hornGeo, accentMat);
        horn.position.set(0, 2.1, 0.2);
        horn.rotation.x = -Math.PI / 4;
        agentGroup.add(horn);

        // Threat Alert Indicator Pin Spheres
        const threatPinGeo = new THREE.SphereGeometry(0.09, 8, 8);
        const threatPinMat = new THREE.MeshBasicMaterial({ color: '#ef4444' });
        const pin1 = new THREE.Mesh(threatPinGeo, threatPinMat);
        pin1.position.set(0.65, 2.4, 0.4);
        agentGroup.add(pin1);
      }

      // Point light per agent building
      const agentLight = new THREE.PointLight(agent.color, 1.5, 8);
      agentLight.position.set(0, 3, 0);
      agentGroup.add(agentLight);

      scene.add(agentGroup);
      agentMeshesRef.current.set(agent.id, agentGroup);
    });

    // -------------------------------------------------------------
    // PERIPHERAL INFRASTRUCTURE NODES
    // -------------------------------------------------------------
    if (showNodes) {
      INFRASTRUCTURE_NODES.forEach((node) => {
        const nodeGroup = new THREE.Group();
        const [nx, ny, nz] = node.position;
        nodeGroup.position.set(nx, ny, nz);
        (nodeGroup as any).userData = { nodeData: node };

        const nodeGeo = new THREE.BoxGeometry(0.6, 0.8, 0.6);
        const nodeMat = new THREE.MeshStandardMaterial({
          color: '#0f172a',
          emissive: node.color,
          emissiveIntensity: 0.4,
          roughness: 0.3,
        });
        const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);
        nodeMesh.position.y = 0.4;
        nodeGroup.add(nodeMesh);

        // Indicator Light
        const indGeo = new THREE.SphereGeometry(0.12, 8, 8);
        const indMat = new THREE.MeshBasicMaterial({ color: node.color });
        const indMesh = new THREE.Mesh(indGeo, indMat);
        indMesh.position.set(0, 0.95, 0);
        nodeGroup.add(indMesh);

        scene.add(nodeGroup);
      });
    }

    // -------------------------------------------------------------
    // ANIMATED EVIDENCE DATA STREAMS (CURVED PATHS + PARTICLES)
    // -------------------------------------------------------------
    const streamParticles: { mesh: THREE.Mesh; path: THREE.CatmullRomCurve3; speed: number; progress: number }[] = [];

    if (showDataStreams) {
      agentsData.forEach((agent) => {
        const [ax, ay, az] = agent.position;

        // Curve path: Agent -> Evidence Fusion Ring -> AI Core
        const curve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(ax, ay + 1.5, az),
          new THREE.Vector3(ax * 0.5, 0.8, az * 0.5),
          new THREE.Vector3(0, 1.5, 0),
        ]);

        // Tube Geometry for Line
        const tubeGeo = new THREE.TubeGeometry(curve, 32, 0.035, 8, false);
        const tubeMat = new THREE.MeshBasicMaterial({
          color: agent.color,
          transparent: true,
          opacity: 0.4,
          wireframe: false,
        });
        const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
        scene.add(tubeMesh);
        tubeMeshesRef.current.set(agent.id, tubeMesh);

        // Moving Data Packet Particles along curve
        const pGeo = new THREE.SphereGeometry(0.14, 12, 12);
        const pMat = new THREE.MeshBasicMaterial({ color: '#ffffff' });

        for (let i = 0; i < 3; i++) {
          const pMesh = new THREE.Mesh(pGeo, pMat);
          scene.add(pMesh);
          streamParticles.push({
            mesh: pMesh,
            path: curve,
            speed: 0.007 + Math.random() * 0.004,
            progress: (i * 0.33) % 1.0,
          });
        }
      });

      streamParticlesRef.current = streamParticles;
    }

    // -------------------------------------------------------------
    // RAYCASTING & INTERACTION (MOUSE HOVER / CLICK)
    // -------------------------------------------------------------
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleMouseMove = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      setTooltipPos({ x: event.clientX - rect.left, y: event.clientY - rect.top });

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children, true);

      let foundAgent: Agent3DData | null = null;
      let foundNode: Node3DData | null = null;

      for (let hit of intersects) {
        let parent: THREE.Object3D | null = hit.object;
        while (parent && parent !== scene) {
          if ((parent as any).userData?.agentData) {
            foundAgent = (parent as any).userData.agentData;
            break;
          }
          if ((parent as any).userData?.nodeData) {
            foundNode = (parent as any).userData.nodeData;
            break;
          }
          parent = parent.parent;
        }
        if (foundAgent || foundNode) break;
      }

      setHoveredAgent(foundAgent);
      setHoveredNode(foundNode);
      container.style.cursor = foundAgent || foundNode ? 'pointer' : isDraggingRef.current ? 'grabbing' : 'grab';
    };

    const handleMouseDown = (event: MouseEvent) => {
      isDraggingRef.current = true;
      previousMousePositionRef.current = { x: event.clientX, y: event.clientY };
    };

    const handleMouseUp = () => {
      isDraggingRef.current = false;
      container.style.cursor = hoveredAgent || hoveredNode ? 'pointer' : 'grab';
    };

    const handleMouseDrag = (event: MouseEvent) => {
      if (!isDraggingRef.current) return;
      const deltaX = event.clientX - previousMousePositionRef.current.x;
      const deltaY = event.clientY - previousMousePositionRef.current.y;

      cameraRotationRef.current.theta -= deltaX * 0.006;
      cameraRotationRef.current.phi = Math.max(
        Math.PI / 12,
        Math.min(Math.PI / 2.2, cameraRotationRef.current.phi - deltaY * 0.006)
      );

      updateCameraPos();
      previousMousePositionRef.current = { x: event.clientX, y: event.clientY };
    };

    const handleClick = () => {
      if (hoveredAgent && onSelectAgent) {
        onSelectAgent(hoveredAgent);
      }
    };

    const handleWheel = (event: WheelEvent) => {
      event.preventDefault();
      cameraRotationRef.current.radius = Math.max(15, Math.min(65, cameraRotationRef.current.radius + event.deltaY * 0.03));
      updateCameraPos();
    };

    container.addEventListener('mousemove', handleMouseMove);
    container.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);
    container.addEventListener('mousemove', handleMouseDrag);
    container.addEventListener('click', handleClick);
    container.addEventListener('wheel', handleWheel, { passive: false });

    // -------------------------------------------------------------
    // ANIMATION LOOP
    // -------------------------------------------------------------
    let animationFrameId: number;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      // Rotate Central Core Rings & Mesh
      if (coreMeshRef.current) {
        coreMeshRef.current.rotation.y += 0.008;
      }
      if (ring1Ref.current) {
        ring1Ref.current.rotation.z += 0.012;
      }
      if (ring2Ref.current) {
        ring2Ref.current.rotation.x += 0.015;
      }
      if (ring3Ref.current) {
        ring3Ref.current.rotation.y -= 0.01;
      }
      if (fusionRingRef.current) {
        fusionRingRef.current.rotation.z += 0.003;
      }

      // Animate Rising Core Particles
      if (particlesRef.current) {
        const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;
        for (let i = 0; i < particleCount; i++) {
          positions[i * 3 + 1] += 0.02;
          if (positions[i * 3 + 1] > 6.5) {
            positions[i * 3 + 1] = 0;
          }
        }
        particlesRef.current.geometry.attributes.position.needsUpdate = true;
      }

      // Animate Moving Data Stream Packets
      streamParticlesRef.current.forEach((item) => {
        item.progress = (item.progress + item.speed) % 1.0;
        const pt = item.path.getPointAt(item.progress);
        item.mesh.position.set(pt.x, pt.y, pt.z);
      });

      // Animate Agent Buildings subtle bobbing/glow & selected state
      agentMeshesRef.current.forEach((group, id) => {
        const isSelected = selectedAgentId === id;
        const time = Date.now() * 0.003;
        const targetY = (Math.sin(time + group.position.x) * 0.08) + (isSelected ? 0.35 : 0);
        group.position.y += (targetY - group.position.y) * 0.1;

        // Animate asset sub-props (radar dish, holo ring, tx ring, avatar)
        const userData = (group as any).userData;
        if (userData?.radarDish) userData.radarDish.rotation.y += 0.02;
        if (userData?.holoRing) userData.holoRing.rotation.z += 0.015;
        if (userData?.txRing) userData.txRing.rotation.x += 0.02;
        if (userData?.avatar) userData.avatar.position.y = 2.3 + Math.sin(Date.now() * 0.004) * 0.08;
      });

      // Smooth camera radius lerp towards target framing
      cameraRotationRef.current.radius += (targetRadiusRef.current - cameraRotationRef.current.radius) * 0.1;

      // Smooth camera interpolation towards target LookAt
      if (cameraRef.current) {
        const target = cameraTargetLookAtRef.current;
        const currentLookAt = (cameraRef.current as any).userData?.lookAt || new THREE.Vector3(0, 1, 0);
        currentLookAt.lerp(target, 0.08);
        (cameraRef.current as any).userData = { lookAt: currentLookAt };

        const { theta, phi, radius } = cameraRotationRef.current;
        cameraRef.current.position.x = currentLookAt.x + radius * Math.sin(phi) * Math.cos(theta);
        cameraRef.current.position.y = currentLookAt.y + radius * Math.cos(phi);
        cameraRef.current.position.z = currentLookAt.z + radius * Math.sin(phi) * Math.sin(theta);
        cameraRef.current.lookAt(currentLookAt);
      }

      renderer.render(scene, camera);
    };

    animate();

    // Clean up
    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener('mousemove', handleMouseMove);
      container.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
      container.removeEventListener('mousemove', handleMouseDrag);
      container.removeEventListener('click', handleClick);
      container.removeEventListener('wheel', handleWheel);

      if (rendererRef.current && rendererRef.current.domElement) {
        container.removeChild(rendererRef.current.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // -------------------------------------------------------------
  // RESIZEOBSERVER FOR DYNAMIC CONTAINER RESIZING (SIDEBAR TOGGLE & WINDOW RESIZE)
  // -------------------------------------------------------------
  useEffect(() => {
    if (!mountRef.current) return;
    const container = mountRef.current;

    const handleContainerResize = () => {
      if (!container || !cameraRef.current || !rendererRef.current) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w === 0 || h === 0) return;

      rendererRef.current.setSize(w, h, false);
      fitIsometricScene();
    };

    const resizeObserver = new ResizeObserver(() => {
      handleContainerResize();
    });

    resizeObserver.observe(container);
    handleContainerResize();

    return () => {
      resizeObserver.disconnect();
    };
  }, [cameraPreset]);

  // Update decision color and active glow state
  useEffect(() => {
    if (!coreMeshRef.current) return;
    const color = getDecisionColorHex(selectedDecision);
    (coreMeshRef.current.material as THREE.MeshStandardMaterial).color.set(color);
    (coreMeshRef.current.material as THREE.MeshStandardMaterial).emissive.set(color);
  }, [selectedDecision]);

  // Focus Camera and Tube Line Glow on Selected Agent
  useEffect(() => {
    if (!selectedAgentId) {
      cameraTargetLookAtRef.current.set(0, 1, 0);
      tubeMeshesRef.current.forEach((mesh) => {
        (mesh.material as THREE.MeshBasicMaterial).opacity = 0.4;
      });
      fitIsometricScene();
      return;
    }

    const agent = agentsData.find((a) => a.id === selectedAgentId);
    if (agent) {
      const [ax, ay, az] = agent.position;
      cameraTargetLookAtRef.current.set(ax * 0.35, 1, az * 0.35);

      tubeMeshesRef.current.forEach((mesh, id) => {
        if (id === selectedAgentId) {
          (mesh.material as THREE.MeshBasicMaterial).opacity = 0.9;
          (mesh.material as THREE.MeshBasicMaterial).color.set(agent.color);
        } else {
          (mesh.material as THREE.MeshBasicMaterial).opacity = 0.2;
        }
      });
      fitIsometricScene();
    }
  }, [selectedAgentId, agentsData]);

  // Handle Preset Camera Changes
  useEffect(() => {
    if (!cameraRef.current) return;
    if (cameraPreset === 'ISO_45') {
      cameraRotationRef.current.theta = Math.PI / 4;
      cameraRotationRef.current.phi = Math.PI / 4.5;
    } else if (cameraPreset === 'TOP_DOWN') {
      cameraRotationRef.current.theta = 0;
      cameraRotationRef.current.phi = 0.05;
    } else if (cameraPreset === 'FRONT') {
      cameraRotationRef.current.theta = Math.PI / 2;
      cameraRotationRef.current.phi = Math.PI / 3;
    }
    fitIsometricScene();
  }, [cameraPreset]);

  return (
    <div
      ref={mountRef}
      className="w-full h-full min-w-0 min-h-0 relative overflow-hidden select-none cursor-grab"
    >
      {/* Floating Holographic Tooltip Card on Agent Hover */}
      {hoveredAgent && (
        <div
          className="absolute z-20 pointer-events-none p-3.5 rounded-xl bg-[#091120]/95 border border-cyan-500/40 shadow-2xl shadow-cyan-500/20 backdrop-blur-md max-w-xs transition-all transform -translate-x-1/2 -translate-y-full mb-3 animate-in fade-in zoom-in-95 duration-150"
          style={{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y - 12}px` }}
        >
          <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-2 mb-2">
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full animate-ping"
                style={{ backgroundColor: hoveredAgent.color }}
              />
              <span className="font-bold text-xs text-white uppercase tracking-wider">
                {hoveredAgent.name}
              </span>
            </div>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-cyan-950 text-cyan-400 border border-cyan-800 uppercase">
              {hoveredAgent.status}
            </span>
          </div>

          <p className="text-[11px] text-slate-300 mb-2 leading-tight">{hoveredAgent.description}</p>

          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono bg-[#050914] p-2 rounded-lg border border-slate-800/80">
            <div>
              <span className="text-slate-400 block">THROUGHPUT</span>
              <span className="text-cyan-400 font-bold">{hoveredAgent.eventsPerSec} ev/sec</span>
            </div>
            <div>
              <span className="text-slate-400 block">RISK SCORE</span>
              <span className={hoveredAgent.riskScore > 60 ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold'}>
                {hoveredAgent.riskScore}/100
              </span>
            </div>
            <div>
              <span className="text-slate-400 block">CONFIDENCE</span>
              <span className="text-white font-bold">{hoveredAgent.confidence}%</span>
            </div>
            <div>
              <span className="text-slate-400 block">MODEL</span>
              <span className="text-purple-400 font-semibold">{hoveredAgent.modelVersion}</span>
            </div>
          </div>
        </div>
      )}

      {/* Hover Tooltip for Peripheral Nodes */}
      {hoveredNode && !hoveredAgent && (
        <div
          className="absolute z-20 pointer-events-none p-2.5 rounded-lg bg-[#0a0f1d]/90 border border-slate-700 shadow-xl backdrop-blur-md transition-all text-xs font-mono transform -translate-x-1/2 -translate-y-full mb-2"
          style={{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y - 8}px` }}
        >
          <div className="text-cyan-400 font-bold">{hoveredNode.name}</div>
          <div className="text-slate-400 text-[10px]">Type: {hoveredNode.type} ● Active Telemetry Stream</div>
        </div>
      )}
    </div>
  );
};
