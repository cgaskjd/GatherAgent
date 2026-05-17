import { useState, useCallback, useRef, useEffect } from 'react';
import { sendChat, type ChatRequest, type ChatResponse, type ToolCall, healthCheck } from './utils/api';
import MessageBubble from './components/MessageBubble';
import InputBar from './components/InputBar';
import StatusBar from './components/StatusBar';
import Sidebar from './components/Sidebar';
import ModelSelector from './components/ModelSelector';
import SettingsDialog from './components/SettingsDialog';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'tool' | 'system' | 'thinking';
  content: string;
  tool_calls?: ToolCall[];
}

const MODEL_PRESETS = [
  { label: 'GPT-5.5', model_id: 'gpt-5.5', provider: 'openai' },
  { label: 'GPT-5.5 Pro', model_id: 'gpt-5.5-pro', provider: 'openai' },
  { label: 'GPT-5', model_id: 'gpt-5', provider: 'openai' },
  { label: 'GPT-4o', model_id: 'gpt-4o', provider: 'openai' },
  { label: 'o3-mini', model_id: 'o3-mini', provider: 'openai' },
  { label: 'Claude Opus 4.7', model_id: 'claude-opus-4-7-20260424', provider: 'anthropic' },
  { label: 'Claude Sonnet 4.6', model_id: 'claude-sonnet-4-6-20260205', provider: 'anthropic' },
  { label: 'Claude Haiku 4.5', model_id: 'claude-haiku-4-5-20250514', provider: 'anthropic' },
  { label: 'Gemini 2.5 Pro', model_id: 'google/gemini-2.5-pro', provider: 'openrouter' },
  { label: 'Gemini 3 Pro', model_id: 'google/gemini-3-pro', provider: 'openrouter' },
  { label: 'DeepSeek V4 Pro', model_id: 'deepseek/deepseek-v4-pro', provider: 'openrouter' },
  { label: 'DeepSeek R2', model_id: 'deepseek/deepseek-r2', provider: 'openrouter' },
  { label: 'Llama 4 Maverick', model_id: 'meta-llama/llama-4-maverick', provider: 'openrouter' },
  { label: 'Qwen 3 235B', model_id: 'qwen/qwen-3-235b-a22b', provider: 'openrouter' },
  { label: 'Mistral Large 3', model_id: 'mistralai/mistral-large-3', provider: 'openrouter' },
];

const THEMES = ['default', 'catppuccin', 'tokyo_night', 'dracula', 'gruvbox', 'slate'];

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [currentModel, setCurrentModel] = useState('gpt-5.5');
  const [currentProvider, setCurrentProvider] = useState('openai');
  const [customBaseUrl, setCustomBaseUrl] = useState<string | null>(null);
  const [customApiKey, setCustomApiKey] = useState<string | null>(null);
  const [mode, setMode] = useState('agent');
  const [cost, setCost] = useState(0);
  const [turns, setTurns] = useState(0);
  const [theme, setTheme] = useState('default');
  const [showSettings, setShowSettings] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [backendOnline, setBackendOnline] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Check backend health
  useEffect(() => {
    const check = async () => {
      const ok = await healthCheck();
      setBackendOnline(ok);
    };
    check();
    const interval = setInterval(check, 5000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const addMessage = useCallback((role: Message['role'], content: string, tool_calls?: ToolCall[]) => {
    const msg: Message = { id: Date.now().toString() + Math.random(), role, content, tool_calls };
    setMessages(prev => [...prev, msg]);
    return msg;
  }, []);

  const handleSend = useCallback(async (text: string) => {
    if (!text.trim() || isThinking) return;
    addMessage('user', text);
    setIsThinking(true);

    try {
      const req: ChatRequest = {
        message: text,
        session_id: sessionId,
        model: currentModel,
        provider: currentProvider,
        base_url: customBaseUrl || undefined,
        api_key: customApiKey || undefined,
        mode,
      };
      const res: ChatResponse = await sendChat(req);
      addMessage('assistant', res.content, res.tool_calls);
      if (res.session_id) setSessionId(res.session_id);
      setTurns(t => t + 1);
      if (res.usage) {
        const inputCost = res.usage.input_tokens * 0.000005;
        const outputCost = res.usage.output_tokens * 0.000015;
        setCost(c => c + inputCost + outputCost);
      }
    } catch (err: any) {
      addMessage('system', `Error: ${err.message || 'Failed to get response'}`);
    } finally {
      setIsThinking(false);
    }
  }, [isThinking, sessionId, currentModel, currentProvider, customBaseUrl, customApiKey, mode, addMessage]);

  const handleModelChange = useCallback((modelId: string, provider: string) => {
    setCurrentModel(modelId);
    setCurrentProvider(provider);
  }, []);

  const handleNewSession = useCallback(() => {
    setMessages([]);
    setSessionId(undefined);
    setCost(0);
    setTurns(0);
  }, []);

  const cycleTheme = useCallback(() => {
    setTheme(t => {
      const idx = THEMES.indexOf(t);
      return THEMES[(idx + 1) % THEMES.length];
    });
  }, []);

  // Welcome screen when no messages
  const welcome = messages.length === 0 && !isThinking;

  return (
    <div className="app">
      <Sidebar
        activeSession={sessionId}
        onNewSession={handleNewSession}
      />
      <div className="main-area">
        <div className="top-bar">
          <div className="top-bar-left">
            <ModelSelector
              presets={MODEL_PRESETS}
              currentModel={currentModel}
              currentProvider={currentProvider}
              onChange={handleModelChange}
            />
          </div>
          <div className="top-bar-right">
            <button className="icon-btn" onClick={() => setMode(m => {
              const modes = ['plan', 'agent', 'yolo', 'sandbox'];
              return modes[(modes.indexOf(m) + 1) % modes.length];
            })}>
              {mode.toUpperCase()}
            </button>
            <button className="icon-btn" onClick={cycleTheme}>
              Theme
            </button>
            <button className="icon-btn" onClick={() => setShowSettings(true)}>
              Settings
            </button>
          </div>
        </div>

        <div className="chat-panel">
          {welcome ? (
            <div className="welcome">
              <h1>GatherAgent</h1>
              <p>The convergence agent — Start a conversation below. Switch models, set custom APIs, and customize your experience.</p>
              {!backendOnline && (
                <p style={{ color: 'var(--warning)', fontSize: 13 }}>
                  Backend offline — run `gather desktop` to start the Python backend first
                </p>
              )}
            </div>
          ) : (
            messages.map(msg => (
              <MessageBubble key={msg.id} message={msg} />
            ))
          )}
          {isThinking && (
            <div className="thinking-indicator">
              <div className="thinking-dots">
                <span>.</span><span>.</span><span>.</span>
              </div>
              Agent is thinking...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <InputBar onSend={handleSend} disabled={isThinking} />

        <StatusBar
          model={currentModel}
          provider={currentProvider}
          mode={mode}
          cost={cost}
          turns={turns}
          backendOnline={backendOnline}
        />
      </div>

      {showSettings && (
        <SettingsDialog
          currentModel={currentModel}
          currentProvider={currentProvider}
          currentBaseUrl={customBaseUrl}
          onClose={() => setShowSettings(false)}
          onSave={(model, provider, baseUrl, apiKey) => {
            setCurrentModel(model);
            setCurrentProvider(provider);
            setCustomBaseUrl(baseUrl);
            setCustomApiKey(apiKey);
            setShowSettings(false);
          }}
        />
      )}
    </div>
  );
}
