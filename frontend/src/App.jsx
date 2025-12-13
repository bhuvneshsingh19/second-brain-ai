import React, { useState } from 'react';
import { Send, Upload, FileText, Database, AlertCircle } from 'lucide-react';

// --- DYNAMIC API URL CONFIGURATION ---
// If we are on the cloud (Render), use the environment variable.
// If we are on a laptop, default to localhost.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const App = () => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am your Second Brain. Upload documents to train me, or ask me anything.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  // Handle Chat
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // CHANGED: Use dynamic API_URL
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      
      if (!res.ok) throw new Error("Server error");
      
      const data = await res.json();
      
      const aiMsg = { 
        role: 'ai', 
        content: data.reply,
        sources: [...new Set(data.sources)] // Unique sources
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'ai', content: 'Error connecting to brain. Is the backend running?' }]);
    }
    setLoading(false);
  };

  // Handle Upload
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', file.name.endsWith('.pdf') ? 'pdf' : 'text');

    setUploadStatus('Uploading...');
    try {
      // CHANGED: Use dynamic API_URL
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!res.ok) throw new Error("Upload failed");
      
      const data = await res.json();
      setUploadStatus(`Ingestion Started: ${data.message}`);
    } catch (err) {
      console.error(err);
      setUploadStatus('Upload failed. Check backend console.');
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 text-white p-6 flex flex-col">
        <h1 className="text-xl font-bold mb-8 flex items-center gap-2">
          <Database className="w-6 h-6 text-blue-400" /> Second Brain
        </h1>
        
        <div className="mb-8">
          <label className="block text-sm font-semibold mb-2 text-slate-400">Ingest Knowledge</label>
          <label className="flex items-center gap-2 cursor-pointer bg-slate-800 hover:bg-slate-700 p-3 rounded transition">
            <Upload size={18} />
            <span className="text-sm">Upload PDF/Text</span>
            <input type="file" className="hidden" onChange={handleFileUpload} />
          </label>
          {uploadStatus && (
            <p className={`text-xs mt-2 ${uploadStatus.includes('failed') ? 'text-red-400' : 'text-green-400'}`}>
              {uploadStatus}
            </p>
          )}
        </div>

        {/* Deployment Info Helper */}
        <div className="mt-auto text-xs text-slate-500">
           <p>Connected to:</p>
           <code className="bg-slate-800 p-1 rounded mt-1 block truncate">
             {API_URL.replace('https://', '').replace('http://', '')}
           </code>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-8 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl p-4 rounded-lg shadow-sm ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 border'
              }`}>
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500 flex flex-col gap-1">
                    <span className="flex items-center gap-1 font-semibold">
                       <FileText size={12} /> Sources:
                    </span>
                    <div className="flex flex-wrap gap-2">
                        {msg.sources.map((s, i) => (
                            <span key={i} className="bg-gray-100 px-2 py-1 rounded text-gray-600">
                                {s}
                            </span>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
             <div className="flex items-center gap-2 text-gray-400 text-sm ml-4 animate-pulse">
                <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full delay-75"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full delay-150"></div>
                Thinking...
             </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t shadow-sm">
          <form onSubmit={sendMessage} className="max-w-4xl mx-auto flex gap-4">
            <input 
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Ask me about your documents..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button 
                type="submit" 
                disabled={loading || !input.trim()}
                className={`p-3 rounded-lg transition flex items-center justify-center ${
                    loading || !input.trim() 
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
                }`}
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default App;