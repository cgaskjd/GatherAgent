import { useState } from 'react';

interface Props {
  currentModel: string;
  currentProvider: string;
  currentBaseUrl: string | null;
  onClose: () => void;
  onSave: (model: string, provider: string, baseUrl: string | null, apiKey: string | null) => void;
}

export default function SettingsDialog({ currentModel, currentProvider, currentBaseUrl, onClose, onSave }: Props) {
  const [model, setModel] = useState(currentModel);
  const [provider, setProvider] = useState(currentProvider);
  const [baseUrl, setBaseUrl] = useState(currentBaseUrl || '');
  const [apiKey, setApiKey] = useState('');
  const [mode, setMode] = useState('agent');

  const handleSave = () => {
    onSave(model, provider, baseUrl || null, apiKey || null);
  };

  return (
    <div className="settings-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="settings-dialog">
        <h2>Settings</h2>

        <div className="settings-group">
          <h3>Model</h3>
          <div className="settings-row">
            <label>Model</label>
            <input value={model} onChange={e => setModel(e.target.value)} placeholder="e.g. gpt-5.5, claude-opus-4-7" />
          </div>
          <div className="settings-row">
            <label>Provider</label>
            <select value={provider} onChange={e => setProvider(e.target.value)}>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="openrouter">OpenRouter</option>
              <option value="ollama">Ollama</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div className="settings-row">
            <label>Mode</label>
            <select value={mode} onChange={e => setMode(e.target.value)}>
              <option value="plan">Plan (read-only)</option>
              <option value="agent">Agent (approval gate)</option>
              <option value="yolo">YOLO (auto-approve)</option>
              <option value="sandbox">Sandbox (container)</option>
            </select>
          </div>
        </div>

        <div className="settings-group">
          <h3>API Endpoint</h3>
          <div className="settings-row">
            <label>Base URL</label>
            <input value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="Leave empty for default, or set custom URL" />
          </div>
          <div className="settings-row">
            <label>API Key</label>
            <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="Leave empty to use env var / config" />
          </div>
        </div>

        <div className="settings-actions">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  );
}
