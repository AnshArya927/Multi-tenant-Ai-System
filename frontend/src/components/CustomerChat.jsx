import React, { useState } from "react";

export default function CustomerChat() {
  const [messages, setMessages] = useState([
    { text: "Hi! How can I help you today?", fromUser: false },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = { text: input, fromUser: true };
    setMessages((prev) => [...prev, userMessage]);

    // TODO: Later replace with backend fetch call
    const dummyBotReply = {
      text: "Thanks for your message! (Backend integration coming soon...)",
      fromUser: false,
    };

    setTimeout(() => {
      setMessages((prev) => [...prev, dummyBotReply]);
    }, 600);

    setInput("");
  };

  return (
    <div className="max-w-md mx-auto mt-10 border rounded shadow-md bg-white p-4">
      <h2 className="text-xl font-bold mb-3 text-center text-blue-700">
        Customer Support Chatbot
      </h2>
      <div className="h-64 overflow-y-auto border p-3 rounded bg-gray-50 mb-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-2 ${
              msg.fromUser ? "text-right text-blue-800" : "text-left text-gray-800"
            }`}
          >
            <div
              className={`inline-block px-3 py-1 rounded ${
                msg.fromUser
                  ? "bg-blue-200"
                  : "bg-gray-200"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border p-2 rounded"
          placeholder="Ask your question..."
        />
        <button
          onClick={sendMessage}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}
