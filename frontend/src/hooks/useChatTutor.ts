import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import api from '@/lib/api';

export interface ChatMessage {
    id: string;
    sender: 'student' | 'tutor_ai';
    text: string;
}

export interface ChatThreadInfo {
    ThreadID: string;
    SessionID: string | null;
    LastUpdatedAt: string;
}

export function useChatTutor(sessionId: string | null = null) {
    const [threadId, setThreadId] = useState<string>(() => uuidv4());
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [historyThreads, setHistoryThreads] = useState<ChatThreadInfo[]>([]);

    const customBaseURL = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';

    // load list threads
    const loadHistoryThreads = useCallback(async () => {
        try {
            const response = await api.get('/chat/threads', { baseURL: customBaseURL });
            setHistoryThreads(response.data.threads);
        } catch (error) {
            console.error("Failed to load history threads:", error);
        }
    }, [customBaseURL]);

    // load msgs d'un thread
    const loadThreadMessages = useCallback(async (selectedThreadId: string) => {
        setIsLoading(true);
        try {
            const response = await api.get(`/chat/threads/${selectedThreadId}/messages`, { baseURL: customBaseURL });

            const loadedMessages: ChatMessage[] = response.data.messages.map((m: any) => ({
                id: uuidv4(),
                sender: m.SenderRole === 'student' ? 'student' : 'tutor_ai',
                text: m.MessageContent
            }));

            setThreadId(selectedThreadId);
            setMessages(loadedMessages);
        } catch (error) {
            console.error("Failed to load messages:", error);
        } finally {
            setIsLoading(false);
        }
    }, [customBaseURL]);

    // Démarrer nouvelle discussion propre
    const startNewChat = useCallback(() => {
        setThreadId(uuidv4());
        setMessages([]);
    }, []);

    // Send msg (Post)
    const sendMessage = useCallback(async (text: string) => {
        if (!text.trim()) return;

        const studentMessage: ChatMessage = { id: uuidv4(), sender: 'student', text: text };
        setMessages((prev) => [...prev, studentMessage]);
        setIsLoading(true);

        try {
            const response = await api.post('/chat/invoke', {
                thread_id: threadId,
                message: text,
                session_id: sessionId || null
            }, { baseURL: customBaseURL });

            const aiMessage: ChatMessage = { id: uuidv4(), sender: 'tutor_ai', text: response.data.response };
            setMessages((prev) => [...prev, aiMessage]);

            // Refresh historic
            loadHistoryThreads();
        } catch (error) {
            console.error("Chat Error:", error);
        } finally {
            setIsLoading(false);
        }
    }, [threadId, sessionId, customBaseURL, loadHistoryThreads]);

    return {
        threadId, messages, isLoading, historyThreads,
        sendMessage, loadHistoryThreads, loadThreadMessages, startNewChat
    };
}