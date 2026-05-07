import { useState } from "react";
import type { FormEvent } from "react";
import { Send } from "lucide-react";
import { api } from "../services/api";

type Message = {
  role: "user" | "bot";
  text: string;
};

export function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      text: "Informe potência do trator, tipo de solo e implemento. Ex.: Tenho trator de 120 hp e solo argiloso. Qual grade usar?",
    },
  ]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const message = String(form.get("message") || "").trim();
    if (!message) return;
    event.currentTarget.reset();
    setMessages((current) => [...current, { role: "user", text: message }]);
    const result = await api.chat(message);
    setMessages((current) => [...current, { role: "bot", text: result.answer }]);
  }

  return (
    <section className="space-y-5">
      <div>
        <p className="text-xs font-bold uppercase text-soil-600">NLP operacional</p>
        <h2 className="text-3xl font-bold">Chatbot técnico</h2>
      </div>
      <div className="panel grid min-h-[560px] grid-rows-[1fr_auto] overflow-hidden">
        <div className="flex flex-col gap-3 overflow-auto p-5">
          {messages.map((message, index) => (
            <div
              className={
                message.role === "user"
                  ? "max-w-3xl self-end rounded-lg bg-soil-600 px-4 py-3 text-white"
                  : "max-w-3xl self-start rounded-lg bg-soil-100 px-4 py-3 text-soil-950"
              }
              key={`${message.role}-${index}`}
            >
              {message.text}
            </div>
          ))}
        </div>
        <form className="grid grid-cols-[1fr_auto] gap-3 border-t border-soil-100 p-4" onSubmit={submit}>
          <input className="input" name="message" placeholder="Digite sua pergunta..." />
          <button className="button" type="submit">
            <Send size={18} />
            Enviar
          </button>
        </form>
      </div>
    </section>
  );
}
