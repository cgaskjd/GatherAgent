interface Props {
  model: string;
  provider: string;
  mode: string;
  cost: number;
  turns: number;
  backendOnline: boolean;
}

export default function StatusBar({ model, provider, mode, cost, turns, backendOnline }: Props) {
  const costStr = cost < 1 ? `$${cost.toFixed(4)}` : `$${cost.toFixed(2)}`;
  return (
    <div className="status-bar">
      <span>
        {backendOnline ? '●' : '○'} {backendOnline ? 'Online' : 'Offline'}
      </span>
      <span>
        Model: <span className="status-value">{model}</span>
      </span>
      <span>
        Provider: <span className="status-value">{provider}</span>
      </span>
      <span>
        Mode: <span className="status-value">{mode}</span>
      </span>
      <span>
        Turn: <span className="status-value">{turns}</span>
      </span>
      <span>
        Cost: <span className="status-value">{costStr}</span>
      </span>
    </div>
  );
}
