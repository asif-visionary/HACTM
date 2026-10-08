import React, { useState } from 'react';
import { TopBar } from './TopBar';
import { Sidebar, NavigationTab } from './Sidebar';

interface AppLayoutProps {
  currentTab: NavigationTab;
  onTabChange: (tab: NavigationTab) => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  currentTab,
  onTabChange,
  children,
}) => {
  const [collapsed, setCollapsed] = useState(false);

  const is3DView = currentTab === '3d-mesh';

  return (
    <div className="h-screen bg-hactm-bg text-hactm-text flex flex-col font-sans overflow-hidden">
      <TopBar />
      <div className="flex flex-1 min-h-0 overflow-hidden">
        <Sidebar
          currentTab={currentTab}
          onTabChange={onTabChange}
          collapsed={collapsed}
          onToggleCollapse={() => setCollapsed(!collapsed)}
        />
        <main
          className={`flex-1 min-w-0 w-full max-w-none focus:outline-none flex flex-col min-h-0 overflow-y-auto overflow-x-hidden ${
            is3DView ? 'p-0' : 'p-4 sm:p-6'
          }`}
          tabIndex={-1}
        >
          <div
            className={`w-full max-w-none min-w-0 flex flex-col flex-1 min-h-0 ${
              is3DView ? '' : 'max-w-[1600px] mx-auto space-y-6'
            }`}
          >
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
