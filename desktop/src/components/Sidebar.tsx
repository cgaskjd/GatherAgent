interface Props {
  activeSession?: string;
  onNewSession: () => void;
}

export default function Sidebar({ onNewSession }: Props) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>GatherAgent</h2>
      </div>
      <div className="sidebar-sessions">
        <div className="session-item active">Current Session</div>
      </div>
      <button className="new-session-btn" onClick={onNewSession}>
        + New Session
      </button>
    </div>
  );
}
