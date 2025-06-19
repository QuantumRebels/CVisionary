import React, { useState, useEffect, useRef } from "react";
import { Send, Paperclip } from "lucide-react";
import axios from "axios";

const ChatInterface = ({ onPromptSubmit }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      content:
        "Hi there! I'm CVisionary, your Resume Building AI assistant. Tell me what you'd like me to build for you.",
      isUser: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [placeholder, setPlaceholder] = useState("Type your prompt...");
  const [thinking, setThinking] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null); // ref for file input

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      content: input,
      isUser: true,
    };

    setMessages((prev) => [...prev, userMessage]);
    onPromptSubmit(input);
    setInput("");
    setThinking(true);

    try {
      const response = await axios.post("/api/chat", { message: input });

      const aiReply = {
        id: Date.now() + 1,
        content: response?.data?.reply || "Got it! What should I do next?",
        isUser: false,
      };

      setMessages((prev) => [...prev, aiReply]);
      setPlaceholder(aiReply.content);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          content: "Something went wrong. Try again.",
          isUser: false,
        },
      ]);
    }

    setThinking(false);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Display file name in chat
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        content: `📁 You uploaded: ${file.name}`,
        isUser: true,
      },
    ]);

    // Uncomment to upload to backend
    // const formData = new FormData();
    // formData.append("file", file);
    // try {
    //   const res = await axios.post("/api/upload", formData);
    //   console.log("File uploaded:", res.data);
    // } catch (err) {
    //   console.error("File upload error", err);
    // }

    e.target.value = null; // Clear for next upload
  };

  return (
    <div className="flex flex-col h-full bg-[#0d0b22]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#0d0b22] mt-16">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-sm px-4 py-2 rounded-2xl text-sm ${
                msg.isUser
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-200"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {thinking && (
          <div className="text-gray-400 text-sm">CVisionary is thinking...</div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Field */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-gray-800 bg-[#0d0b22] p-4"
      >
        <div className="flex items-center gap-2 bg-[#0d0b22] px-4 py-3 rounded-xl border border-gray-700 focus-within:border-blue-500">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            className="flex-1 bg-transparent outline-none text-white placeholder-gray-500"
          />

          {/* Hidden File Input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current.click()}
            className="p-1"
            title="Upload file"
          >
            <Paperclip className="w-5 h-5 text-gray-500" />
          </button>

          <button
            type="submit"
            disabled={!input.trim()}
            className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
