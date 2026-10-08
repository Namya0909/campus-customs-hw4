import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import { ApiError, fetchChatHistory, imageUrl, sendChatMessage } from "../api";
import { useAuth } from "../context/AuthContext";
import { usePageContext } from "../context/PageContextProvider";
import type { ChatMessage, ProductCard } from "../types";
import "./ChatWidget.css";

interface DisplayMessage extends ChatMessage {
  id: number;
  products?: ProductCard[];
}

const GREETING = "Hi! I'm the Campus Customs assistant. Ask me about sizing, colors, or what's in stock.";

function greetingMessage(): DisplayMessage {
  return { id: 0, role: "assistant", content: GREETING };
}

export default function ChatWidget() {
  const { user } = useAuth();
  const { activeProduct } = usePageContext();
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [messages, setMessages] = useState<DisplayMessage[]>([greetingMessage()]);
  const [unreadCount, setUnreadCount] = useState(0);
  const messagesRef = useRef<HTMLDivElement>(null);
  const isOpenRef = useRef(isOpen);

  // handleSubmit's async continuation closes over isOpen as it was when the request started;
  // this ref tracks the live value so a reply that arrives after the panel was closed (e.g. the
  // customer sent a question, then closed the panel before it replied) is still detected as "the
  // panel is closed right now" and counted as unread.
  useEffect(() => {
    isOpenRef.current = isOpen;
  }, [isOpen]);

  // Auto-scroll to the newest message whenever the conversation changes or the panel opens.
  useEffect(() => {
    if (isOpen) {
      messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, isSending, isOpen]);

  function openPanel() {
    setIsOpen(true);
    setUnreadCount(0);
  }

  // Reload saved history when a customer logs in; reset to a fresh greeting on logout so the
  // next guest (or a different account) never sees someone else's conversation.
  useEffect(() => {
    if (!user) {
      setMessages([greetingMessage()]);
      return;
    }
    let cancelled = false;
    fetchChatHistory().then((entries) => {
      if (cancelled || entries.length === 0) return;
      setMessages(entries.map((entry, i) => ({ id: i, ...entry })));
    });
    return () => {
      cancelled = true;
    };
  }, [user?.id]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || isSending) return;

    const history: ChatMessage[] = messages.map(({ role, content }) => ({ role, content }));
    setMessages((prev) => [...prev, { id: Date.now(), role: "user", content: text }]);
    setDraft("");
    setIsSending(true);

    try {
      const reply = await sendChatMessage(text, history, activeProduct);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "assistant", content: reply.message, products: reply.products },
      ]);
      if (!isOpenRef.current) setUnreadCount((n) => n + 1);
    } catch (err) {
      const content =
        err instanceof ApiError ? err.message : "Something went wrong reaching the assistant. Please try again.";
      setMessages((prev) => [...prev, { id: Date.now() + 1, role: "assistant", content }]);
      if (!isOpenRef.current) setUnreadCount((n) => n + 1);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="chat-widget">
      <div className={"chat-panel" + (isOpen ? " chat-panel-open" : "")} aria-hidden={!isOpen}>
        <div className="chat-header">
          <span className="chat-avatar" aria-hidden="true">
            🎓
          </span>
          <div className="chat-header-text">
            <span className="chat-header-title">Campus Customs Concierge</span>
            <span className="chat-header-subtitle">Usually replies in a few seconds</span>
          </div>
          <button className="chat-close" onClick={() => setIsOpen(false)} aria-label="Close chat" tabIndex={isOpen ? 0 : -1}>
            ×
          </button>
        </div>

        <div className="chat-messages" ref={messagesRef}>
          {messages.map((m) => (
            <div key={m.id} className="chat-turn">
              <div className={`chat-bubble ${m.role}`}>{m.content}</div>
              {m.products && m.products.length > 0 && (
                <div className="chat-products">
                  {m.products.map((p) => (
                    <Link
                      to={`/products/${p.product_id}`}
                      key={p.product_id}
                      className="chat-product-card"
                      tabIndex={isOpen ? 0 : -1}
                    >
                      <img src={imageUrl(p.image_url)} alt={p.name} />
                      <div className="chat-product-info">
                        <span className="chat-product-name">{p.name}</span>
                        <span className="chat-product-type">{p.garment_type}</span>
                        <div className="chat-product-tags">
                          <span className="price-tag">${p.price.toFixed(2)}</span>
                          <span className={"stock-pill" + (p.in_stock ? "" : " out")}>
                            {p.in_stock ? "In stock" : "Out of stock"}
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
          {isSending && (
            <div className="chat-bubble assistant chat-typing" aria-label="Assistant is typing">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          )}
        </div>

        <form className="chat-input-row" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Ask about a product…"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            tabIndex={isOpen ? 0 : -1}
          />
          <button type="submit" disabled={isSending || !draft.trim()} tabIndex={isOpen ? 0 : -1}>
            Send
          </button>
        </form>
      </div>

      <button
        className="chat-toggle"
        onClick={() => (isOpen ? setIsOpen(false) : openPanel())}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? "×" : "💬"}
        {!isOpen && unreadCount > 0 && <span className="chat-unread-badge">{unreadCount}</span>}
      </button>
    </div>
  );
}
