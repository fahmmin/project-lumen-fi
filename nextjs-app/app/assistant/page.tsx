'use client';

import { useState, useEffect, useRef } from 'react';
import { useUser } from '@/contexts/UserContext';
import { assistantAPI, ChatResponse, ConversationMessage } from '@/services/api';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import LoadingSpinner from '@/components/LoadingSpinner';
import { MessageCircle, Send, Bot, User, Sparkles, Trash2, RefreshCw, AlertCircle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export default function AssistantPage() {
    const { userId, isConnected } = useUser();
    const [messages, setMessages] = useState<ConversationMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const { toast } = useToast();

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;
        if (!isConnected || !userId) {
            toast({
                title: 'Wallet Not Connected',
                description: 'Please connect your wallet to use the assistant.',
                variant: 'destructive',
            });
            return;
        }

        const userMessage = input.trim();
        setInput('');
        setIsLoading(true);
        setIsTyping(true);

        // Add user message to UI immediately
        const newUserMessage: ConversationMessage = {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, newUserMessage]);

        try {
            const response: ChatResponse = await assistantAPI.chat({
                message: userMessage,
                user_id: userId,
                session_id: sessionId || undefined,
            });

            // Update session ID if we got a new one
            if (response.session_id) {
                setSessionId(response.session_id);
            }

            // Add assistant response
            const assistantMessage: ConversationMessage = {
                role: 'assistant',
                content: response.response,
                timestamp: new Date().toISOString(),
                metadata: response.action_taken ? { action: response.action_taken } : undefined,
            };
            setMessages((prev) => [...prev, assistantMessage]);

            // Update suggestions
            if (response.suggestions && response.suggestions.length > 0) {
                setSuggestions(response.suggestions);
            } else {
                setSuggestions([]);
            }

            // Show error toast if action failed
            if (response.action_taken && !response.action_taken.success) {
                toast({
                    title: 'Action Failed',
                    description: response.action_taken.error || 'The requested action could not be completed.',
                    variant: 'destructive',
                });
            }
        } catch (error: any) {
            console.error('Chat error:', error);
            const errorMessage: ConversationMessage = {
                role: 'assistant',
                content: `Sorry, I encountered an error: ${error.message || 'Unknown error'}. Please try again.`,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
            toast({
                title: 'Error',
                description: error.message || 'Failed to send message',
                variant: 'destructive',
            });
        } finally {
            setIsLoading(false);
            setIsTyping(false);
            inputRef.current?.focus();
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion);
        inputRef.current?.focus();
    };

    const handleClearChat = async () => {
        if (sessionId) {
            try {
                await assistantAPI.clearSession(sessionId);
            } catch (error) {
                console.error('Failed to clear session:', error);
            }
        }
        setMessages([]);
        setSessionId(null);
        setSuggestions([]);
        toast({
            title: 'Chat Cleared',
            description: 'Conversation history has been cleared.',
        });
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <Container className="py-6 max-w-4xl">
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold flex items-center gap-2">
                            <MessageCircle className="h-8 w-8" />
                            AI Assistant
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-1">
                            Chat with your financial assistant using natural language
                        </p>
                    </div>
                    {messages.length > 0 && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleClearChat}
                            className="flex items-center gap-2"
                        >
                            <Trash2 className="h-4 w-4" />
                            Clear Chat
                        </Button>
                    )}
                </div>

                {/* Connection Status */}
                {!isConnected && (
                    <Card className="border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20">
                        <CardContent className="pt-6">
                            <div className="flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
                                <AlertCircle className="h-5 w-5" />
                                <p>Please connect your wallet to use the assistant.</p>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Chat Messages */}
                <Card className="h-[500px] flex flex-col">
                    <CardHeader className="border-b">
                        <CardTitle className="flex items-center gap-2">
                            <Bot className="h-5 w-5" />
                            Conversation
                        </CardTitle>
                        <CardDescription>
                            Ask me anything about your finances, goals, spending, and more!
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 text-gray-500 dark:text-gray-400">
                                <Sparkles className="h-12 w-12" />
                                <div>
                                    <p className="text-lg font-semibold mb-2">Welcome to AI Assistant!</p>
                                    <p className="text-sm">
                                        I can help you with:
                                    </p>
                                    <ul className="text-sm mt-2 space-y-1 list-disc list-inside">
                                        <li>Adding receipts and expenses</li>
                                        <li>Creating financial goals</li>
                                        <li>Viewing your dashboard</li>
                                        <li>Generating reports</li>
                                        <li>And much more!</li>
                                    </ul>
                                    <p className="text-sm mt-4">
                                        Try saying: &quot;I spent $50 at Starbucks&quot; or &quot;Show my dashboard&quot;
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <>
                                {messages.map((message, index) => (
                                    <div
                                        key={index}
                                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                            }`}
                                    >
                                        {message.role === 'assistant' && (
                                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center">
                                                <Bot className="h-4 w-4" />
                                            </div>
                                        )}
                                        <div
                                            className={`max-w-[80%] rounded-lg p-3 ${message.role === 'user'
                                                ? 'bg-black dark:bg-white text-white dark:text-black'
                                                : 'bg-gray-100 dark:bg-gray-800'
                                                }`}
                                        >
                                            <p className="whitespace-pre-wrap break-words">{message.content}</p>
                                            {message.metadata?.action && (
                                                <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600">
                                                    <Badge variant="outline" className="text-xs">
                                                        {message.metadata.action.method} {message.metadata.action.endpoint}
                                                    </Badge>
                                                    {message.metadata.action.success ? (
                                                        <Badge variant="default" className="ml-2 text-xs bg-green-500">
                                                            Success
                                                        </Badge>
                                                    ) : (
                                                        <Badge variant="destructive" className="ml-2 text-xs">
                                                            Failed
                                                        </Badge>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                        {message.role === 'user' && (
                                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                                                <User className="h-4 w-4" />
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {isTyping && (
                                    <div className="flex gap-3 justify-start">
                                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center">
                                            <Bot className="h-4 w-4" />
                                        </div>
                                        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
                                            <LoadingSpinner size="sm" />
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </>
                        )}
                    </CardContent>
                </Card>

                {/* Suggestions */}
                {suggestions.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {suggestions.map((suggestion, index) => (
                            <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="text-xs"
                            >
                                {suggestion}
                            </Button>
                        ))}
                    </div>
                )}

                {/* Input Area */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex gap-2">
                            <Input
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder={
                                    isConnected
                                        ? "Type your message... (e.g., 'I spent $50 at Starbucks')"
                                        : 'Connect wallet to start chatting...'
                                }
                                disabled={!isConnected || isLoading}
                                className="flex-1"
                            />
                            <Button
                                onClick={handleSend}
                                disabled={!isConnected || isLoading || !input.trim()}
                                className="flex items-center gap-2"
                            >
                                {isLoading ? (
                                    <LoadingSpinner size="sm" />
                                ) : (
                                    <Send className="h-4 w-4" />
                                )}
                                Send
                            </Button>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                            Press Enter to send, Shift+Enter for new line
                        </p>
                    </CardContent>
                </Card>
            </div>
        </Container>
    );
}

