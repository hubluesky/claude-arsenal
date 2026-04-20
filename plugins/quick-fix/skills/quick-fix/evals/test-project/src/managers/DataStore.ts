export class DataStore {
  private data: Map<string, unknown> = new Map();
  private isDirty: boolean = false;

  set(key: string, value: unknown) {
    this.data.set(key, value);
    this.isDirty = true;
  }

  get(key: string): unknown {
    return this.data.get(key);
  }

  async save(): Promise<void> {
    if (!this.isDirty) return;

    const payload = Object.fromEntries(this.data);
    const response = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Save failed: ${response.status}`);
    }

    this.isDirty = false;
  }
}
