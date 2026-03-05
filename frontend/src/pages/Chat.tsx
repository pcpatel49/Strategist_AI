import { useState, useRef, useEffect } from 'react';
import { api } from '../api';
import { Send, User, Bot } from 'lucide-react';
import type { ChatMessage } from '../types';

export const Chat = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Load history
        api.get<ChatMessage[]>('/api/chat/history').then(res => {
            setMessages(res.data.reverse()); // Assuming backend orders latest first
        });
    }, []);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input;
        setInput('');
        setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: userMessage, created_at: new Date().toISOString() }]);
        setIsTyping(true);

        try {
            const res = await api.post('/api/chat', { content: userMessage });
            // Map backend { answer, message_id } to frontend ChatMessage structure
            const assistantMsg: ChatMessage = {
                id: res.data.message_id || Date.now(),
                role: 'assistant',
                content: res.data.answer || '',
                created_at: new Date().toISOString()
            };
            setMessages(prev => [...prev.filter(m => m !== undefined), assistantMsg]);
        } catch (e) {
            console.error("Chat error", e);
            setMessages(prev => [...prev.filter(m => m !== undefined), {
                id: Date.now(),
                role: 'assistant',
                content: "Sorry, I'm having trouble connecting to my systems right now.",
                created_at: new Date().toISOString()
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="h-[calc(100vh-6rem)] flex flex-col bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                <h2 className="text-lg font-bold text-gray-900 flex items-center">
                    <Bot className="text-indigo-600 mr-2" size={24} />
                    AI Admissions Advisor
                </h2>
                <p className="text-xs text-gray-500 mt-1">Context-aware agent with RAG document access</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-4">
                        <Bot size={48} className="text-indigo-200" />
                        <p>Ask me about your courses, milestones, or university requirements.</p>
                    </div>
                )}

                {messages.map((m, idx) => {
                    if (!m) return null;
                    return (
                        <div key={m.id || idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex items-end space-x-2 max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${m.role === 'user' ? 'bg-indigo-600' : 'bg-emerald-500'}`}>
                                    {m.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                                </div>

                                <div className={`px-5 py-3.5 rounded-2xl shadow-sm text-[15px] leading-relaxed whitespace-pre-wrap ${m.role === 'user'
                                    ? 'bg-indigo-600 text-white rounded-br-sm'
                                    : 'bg-gray-100 text-gray-800 rounded-bl-sm'
                                    }`}>
                                    {m.content}
                                </div>
                            </div>
                        </div>
                    );
                })}

                {isTyping && (
                    <div className="flex justify-start">
                        <div className="flex items-end space-x-2 max-w-[80%]">
                            <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0">
                                <Bot size={16} className="text-white" />
                            </div>
                            <div className="px-5 py-4 rounded-2xl bg-gray-100 rounded-bl-sm flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="p-4 bg-white border-t border-gray-100">
                <form onSubmit={handleSend} className="relative flex items-center">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        disabled={isTyping}
                        className="w-full pl-6 pr-14 py-4 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:border-indigo-500 focus:bg-white transition-all focus:ring-4 focus:ring-indigo-500/10"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isTyping}
                        className="absolute right-2 p-2.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors shadow-sm"
                    >
                        <Send size={18} className="translate-x-[1px] translate-y-[-1px]" />
                    </button>
                </form>
            </div>
        </div>
    );
};
