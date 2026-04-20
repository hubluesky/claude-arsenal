import { DataStore } from '../managers/DataStore';

export class SaveButton {
  private button: HTMLButtonElement;
  private dataStore: DataStore;
  private isSaving: boolean = false;

  constructor(buttonEl: HTMLButtonElement, dataStore: DataStore) {
    this.button = buttonEl;
    this.dataStore = dataStore;
    this.bindEvents();
  }

  private bindEvents() {
    // Bug: addEventListener uses wrong event type 'onclick' instead of 'click'
    this.button.addEventListener('onclick', this.handleSave.bind(this));
  }

  private async handleSave() {
    if (this.isSaving) return;
    this.isSaving = true;
    this.button.disabled = true;

    try {
      await this.dataStore.save();
      this.showSuccess();
    } catch (e) {
      this.showError(e as Error);
    } finally {
      this.isSaving = false;
      this.button.disabled = false;
    }
  }

  private showSuccess() {
    this.button.textContent = 'Saved!';
    setTimeout(() => {
      this.button.textContent = 'Save';
    }, 2000);
  }

  private showError(error: Error) {
    console.error('Save failed:', error);
    this.button.textContent = 'Save Failed';
    setTimeout(() => {
      this.button.textContent = 'Save';
    }, 3000);
  }
}
