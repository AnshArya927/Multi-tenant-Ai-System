import React, { useState } from "react";

export default function UploadFAQs() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = (e) => {
    e.preventDefault();

    if (!file) {
      setMessage("Please select a file first.");
      return;
    }

    // TODO: Connect with backend API later
    setMessage(`File "${file.name}" uploaded successfully!`);
    setFile(null);
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded shadow-md bg-white">
      <h2 className="text-xl font-bold mb-4 text-center">
        Upload Company FAQs/Docs
      </h2>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          onChange={handleFileChange}
          className="w-full p-2 mb-4 border rounded"
          required
        />
        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
        >
          Upload
        </button>
      </form>
      {message && (
        <div className="mt-4 text-blue-600 font-medium text-center">
          {message}
        </div>
      )}
    </div>
  );
}
