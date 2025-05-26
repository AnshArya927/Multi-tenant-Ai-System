import React, { useState } from "react";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages([...messages, { text: input, fromUser: true }]);
    setInput("");
  };

  return (
    <div className="border p-4 rounded w-80">
      <div className="mb-2 font-bold">Chatbot</div>
      <div className="h-48 overflow-y-auto border mb-2 p-2">
        {messages.map((msg, i) => (
          <div key={i} className={msg.fromUser ? "text-right" : "text-left"}>
            {msg.text}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="border p-1 w-full"
        placeholder="Type your message"
      />
      <button
        onClick={sendMessage}
        className="mt-2 bg-blue-600 text-white px-4 py-1 rounded"
      >
        Send
      </button>
    </div>
  );
}
