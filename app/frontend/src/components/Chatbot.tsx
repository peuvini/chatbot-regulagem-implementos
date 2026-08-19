import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { History, Leaf, MessageSquareText, Plus, Sprout, UserRound } from "lucide-react";
import { api } from "../services/api";
import type { ChatConversation } from "../types/api";

type Message = { role: "user" | "bot"; text: string };
type Soil = { key: "arenoso" | "argiloso" | "textura-media"; label: string; note: string; color: string };

const openingMessage: Message = {
  role: "bot",
  text: "Informe a potência do trator, o tipo de solo e a operação desejada. Como posso ajudar?",
};

const soils: Soil[] = [
  { key: "arenoso", label: "Solo arenoso", note: "Menor coesão e menor resistência à tração.", color: "#d9ad5a" },
  { key: "argiloso", label: "Solo argiloso", note: "Maior aderência e demanda de tração.", color: "#8e4e32" },
  { key: "textura-media", label: "Textura média", note: "Condição intermediária para regulagem.", color: "#987142" },
];

export function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([openingMessage]);
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [soilIndex, setSoilIndex] = useState(0);
  const messagesPanel = useRef<HTMLDivElement>(null);
  const soil = soils[soilIndex];

  useEffect(() => { loadConversations(); }, []);
  useEffect(() => {
    const panel = messagesPanel.current;
    if (panel) panel.scrollTo({ top: panel.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);
  useEffect(() => {
    const interval = window.setInterval(() => setSoilIndex((current) => (current + 1) % soils.length), 7000);
    return () => window.clearInterval(interval);
  }, []);

  async function loadConversations() {
    const result = await api.chatConversations();
    setConversations(result);
  }

  async function openConversation(conversationId: number) {
    const conversation = await api.chatConversation(conversationId);
    setActiveConversationId(conversation.id);
    setMessages(conversation.messages.map((message) => ({ role: message.role === "user" ? "user" : "bot", text: message.content })));
  }

  function newConversation() {
    setActiveConversationId(null);
    setMessages([openingMessage]);
  }

  async function sendMessage(message: string) {
    if (!message || loading) return;
    setLoading(true);
    setMessages((current) => [...current, { role: "user", text: message }]);
    try {
      const result = await api.chatInConversation(message, activeConversationId);
      setActiveConversationId(result.conversation_id);
      setMessages((current) => [...current, { role: "bot", text: result.answer }]);
      await loadConversations();
    } finally {
      setLoading(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = String(new FormData(event.currentTarget).get("message") || "").trim();
    if (!message || loading) return;
    event.currentTarget.reset();
    await sendMessage(message);
  }

  const suggestions = [
    `Grade para 120 hp em ${soil.label.toLowerCase()}`,
    "Arado para solo seco",
    "Implementos para trator de 90 hp",
  ];

  return (
    <section className="chat-layout grid h-full min-h-0 overflow-hidden rounded-[24px] border border-[#cdbda9] shadow-lg lg:grid-cols-[250px_minmax(0,1fr)]">
      <aside className="hidden min-h-0 flex-col border-r border-[#c2b097] bg-[#d7c8b4] lg:flex">
        <div className="border-b border-[#c2b097] p-4">
          <button className="flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border-0 bg-[#6d513c] px-4 font-semibold text-white transition hover:bg-[#58402f]" onClick={newConversation} type="button"><Plus className="shrink-0" size={17} /><span>Nova consulta</span></button>
        </div>
        <div className="px-5 pb-2 pt-4">
          <p className="flex items-center gap-2 text-xs font-bold uppercase text-base-content/55"><History size={14} /> Histórico</p>
        </div>
        <div className="panel-scroll min-h-0 flex-1 overflow-auto px-3 pb-3">
          <div className="grid gap-1">
            {conversations.map((conversation) => (
              <button className={`conversation-button ${conversation.id === activeConversationId ? "active" : ""}`} key={conversation.id} onClick={() => openConversation(conversation.id)} type="button">
                <MessageSquareText size={16} /><span className="line-clamp-2">{conversation.title}</span>
              </button>
            ))}
            {conversations.length === 0 && <p className="px-3 py-4 text-sm leading-6 text-base-content/55">Suas consultas aparecerão aqui.</p>}
          </div>
        </div>
      </aside>

      <div className="grid min-h-0 min-w-0 grid-rows-[auto_auto_minmax(0,1fr)_auto] bg-[#eee7db]">
        <header className="flex min-h-16 items-center justify-between gap-4 border-b border-[#cdbda9] bg-[#f5efe5] px-4 py-3 md:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#59651f] text-white"><Leaf size={20} /></span>
            <div className="min-w-0">
              <h2 className="truncate text-lg font-bold">Assistente técnico</h2>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <button className="btn btn-ghost btn-circle lg:hidden" aria-label="Nova consulta" onClick={newConversation} title="Nova consulta" type="button"><Plus size={19} /></button>
            <button className="soil-indicator flex min-h-10 items-center gap-2 rounded-full border border-base-300 bg-white px-3 text-left" data-soil={soil.key} onClick={() => setSoilIndex((current) => (current + 1) % soils.length)} title="Alternar condição do solo" type="button">
              <span className="flex h-8 w-8 items-center justify-center rounded-full" style={{ backgroundColor: soil.color }}><Sprout className="text-white" size={16} /></span>
              <strong className="hidden text-xs md:block">{soil.label}</strong>
            </button>
          </div>
        </header>

        <div className="border-b border-[#d7c9b6] bg-[#faf7f0] px-4 py-3 md:px-6">
          <p className="mb-2 text-[11px] font-bold uppercase text-base-content/45">Sugestões</p>
          <div className="suggestion-strip flex gap-2 overflow-x-auto pb-1">
            {suggestions.map((prompt) => (
              <button className="suggestion-chip" disabled={loading} key={prompt} onClick={() => sendMessage(prompt)} type="button">{prompt}</button>
            ))}
          </div>
        </div>

        <div className="chat-messages panel-scroll min-h-0 overflow-auto px-4 py-5 md:px-7" ref={messagesPanel}>
          {messages.map((message, index) => <MessageRow message={message} key={`${message.role}-${index}`} />)}
          {loading && (
            <div className="chat chat-start">
              <div className="chat-image avatar placeholder"><div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#59651f] text-white"><Leaf size={17} /></div></div>
              <div className="chat-header text-xs font-bold text-base-content/55">Assistente ARIPS</div>
              <div className="chat-bubble rounded-2xl bg-white text-base-content shadow-sm"><span className="loading loading-dots loading-sm" /> Consultando parâmetros...</div>
            </div>
          )}
        </div>

        <div className="border-t border-[#cdbda9] bg-[#f5efe5] p-3 md:p-4">
          <form className="flex items-center gap-2 rounded-full border border-[#c8b79f] bg-white px-3 py-2 shadow-sm focus-within:border-[#59651f] focus-within:ring-2 focus-within:ring-[#59651f]/15" onSubmit={submit}>
            <input className="min-h-10 min-w-0 flex-1 bg-transparent px-2 text-sm outline-none placeholder:text-base-content/40" name="message" placeholder="Digite sua dúvida sobre trator, implemento ou solo..." />
            <button className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-0 bg-[#59651f] p-0 text-white transition hover:bg-[#475119] disabled:opacity-60" disabled={loading} aria-label="Enviar pergunta" title="Enviar pergunta" type="submit"><Leaf className="block" size={20} /></button>
          </form>
        </div>
      </div>
    </section>
  );
}

function MessageRow({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={`mb-4 flex items-end ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[84%] items-end gap-2 ${isUser ? "flex-row-reverse" : ""}`}>
        <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${isUser ? "bg-[#d4aa55] text-[#272417]" : "bg-[#59651f] text-white"}`}>
          {isUser ? <UserRound size={17} /> : <Leaf size={17} />}
        </div>
        <div className={`grid gap-1 ${isUser ? "justify-items-end" : "justify-items-start"}`}>
          <div className="text-xs font-bold text-base-content/55">{isUser ? "Você" : "Assistente ARIPS"}</div>
          <div className={`w-fit whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-6 ${isUser ? "rounded-br-md bg-[#59651f] text-white" : "rounded-bl-md bg-white text-base-content shadow-sm"}`}>{message.text}</div>
        </div>
      </div>
    </div>
  );
}
