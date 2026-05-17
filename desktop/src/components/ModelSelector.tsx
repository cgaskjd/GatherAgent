import { useState } from 'react';

interface ModelPreset {
  label: string;
  model_id: string;
  provider: string;
}

interface Props {
  presets: ModelPreset[];
  currentModel: string;
  currentProvider: string;
  onChange: (modelId: string, provider: string) => void;
}

export default function ModelSelector({ presets, currentModel, currentProvider, onChange }: Props) {
  const [customModel, setCustomModel] = useState('');
  const [customProvider, setCustomProvider] = useState('openai');
  const [showCustom, setShowCustom] = useState(false);

  const currentValue = presets.find(p => p.model_id === currentModel)
    ? currentModel
    : '__custom__';

  const handleSelect = (val: string) => {
    if (val === '__custom__') {
      setShowCustom(true);
      return;
    }
    setShowCustom(false);
    const preset = presets.find(p => p.model_id === val);
    if (preset) onChange(preset.model_id, preset.provider);
  };

  const handleCustomSubmit = () => {
    if (customModel.trim()) {
      const provider = customProvider || detectProvider(customModel);
      onChange(customModel.trim(), provider);
      setShowCustom(false);
    }
  };

  return (
    <div className="model-selector">
      <select value={currentValue} onChange={e => handleSelect(e.target.value)}>
        {presets.map(p => (
          <option key={p.model_id} value={p.model_id}>
            {p.label} ({p.provider})
          </option>
        ))}
        <option value="__custom__">Custom...</option>
      </select>
      {showCustom && (
        <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
          <input
            value={customModel}
            onChange={e => setCustomModel(e.target.value)}
            placeholder="model name"
            style={{ width: 140, fontSize: 12, padding: '4px 8px', borderRadius: 4,
                     background: 'var(--bg-primary)', border: '1px solid var(--border)',
                     color: 'var(--text-primary)' }}
            onKeyDown={e => e.key === 'Enter' && handleCustomSubmit()}
          />
          <select
            value={customProvider}
            onChange={e => setCustomProvider(e.target.value)}
            style={{ fontSize: 12, padding: '4px 8px', borderRadius: 4,
                     background: 'var(--bg-primary)', border: '1px solid var(--border)',
                     color: 'var(--text-primary)' }}
          >
            <option value="openai">openai</option>
            <option value="anthropic">anthropic</option>
            <option value="openrouter">openrouter</option>
            <option value="ollama">ollama</option>
          </select>
          <button className="icon-btn" onClick={handleCustomSubmit} style={{ fontSize: 11 }}>
            OK
          </button>
        </div>
      )}
    </div>
  );
}

function detectProvider(model: string): string {
  const m = model.toLowerCase();
  if (m.startsWith('gpt-') || m.startsWith('o1') || m.startsWith('o3')) return 'openai';
  if (m.startsWith('claude-')) return 'anthropic';
  if (m.includes('/')) return 'openrouter';
  if (m.includes(':')) return 'ollama';
  return 'openai';
}
