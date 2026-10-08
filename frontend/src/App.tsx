import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from './components/layout/AppLayout';
import { NavigationTab } from './components/layout/Sidebar';
import { CyberTrustOrchestratorDashboard } from './components/dashboard/CyberTrustOrchestratorDashboard';
import { Overview } from './pages/Overview';
import { NetworkSecurity } from './pages/NetworkSecurity';
import { PhishingIntelligence } from './pages/PhishingIntelligence';
import { DeviceSecurity } from './pages/DeviceSecurity';
import { UserBehavior } from './pages/UserBehavior';
import { IdentityAuthentication } from './pages/IdentityAuthentication';
import { TransactionSecurity } from './pages/TransactionSecurity';
import { EvidenceFusion } from './pages/EvidenceFusion';
import { CyberRisk } from './pages/CyberRisk';
import { AdaptiveMemoryPage } from './pages/AdaptiveMemory';
import { AttackEvidenceGraphPage } from './pages/AttackEvidenceGraph';
import { TemporalAnalysisPage } from './pages/TemporalAnalysis';
import { ResearchLabPage } from './pages/ResearchLab';
import { ReliabilityDashboard } from './pages/ReliabilityDashboard';
import { OrchestrationDashboard } from './pages/OrchestrationDashboard';
import { ZeroTrustDashboard } from './pages/ZeroTrustDashboard';
import { FeedbackDashboard } from './pages/FeedbackDashboard';
import { EvaluationDashboard } from './pages/EvaluationDashboard';
import { ResearchDashboard } from './pages/ResearchDashboard';
import { SecurityEvents } from './pages/SecurityEvents';
import { Evidence } from './pages/Evidence';
import { Entities } from './pages/Entities';
import { Agents } from './pages/Agents';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
    },
  },
});

const getTabFromLocation = (): NavigationTab | null => {
  const hash = window.location.hash.replace('#', '').toLowerCase();
  const path = window.location.pathname.replace('/', '').toLowerCase();

  if (hash === '3d-mesh' || hash === '3d' || path === '3d-mesh' || path === '3d') {
    return '3d-mesh';
  }
  if (hash === 'security-events' || hash === 'events' || path === 'security-events' || path === 'events') {
    return 'events';
  }
  if (hash === 'evidence' || hash === 'evidence-explorer' || path === 'evidence' || path === 'evidence-explorer') {
    return 'evidence';
  }

  const validTabs: NavigationTab[] = [
    '3d-mesh', 'overview', 'network', 'phishing', 'device', 'uba', 'identity', 'transaction',
    'evidence-fusion', 'cyber-risk', 'memory', 'graph', 'temporal', 'research-lab',
    'reliability', 'orchestration', 'zero-trust', 'feedback', 'evaluation',
    'research', 'events', 'evidence', 'entities', 'agents', 'reports', 'settings'
  ];

  if (validTabs.includes(hash as NavigationTab)) return hash as NavigationTab;
  if (validTabs.includes(path as NavigationTab)) return path as NavigationTab;

  return null;
};

export function App() {
  const [currentTab, setCurrentTab] = useState<NavigationTab>(() => getTabFromLocation() || '3d-mesh');

  useEffect(() => {
    const handleHashOrPopState = () => {
      const tab = getTabFromLocation();
      if (tab) {
        setCurrentTab(tab);
      }
    };

    window.addEventListener('hashchange', handleHashOrPopState);
    window.addEventListener('popstate', handleHashOrPopState);

    return () => {
      window.removeEventListener('hashchange', handleHashOrPopState);
      window.removeEventListener('popstate', handleHashOrPopState);
    };
  }, []);

  const handleTabChange = (tab: NavigationTab) => {
    setCurrentTab(tab);
    window.location.hash = tab;
  };

  const renderContent = () => {
    switch (currentTab) {
      case '3d-mesh':
        return <CyberTrustOrchestratorDashboard />;
      case 'overview':
        return (
          <Overview
            onNavigateToEvidence={() => handleTabChange('evidence')}
            onNavigateToSettings={() => handleTabChange('settings')}
            onNavigateToDomain={(domain: NavigationTab) => handleTabChange(domain)}
          />
        );
      case 'network':
        return <NetworkSecurity />;
      case 'phishing':
        return <PhishingIntelligence />;
      case 'device':
        return <DeviceSecurity />;
      case 'uba':
        return <UserBehavior />;
      case 'identity':
        return <IdentityAuthentication />;
      case 'transaction':
        return <TransactionSecurity />;
      case 'evidence-fusion':
        return <EvidenceFusion />;
      case 'cyber-risk':
        return <CyberRisk />;
      case 'memory':
        return <AdaptiveMemoryPage />;
      case 'graph':
        return <AttackEvidenceGraphPage />;
      case 'temporal':
        return <TemporalAnalysisPage />;
      case 'research-lab':
        return <ResearchLabPage />;
      case 'reliability':
        return <ReliabilityDashboard />;
      case 'orchestration':
        return <OrchestrationDashboard />;
      case 'zero-trust':
        return <ZeroTrustDashboard />;
      case 'feedback':
        return <FeedbackDashboard />;
      case 'evaluation':
        return <EvaluationDashboard />;
      case 'research':
        return <ResearchDashboard />;
      case 'events':
        return <SecurityEvents />;
      case 'evidence':
        return <Evidence />;
      case 'entities':
        return <Entities />;
      case 'agents':
        return (
          <Agents
            onNavigateToDomain={(domain: NavigationTab) => handleTabChange(domain)}
          />
        );
      case 'reports':
        return <Reports />;
      case 'settings':
        return <Settings />;
      default:
        return (
          <Overview
            onNavigateToEvidence={() => handleTabChange('evidence')}
            onNavigateToSettings={() => handleTabChange('settings')}
            onNavigateToDomain={(domain: NavigationTab) => handleTabChange(domain)}
          />
        );
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <AppLayout currentTab={currentTab} onTabChange={handleTabChange}>
        {renderContent()}
      </AppLayout>
    </QueryClientProvider>
  );
}

export default App;
