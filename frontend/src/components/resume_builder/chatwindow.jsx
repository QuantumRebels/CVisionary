import React, { useState, useEffect, useRef } from "react";
import { Send, Paperclip } from "lucide-react";
import axios from "axios";

const ChatInterface = ({ onPromptSubmit, initialPrompt, darkMode }) => {
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
  const fileInputRef = useRef(null);

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
    if (onPromptSubmit) onPromptSubmit(input);
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

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        content: `📁 You uploaded: ${file.name}`,
        isUser: true,
      },
    ]);
    e.target.value = null;
  };

  const bgClass = darkMode ? "bg-[#0d0b22]" : "bg-white";
  const textClass = darkMode ? "text-white" : "text-gray-900";
  const borderClass = darkMode ? "border-gray-700" : "border-blue-200";
  const inputBg = darkMode
    ? "bg-[#0d0b22] border-gray-700"
    : "bg-blue-100 border-blue-200";
  const inputText = darkMode ? "text-white" : "text-gray-900";
  const placeholderText = darkMode ? "placeholder-gray-500" : "placeholder-gray-400";
  const userMsgBg = darkMode
    ? "bg-blue-600 text-white"
    : "bg-blue-500 text-white";
  const aiMsgBg = darkMode
    ? "bg-gray-800 text-gray-200"
    : "bg-blue-100 text-gray-900";
  const sendBtnBg = darkMode
    ? "bg-blue-600 hover:bg-blue-700"
    : "bg-blue-500 hover:bg-blue-600";
  const disabledBtnBg = darkMode
    ? "bg-gray-600"
    : "bg-gray-300";

  return (
    <div className={`flex flex-col h-full ${bgClass} transition-colors duration-300`}>
      <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${bgClass} mt-16`}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-sm px-4 py-2 rounded-2xl text-sm ${
                msg.isUser ? userMsgBg : aiMsgBg
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
      <form
        onSubmit={handleSubmit}
        className={`border-t ${borderClass} ${bgClass} p-4`}
      >
        <div className={`flex items-center gap-2 ${bgClass} px-4 py-3 rounded-xl border ${borderClass} focus-within:border-blue-500`}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            className={`flex-1 bg-transparent outline-none ${inputText} ${placeholderText}`}
          />

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
            <Paperclip className={`w-5 h-5 ${darkMode ? "text-gray-500" : "text-blue-500"}`} />
          </button>

          <button
            type="submit"
            disabled={!input.trim()}
            className={`p-2 rounded-lg ${sendBtnBg} disabled:${disabledBtnBg}`}
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;