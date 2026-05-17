import type { Message } from '../App';

interface Props {
  message: Message;
}

export default function MessageBubble({ message }: Props) {
  const roleLabels: Record<string, string> = {
    user: 'You',
    assistant: 'GatherAgent',
    tool: 'Tool Result',
    system: 'System',
    thinking: 'Thinking',
  };

  return (
    <div className={`message ${message.role}`}>
      <div className="message-role">{roleLabels[message.role] || message.role}</div>
      <div className="message-content">
        {message.role === 'assistant' ? (
          <MarkdownContent content={message.content} />
        ) : message.role === 'tool' ? (
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 12 }}>
            {message.content.length > 500
              ? message.content.slice(0, 500) + '...'
              : message.content}
          </pre>
        ) : (
          message.content
        )}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div style={{ marginTop: 8 }}>
            {message.tool_calls.map((tc, i) => (
              <div key={i} className="tool-card">
                <div className="tool-card-header">
                  <span>{tc.name}</span>
                </div>
                <div className="tool-card-body">
                  {tc.arguments.length > 200
                    ? tc.arguments.slice(0, 200) + '...'
                    : tc.arguments}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/** Simple markdown-like rendering for assistant messages */
function MarkdownContent({ content }: { content: string }) {
  const parts = content.split(/(```[\s\S]*?```)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('```') && part.endsWith('```')) {
          const lines = part.slice(3, -3).split('\n');
          const lang = lines[0]?.trim() || '';
          const code = lines.slice(lang ? 1 : 0).join('\n');
          return (
            <pre key={i} style={{ position: 'relative' }}>
              <button
                className="copy-btn"
                onClick={() => navigator.clipboard.writeText(code)}
              >
                Copy
              </button>
              <code>{code}</code>
            </pre>
          );
        }
        // Inline code
        const inlineParts = part.split(/(`[^`]+`)/g);
        return (
          <span key={i}>
            {inlineParts.map((p, j) =>
              p.startsWith('`') && p.endsWith('`') ? (
                <code key={j}>{p.slice(1, -1)}</code>
              ) : (
                <span key={j} style={{ whiteSpace: 'pre-wrap' }}>{p}</span>
              )
            )}
          </span>
        );
      })}
    </>
  );
}
