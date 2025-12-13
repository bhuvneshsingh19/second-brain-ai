import React, { useState } from 'react';
import { Send, Upload, FileText, Database } from 'lucide-react';

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
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      
      const aiMsg = { 
        role: 'ai', 
        content: data.reply,
        sources: [...new Set(data.sources)] // Unique sources
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Error connecting to brain.' }]);
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
      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setUploadStatus(`Ingestion Started: ${data.message}`);
    } catch (err) {
      setUploadStatus('Upload failed');
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
          {uploadStatus && <p className="text-xs mt-2 text-green-400">{uploadStatus}</p>}
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
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500 flex gap-2">
                    <FileText size={12} />
                    Sources: {msg.sources.join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="text-gray-400 text-sm ml-4">Thinking...</div>}
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t">
          <form onSubmit={sendMessage} className="max-w-4xl mx-auto flex gap-4">
            <input 
              className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ask me about your documents..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button type="submit" className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700">
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default App;