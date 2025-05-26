import React, { useState } from "react";

export default function AgentChatbot() {
  const [ticketID, setTicketID] = useState("");
  const [response, setResponse] = useState("");

  const handleSearch = () => {
    // TODO: Replace with backend call later
    setResponse(`Showing results for Ticket ID: ${ticketID}`);
  };

  return (
    <div className="border p-4 rounded w-96 mx-auto mt-10 shadow-md">
      <h2 className="text-xl font-bold mb-4 text-center">Agent Assistant</h2>
      
      <input
        type="text"
        value={ticketID}
        onChange={(e) => setTicketID(e.target.value)}
        placeholder="Enter Ticket ID"
        className="border p-2 w-full mb-3 rounded"
      />

      <button
        onClick={handleSearch}
        className="bg-green-600 text-white px-4 py-2 rounded w-full hover:bg-green-700"
      >
        Search
      </button>

      {response && (
        <div className="mt-4 p-3 border rounded bg-gray-100 text-sm">
          {response}
        </div>
      )}
    </div>
  );
}
