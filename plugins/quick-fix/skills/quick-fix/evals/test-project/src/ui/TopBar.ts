import { SessionManager } from '../managers/SessionManager';

export class TopBar {
  private titleLabel: HTMLElement;
  private sessionManager: SessionManager;

  constructor(titleEl: HTMLElement, sessionManager: SessionManager) {
    this.titleLabel = titleEl;
    this.sessionManager = sessionManager;
  }

  updateTitle() {
    // Bug: should use sessionManager.getTitle() but falls back to hardcoded string
    // when session title is empty string (not null/undefined)
    const title = this.sessionManager.getTitle() || 'New conversation';
    this.titleLabel.textContent = title;
  }

  onSessionChange(sessionId: string) {
    this.sessionManager.loadSession(sessionId);
    this.updateTitle();
  }
}
