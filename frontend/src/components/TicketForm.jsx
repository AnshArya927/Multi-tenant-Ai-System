import React, { useState } from "react";

export default function TicketForm() {
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    // Later, replace this with actual POST request to backend
    console.log({
      email,
      subject,
      description,
    });

    setSuccess(true);
    setEmail("");
    setSubject("");
    setDescription("");
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded shadow bg-white">
      <h2 className="text-xl font-bold mb-4 text-center text-red-600">
        Raise a Support Ticket
      </h2>
      {success && (
        <div className="mb-4 text-green-600 font-semibold">
          Ticket submitted! Support will contact you shortly.
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          required
          placeholder="Your Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border p-2 rounded"
        />
        <input
          type="text"
          required
          placeholder="Issue Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="w-full border p-2 rounded"
        />
        <textarea
          required
          placeholder="Describe your issue..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full border p-2 rounded h-28"
        />
        <button
          type="submit"
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Submit Ticket
        </button>
      </form>
    </div>
  );
}
