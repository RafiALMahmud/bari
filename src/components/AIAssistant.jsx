import { useState, useRef, useEffect } from "react";
import { aiChat } from "../api";
import "./AIAssistant.css";

const UNIVERSITIES = [
  "", "BRAC University", "North South University", "BUET",
  "Dhaka University", "Jahangirnagar University", "IUT", "AIUB", "AUST",
];

const SUGGESTIONS = [
  "I need a furnished room near BRAC University under ৳10,000",
  "Show me women-only sublets in Dhanmondi",
  "Daily rental near Dhaka airport",
  "Office space in Banani under ৳50,000/month",
];

export default function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm the bari.com AI assistant. Tell me what you're looking for — budget, area, university, or anything else — and I'll find the best matches for you." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ budget_max: "", nearby_university: "", listing_type: "", is_female_only: false });
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  async function send(text) {
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const apiFilters = {
        budget_max: filters.budget_max ? parseFloat(filters.budget_max) : undefined,
        nearby_university: filters.nearby_university || undefined,
        listing_type: filters.listing_type || undefined,
        is_female_only: filters.is_female_only || undefined,
      };
      const allMsgs = [...messages, userMsg];
      const { reply } = await aiChat(allMsgs, apiFilters);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Sorry, I couldn't connect right now. (${err.message})` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    send(input.trim());
  }

  return (
    <>
      <button className="ai-fab" onClick={() => setOpen((p) => !p)} title="AI Property Assistant">
        {open ? "✕" : "✦"}
      </button>

      {open && (
        <div className="ai-panel">
          <div className="ai-header">
            <span className="ai-header-icon">✦</span>
            <div>
              <div className="ai-header-title">AI Property Assistant</div>
              <div className="ai-header-sub">Powered by bari.com</div>
            </div>
            <button className="ai-close" onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className="ai-filters">
            <input
              type="number"
              placeholder="Max budget (৳)"
              value={filters.budget_max}
              onChange={(e) => setFilters((p) => ({ ...p, budget_max: e.target.value }))}
            />
            <select
              value={filters.nearby_university}
              onChange={(e) => setFilters((p) => ({ ...p, nearby_university: e.target.value }))}
            >
              {UNIVERSITIES.map((u) => <option key={u} value={u}>{u || "Any university"}</option>)}
            </select>
            <select
              value={filters.listing_type}
              onChange={(e) => setFilters((p) => ({ ...p, listing_type: e.target.value }))}
            >
              <option value="">Any type</option>
              <option value="rent">Rent</option>
              <option value="sublet">Sublet</option>
              <option value="sale">Sale</option>
            </select>
            <label className="ai-female-check">
              <input
                type="checkbox"
                checked={filters.is_female_only}
                onChange={(e) => setFilters((p) => ({ ...p, is_female_only: e.target.checked }))}
              />
              Women-only
            </label>
          </div>

          <div className="ai-messages">
            {messages.map((m, i) => (
              <div key={i} className={`ai-msg ${m.role}`}>
                {m.role === "assistant" && <span className="ai-msg-icon">✦</span>}
                <div className="ai-msg-bubble">{m.content}</div>
              </div>
            ))}
            {loading && (
              <div className="ai-msg assistant">
                <span className="ai-msg-icon">✦</span>
                <div className="ai-msg-bubble ai-typing"><span /><span /><span /></div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {messages.length === 1 && (
            <div className="ai-suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="ai-suggestion" onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          )}

          <form className="ai-input-row" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe what you're looking for…"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>→</button>
          </form>
        </div>
      )}
    </>
  );
}
