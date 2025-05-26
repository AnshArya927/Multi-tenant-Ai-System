import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import chatbot from "./components/chatbot";              
import AgentChatbot from "./components/AgentChatbot";
import RegisterCompany from "./components/RegisterCompany";
import faq from "./components/faq";                        
import CustomerChat from "./components/CustomerChat";
import TicketForm from "./components/TicketForm";         

export default function App() {
  return (
    <Router>
      <div className="p-4">
        <nav className="mb-4 space-x-4">
          <Link to="/">User Chat</Link>
          <Link to="/agent">Agent Chat</Link>
          <Link to="/register">Register Company</Link>
          <Link to="/upload">Upload Docs</Link>
          <Link to="/ticket">Create Ticket</Link>
          <Link to="/customer-chat">Customer Chat</Link>
        </nav>
        <Routes>
          <Route path="/" element={<chatbot />} />
          <Route path="/agent" element={<AgentChatbot />} />
          <Route path="/register" element={<RegisterCompany />} />
          <Route path="/faq" element={<faq />} />
          <Route path="/customer-chat" element={<CustomerChat />} />
          <Route path="/ticket" element={<TicketForm />} />  {/* use TicketForm here */}
        </Routes>
      </div>
    </Router>
  );
}
