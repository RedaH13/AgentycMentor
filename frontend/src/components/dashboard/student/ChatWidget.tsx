'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useChatTutor } from '@/hooks/useChatTutor';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { MessageSquare, X, Send, Bot, History, Plus, MessageCircle } from 'lucide-react';

interface ChatWidgetProps {
    reportSessionId?: string | null;
}

export default function ChatWidget({ reportSessionId }: ChatWidgetProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [inputValue, setInputValue] = useState('');
    const [showHistory, setShowHistory] = useState(false);

    const [includeContext, setIncludeContext] = useState(!!reportSessionId);
    const activeSessionId = includeContext ? (reportSessionId || null) : null;

    const {
        messages, isLoading, historyThreads,
        sendMessage, loadHistoryThreads, loadThreadMessages, startNewChat
    } = useChatTutor(activeSessionId);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!showHistory) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isLoading, showHistory]);

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim()) return;
        sendMessage(inputValue);
        setInputValue('');
    };

    const toggleHistory = () => {
        const nextState = !showHistory;
        setShowHistory(nextState);
        if (nextState) loadHistoryThreads();
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {isOpen && (
                <div className="mb-4 w-96 h-[550px] bg-white rounded-2xl shadow-xl border border-zinc-200 flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 duration-300 font-sans">

                    {/* Header */}
                    <div className="bg-zinc-900 text-white p-4 flex flex-col gap-3 border-b border-zinc-800">
                        <div className="flex justify-between items-center">
                            <h3 className="font-semibold flex items-center gap-2 text-sm tracking-wide">
                                <Bot className="w-5 h-5 text-zinc-300" />
                                AgentycMentor
                            </h3>
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={toggleHistory}
                                    className={`p-1.5 rounded-md transition-colors ${showHistory ? 'bg-zinc-700 text-white' : 'text-zinc-400 hover:text-white hover:bg-zinc-800'}`}
                                    title="Chat History"
                                >
                                    <History className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="text-zinc-400 hover:text-white hover:bg-zinc-800 p-1.5 rounded-md transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        {/* Toggle Context */}
                        {reportSessionId && !showHistory && (
                            <label className="flex items-center text-xs bg-zinc-800/80 p-2 rounded-lg cursor-pointer hover:bg-zinc-700 transition-colors border border-zinc-700/50">
                                <input
                                    type="checkbox"
                                    checked={includeContext}
                                    onChange={(e) => setIncludeContext(e.target.checked)}
                                    className="mr-2.5 rounded-sm bg-zinc-900 border-zinc-600 text-zinc-300 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5"
                                />
                                <span className="text-zinc-300 font-medium">Use current report context</span>
                            </label>
                        )}
                    </div>

                    {/* History View */}
                    {showHistory ? (
                        <div className="flex-1 overflow-y-auto bg-zinc-50 flex flex-col">
                            <div className="p-4 border-b border-zinc-200 bg-white sticky top-0 z-10">
                                <button
                                    onClick={() => {
                                        startNewChat();
                                        setShowHistory(false);
                                    }}
                                    className="w-full flex items-center justify-center gap-2 bg-zinc-900 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-zinc-800 transition-colors"
                                >
                                    <Plus className="w-4 h-4" /> New Conversation
                                </button>
                            </div>
                            <div className="p-2 flex flex-col gap-1">
                                {historyThreads.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center py-10 text-zinc-400 gap-2">
                                        <MessageCircle className="w-8 h-8 opacity-50" />
                                        <p className="text-sm">No chat history found.</p>
                                    </div>
                                ) : (
                                    historyThreads.map((thread) => (
                                        <button
                                            key={thread.ThreadID}
                                            onClick={() => {
                                                loadThreadMessages(thread.ThreadID);
                                                setShowHistory(false);
                                            }}
                                            className="text-left px-4 py-3 bg-white hover:bg-zinc-100 rounded-lg transition-colors border border-zinc-100 hover:border-zinc-300 flex flex-col gap-1.5"
                                        >
                                            <span className="text-sm font-semibold text-zinc-800 truncate flex items-center gap-2">
                                                <MessageSquare className="w-3.5 h-3.5 text-zinc-400" />
                                                {thread.SessionID ? `Context: ${thread.SessionID.slice(0, 8)}...` : "General Chat"}
                                            </span>
                                            <span className="text-xs font-medium text-zinc-500">
                                                {new Date(thread.LastUpdatedAt).toLocaleDateString()} at {new Date(thread.LastUpdatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>
                    ) : (
                        /* Standard Chat Messages View */
                        <>
                            <div className="flex-1 p-4 overflow-y-auto bg-zinc-50/50 flex flex-col gap-4">
                                {messages.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center h-full text-zinc-400 space-y-3">
                                        <Bot className="w-12 h-12 text-zinc-200" />
                                        <p className="text-sm text-center max-w-[80%]">
                                            Hello! Ask me a question about the engineering framework or your evaluations.
                                        </p>
                                    </div>
                                ) : (
                                    messages.map((msg) => (
                                        <div key={msg.id} className={`flex ${msg.sender === 'student' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[85%] px-4 py-3 text-sm shadow-sm ${msg.sender === 'student'
                                                ? 'bg-zinc-900 text-white rounded-2xl rounded-br-sm'
                                                : 'bg-white border border-zinc-200 text-zinc-800 rounded-2xl rounded-bl-sm overflow-hidden'
                                                }`}>

                                                <ReactMarkdown
                                                    remarkPlugins={[remarkMath]}
                                                    rehypePlugins={[rehypeKatex]}
                                                    components={{
                                                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0 leading-relaxed" {...props} />,
                                                        ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2 space-y-1" {...props} />,
                                                        ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2 space-y-1" {...props} />,
                                                        li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                                                        strong: ({ node, ...props }) => <strong className="font-semibold text-zinc-900" {...props} />,
                                                        em: ({ node, ...props }) => <em className="italic" {...props} />,
                                                        hr: ({ node, ...props }) => <hr className="my-3 border-zinc-100" {...props} />,
                                                        code: ({ node, ...props }) => <code className="bg-zinc-100 text-zinc-800 px-1 py-0.5 rounded text-xs font-mono" {...props} />
                                                    }}
                                                >
                                                    {msg.text}
                                                </ReactMarkdown>

                                            </div>
                                        </div>
                                    ))
                                )}

                                {isLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-white border border-zinc-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm flex items-center gap-1.5 h-10">
                                            <div className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce"></div>
                                            <div className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                                            <div className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Chat Input */}
                            <form onSubmit={handleSend} className="p-3 bg-white border-t border-zinc-100 flex gap-2">
                                <input
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    placeholder="Type your message..."
                                    className="flex-1 bg-zinc-50 border border-zinc-200 rounded-xl px-4 py-2.5 text-sm text-zinc-800 placeholder:text-zinc-400 focus:outline-none focus:border-zinc-400 focus:ring-1 focus:ring-zinc-400 transition-colors"
                                    disabled={isLoading}
                                />
                                <button
                                    type="submit"
                                    disabled={!inputValue.trim() || isLoading}
                                    className="bg-zinc-900 text-white rounded-xl p-2 w-11 h-11 flex items-center justify-center hover:bg-zinc-800 disabled:bg-zinc-100 disabled:text-zinc-400 disabled:cursor-not-allowed transition-colors border border-transparent disabled:border-zinc-200"
                                >
                                    <Send className="w-4 h-4 ml-0.5" />
                                </button>
                            </form>
                        </>
                    )}
                </div>
            )}

            {/* Floating Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="bg-zinc-900 text-white rounded-full p-4 shadow-lg hover:bg-zinc-800 hover:shadow-xl transition-all transform hover:-translate-y-1 flex items-center gap-2 border border-zinc-800"
                >
                    <MessageSquare className="w-6 h-6" />
                </button>
            )}
        </div>
    );
}