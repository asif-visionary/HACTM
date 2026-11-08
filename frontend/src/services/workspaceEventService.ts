/**
 * Resilient Real-Time Event Stream Service for HACTM Cyber Operations Workspace.
 * Manages Server-Sent Events (SSE) connection, auto-reconnection with backoff,
 * event deduplication, and subscriber dispatching.
 */

import { WorkspaceEvent } from '../types/workspace';

export type StreamConnectionStatus = 'CONNECTING' | 'CONNECTED' | 'RECONNECTING' | 'DISCONNECTED';

type EventListener = (event: WorkspaceEvent) => void;
type StatusListener = (status: StreamConnectionStatus) => void;

class WorkspaceEventService {
  private eventSource: EventSource | null = null;
  private eventListeners: Set<EventListener> = new Set();
  private statusListeners: Set<StatusListener> = new Set();
  private processedEventIds: Set<string> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private baseBackoffMs = 1500;
  private maxBackoffMs = 15000;
  private reconnectTimeoutId: any = null;
  private status: StreamConnectionStatus = 'DISCONNECTED';
  private streamUrl = '/api/v1/workspace/stream';

  constructor() {
    // Service initialized
  }

  public getStatus(): StreamConnectionStatus {
    return this.status;
  }

  private setStatus(newStatus: StreamConnectionStatus) {
    if (this.status !== newStatus) {
      this.status = newStatus;
      this.statusListeners.forEach((listener) => {
        try {
          listener(newStatus);
        } catch (e) {
          console.error('Error in status listener:', e);
        }
      });
    }
  }

  public connect(): void {
    if (this.eventSource && (this.eventSource.readyState === EventSource.OPEN || this.eventSource.readyState === EventSource.CONNECTING)) {
      return;
    }

    this.setStatus('CONNECTING');
    try {
      this.eventSource = new EventSource(this.streamUrl);

      this.eventSource.onopen = () => {
        this.reconnectAttempts = 0;
        this.setStatus('CONNECTED');
      };

      this.eventSource.onmessage = (event: MessageEvent) => {
        try {
          if (!event.data) return;
          const parsed = JSON.parse(event.data) as WorkspaceEvent;
          this.handleIncomingEvent(parsed);
        } catch (err) {
          console.warn('Failed to parse SSE payload:', event.data, err);
        }
      };

      this.eventSource.onerror = (err) => {
        console.warn('SSE stream error, initiating reconnection:', err);
        this.eventSource?.close();
        this.eventSource = null;
        this.scheduleReconnect();
      };
    } catch (e) {
      console.error('Failed to initialize EventSource:', e);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
    }

    this.setStatus('RECONNECTING');
    const delay = Math.min(
      this.baseBackoffMs * Math.pow(1.5, this.reconnectAttempts),
      this.maxBackoffMs
    );
    this.reconnectAttempts++;

    this.reconnectTimeoutId = setTimeout(() => {
      this.connect();
    }, delay);
  }

  public disconnect(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.setStatus('DISCONNECTED');
  }

  public onEvent(listener: EventListener): () => void {
    this.eventListeners.add(listener);
    return () => {
      this.eventListeners.delete(listener);
    };
  }

  public onStatusChange(listener: StatusListener): () => void {
    this.statusListeners.add(listener);
    listener(this.status);
    return () => {
      this.statusListeners.delete(listener);
    };
  }

  public handleIncomingEvent(event: WorkspaceEvent): void {
    if (event.event_type === 'heartbeat') return;

    // Deduplication check
    if (event.event_id) {
      if (this.processedEventIds.has(event.event_id)) {
        return;
      }
      this.processedEventIds.add(event.event_id);
      if (this.processedEventIds.size > 500) {
        const oldest = Array.from(this.processedEventIds).slice(0, 100);
        oldest.forEach((id) => this.processedEventIds.delete(id));
      }
    }

    // Broadcast to listeners
    this.eventListeners.forEach((listener) => {
      try {
        listener(event);
      } catch (e) {
        console.error('Error dispatching workspace event:', e);
      }
    });
  }
}

export const workspaceEventService = new WorkspaceEventService();

