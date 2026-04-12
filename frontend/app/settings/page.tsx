import { PreferencesForm } from '@/features/preferences/preferences-form';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">Adjust remembered navigation state.</p>
      </div>
      <PreferencesForm />
    </div>
  );
}
