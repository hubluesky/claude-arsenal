export class SessionManager {
  private currentSession: { id: string; title: string } | null = null;
  private titleUpdateCallback: ((title: string) => void) | null = null;

  async loadSession(sessionId: string) {
    // Simulates async session loading
    const data = await this.fetchSession(sessionId);
    this.currentSession = data;
    // Bug: fires callback before title is set from server response
    // The auto-title feature sets title asynchronously after AI generates it
    if (this.titleUpdateCallback) {
      this.titleUpdateCallback(this.getTitle());
    }
  }

  getTitle(): string {
    // Returns empty string when session is new (before AI generates title)
    // This causes TopBar to show 'New conversation' due to || fallback
    return this.currentSession?.title ?? '';
  }

  setAutoTitle(title: string) {
    if (this.currentSession) {
      this.currentSession.title = title;
      if (this.titleUpdateCallback) {
        this.titleUpdateCallback(title);
      }
    }
  }

  onTitleUpdate(callback: (title: string) => void) {
    this.titleUpdateCallback = callback;
  }

  private async fetchSession(id: string): Promise<{ id: string; title: string }> {
    // Simulate API call
    return { id, title: '' };
  }
}
