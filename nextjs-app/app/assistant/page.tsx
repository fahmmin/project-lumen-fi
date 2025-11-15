'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useUser } from '@/contexts/UserContext';
import { assistantAPI, ChatResponse, ConversationMessage, ingestionAPI, type IngestionResponse } from '@/services/api';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import LoadingSpinner from '@/components/LoadingSpinner';
import { MessageCircle, Send, Bot, User, Sparkles, Trash2, RefreshCw, AlertCircle, Upload, File, X, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export default function AssistantPage() {
    const { userId, isConnected } = useUser();
    const [messages, setMessages] = useState<ConversationMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
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

    // File upload handlers
    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            handleFileSelect(droppedFile);
        }
    }, []);

    const handleFileSelect = (selectedFile: File) => {
        const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(selectedFile.type)) {
            toast({
                title: 'Invalid file type',
                description: 'Please upload a PDF or image file (JPEG, PNG)',
                variant: 'destructive',
            });
            return;
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            toast({
                title: 'File too large',
                description: 'File size must be less than 10MB',
                variant: 'destructive',
            });
            return;
        }

        setFile(selectedFile);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        if (!isConnected || !userId) {
            toast({
                title: 'Wallet Not Connected',
                description: 'Please connect your wallet to upload files.',
                variant: 'destructive',
            });
            return;
        }

        setUploading(true);
        setIsLoading(true);

        try {
            // Upload the file
            const result: IngestionResponse = await ingestionAPI.uploadDocument(file, userId);

            toast({
                title: 'Upload successful',
                description: 'Document has been processed and indexed',
            });

            // Add user message about the upload
            const uploadMessage: ConversationMessage = {
                role: 'user',
                content: `I just uploaded a file: ${file.name}`,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, uploadMessage]);

            // Add assistant confirmation message directly (no API call to avoid triggering report endpoints)
            const assistantMessage: ConversationMessage = {
                role: 'assistant',
                content: `Great! I've successfully processed your file "${file.name}". The document has been indexed (Document ID: ${result.document_id}, ${result.chunks_created} chunks created). You can now ask me questions about it, such as:\n\n• "What information is in this document?"\n• "Extract the key details from this file"\n• "What expenses are in this receipt?"\n• "Summarize this document"`,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);

            // Add helpful suggestions for uploaded files
            setSuggestions([
                "What information is in this document?",
                "Extract the key details from this file",
                "What expenses are in this receipt?",
            ]);

            // Clear the file
            setFile(null);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        } catch (error: any) {
            console.error('Upload error:', error);
            toast({
                title: 'Upload failed',
                description: error.message || 'Failed to upload document',
                variant: 'destructive',
            });
        } finally {
            setUploading(false);
            setIsLoading(false);
            setIsTyping(false);
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
                                        <li>Uploading and analyzing receipts, invoices, and documents</li>
                                        <li>Adding receipts and expenses</li>
                                        <li>Creating financial goals</li>
                                        <li>Viewing your dashboard</li>
                                        <li>Generating reports</li>
                                        <li>And much more!</li>
                                    </ul>
                                    <p className="text-sm mt-4">
                                        Try uploading a file or saying: &quot;I spent $50 at Starbucks&quot; or &quot;Show my dashboard&quot;
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

                {/* File Upload Area */}
                {file && (
                    <Card className="border-2 border-black dark:border-white">
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <File className="h-5 w-5 text-black dark:text-white" />
                                    <div>
                                        <p className="font-medium text-sm">{file.name}</p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">
                                            {(file.size / 1024).toFixed(2)} KB
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    {!uploading && (
                                        <Button
                                            onClick={handleUpload}
                                            disabled={!isConnected || isLoading}
                                            size="sm"
                                            className="flex items-center gap-2"
                                        >
                                            <Upload className="h-4 w-4" />
                                            Upload
                                        </Button>
                                    )}
                                    {uploading && (
                                        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                            Uploading...
                                        </div>
                                    )}
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => {
                                            setFile(null);
                                            if (fileInputRef.current) {
                                                fileInputRef.current.value = '';
                                            }
                                        }}
                                        disabled={uploading}
                                    >
                                        <X className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Input Area */}
                <Card
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={isDragging ? 'border-2 border-black dark:border-white border-dashed' : ''}
                >
                    <CardContent className="pt-6">
                        <div className="flex gap-2">
                            <div className="flex-1 relative">
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
                                    disabled={!isConnected || isLoading || uploading}
                                    className="flex-1 pr-10"
                                />
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    id="file-input-assistant"
                                    className="hidden"
                                    accept=".pdf,.jpg,.jpeg,.png"
                                    onChange={handleFileInput}
                                    disabled={!isConnected || isLoading || uploading}
                                />
                                <label
                                    htmlFor="file-input-assistant"
                                    className="absolute right-2 top-1/2 -translate-y-1/2 cursor-pointer p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
                                    title="Upload file"
                                >
                                    <Upload className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                                </label>
                            </div>
                            <Button
                                onClick={handleSend}
                                disabled={!isConnected || isLoading || uploading || !input.trim()}
                                className="flex items-center gap-2"
                            >
                                {isLoading && !uploading ? (
                                    <LoadingSpinner size="sm" />
                                ) : (
                                    <Send className="h-4 w-4" />
                                )}
                                Send
                            </Button>
                        </div>
                        <div className="flex items-center justify-between mt-2">
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                Press Enter to send, Shift+Enter for new line
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                {isDragging ? 'Drop file here' : 'Drag & drop or click upload icon to attach file'}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </Container>
    );
}

