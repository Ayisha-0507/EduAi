import { useState } from "react";

export default function FeedbackButton() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);

  const handleSend = () => {
    // TODO: Integrate with backend or email service
    setSent(true);
    setTimeout(() => {
      setOpen(false);
      setSent(false);
      setMessage("");
    }, 2000);
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-50 bg-accent-green text-white rounded-full shadow-lg px-4 py-2 text-sm font-semibold hover:bg-accent-blue transition"
        aria-label="Send feedback"
      >
        💬 Feedback
      </button>
      {open && (
        <div className="fixed bottom-20 right-6 z-50 bg-bg-primary border border-border-default rounded-lg shadow-xl p-4 w-80">
          <h3 className="font-bold mb-2">Send Feedback</h3>
          <textarea
            className="w-full border border-border-default rounded p-2 mb-2"
            rows={3}
            value={message}
            onChange={e => setMessage(e.target.value)}
            placeholder="Your feedback or suggestion..."
          />
          <div className="flex justify-end gap-2">
            <button onClick={() => setOpen(false)} className="px-2 py-1 text-sm">Cancel</button>
            <button
              onClick={handleSend}
              className="bg-accent-green text-white px-3 py-1 rounded text-sm font-semibold hover:bg-accent-blue transition"
              disabled={!message.trim() || sent}
            >
              {sent ? "Sent!" : "Send"}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
