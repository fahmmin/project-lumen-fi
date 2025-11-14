'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { memoryAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { FileText, Search, ArrowRight, FileSearch } from 'lucide-react';
import Link from 'next/link';

interface Document {
    document_id: string;
    filename: string;
    vendor?: string;
    date?: string;
    amount?: number;
    category?: string;
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();
    const router = useRouter();

    useEffect(() => {
        loadDocuments();
    }, []);

    useEffect(() => {
        if (searchQuery.trim() === '') {
            setFilteredDocuments(documents);
        } else {
            const query = searchQuery.toLowerCase();
            setFilteredDocuments(
                documents.filter(
                    (doc) =>
                        doc.filename.toLowerCase().includes(query) ||
                        doc.vendor?.toLowerCase().includes(query) ||
                        doc.category?.toLowerCase().includes(query)
                )
            );
        }
    }, [searchQuery, documents]);

    const loadDocuments = async () => {
        try {
            setLoading(true);
            const memory = await memoryAPI.getWorkspaceMemory();

            // Parse documents from workspace content
            const docMatches = memory.workspace_content.match(/### NEW DOCUMENT INGESTED[\s\S]*?(?=###|$)/g) || [];
            const parsedDocs: Document[] = docMatches.map((match) => {
                const idMatch = match.match(/Document ID: (doc_\w+)/);
                const filenameMatch = match.match(/Filename: (.+)/);
                const vendorMatch = match.match(/Vendor: (.+)/);
                const dateMatch = match.match(/Date: (.+)/);
                const amountMatch = match.match(/Amount: ([\d.]+)/);
                const categoryMatch = match.match(/Category: (.+)/);

                return {
                    document_id: idMatch?.[1] || '',
                    filename: filenameMatch?.[1] || 'Unknown',
                    vendor: vendorMatch?.[1],
                    date: dateMatch?.[1],
                    amount: amountMatch ? parseFloat(amountMatch[1]) : undefined,
                    category: categoryMatch?.[1],
                };
            }).filter((doc) => doc.document_id);

            setDocuments(parsedDocs);
            setFilteredDocuments(parsedDocs);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load documents',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleRunAudit = (doc: Document) => {
        const auditData = {
            vendor: doc.vendor || '',
            date: doc.date || new Date().toISOString().split('T')[0],
            amount: doc.amount || 0,
            category: doc.category || '',
        };
        sessionStorage.setItem('auditData', JSON.stringify(auditData));
        router.push('/audit');
    };

    return (
        <Container>
            <div className="max-w-6xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold mb-2">Documents</h1>
                        <p className="text-gray-600">
                            Manage and view all ingested documents
                        </p>
                    </div>
                    <Link href="/upload">
                        <Button>
                            <FileText className="h-4 w-4 mr-2" />
                            Upload New
                        </Button>
                    </Link>
                </div>

                {/* Search */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input
                                placeholder="Search documents by name, vendor, or category..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Documents List */}
                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {[1, 2, 3, 4, 5, 6].map((i) => (
                            <Card key={i}>
                                <CardHeader>
                                    <Skeleton className="h-4 w-3/4" />
                                    <Skeleton className="h-3 w-1/2 mt-2" />
                                </CardHeader>
                                <CardContent>
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-2/3 mt-2" />
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : filteredDocuments.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filteredDocuments.map((doc) => (
                            <Card key={doc.document_id} className="hover:shadow-md transition-shadow">
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <FileText className="h-5 w-5 text-gray-400" />
                                        {doc.category && (
                                            <Badge variant="outline">{doc.category}</Badge>
                                        )}
                                    </div>
                                    <CardTitle className="text-lg mt-2 line-clamp-2">
                                        {doc.filename}
                                    </CardTitle>
                                    <CardDescription className="text-xs">
                                        ID: {doc.document_id}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-3">
                                    {doc.vendor && (
                                        <div>
                                            <p className="text-xs text-gray-600">Vendor</p>
                                            <p className="text-sm font-medium">{doc.vendor}</p>
                                        </div>
                                    )}
                                    {doc.amount !== undefined && (
                                        <div>
                                            <p className="text-xs text-gray-600">Amount</p>
                                            <p className="text-sm font-medium">${doc.amount.toFixed(2)}</p>
                                        </div>
                                    )}
                                    {doc.date && (
                                        <div>
                                            <p className="text-xs text-gray-600">Date</p>
                                            <p className="text-sm font-medium">{doc.date}</p>
                                        </div>
                                    )}
                                    <div className="flex gap-2 pt-2">
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="flex-1"
                                            onClick={() => handleRunAudit(doc)}
                                        >
                                            <FileSearch className="h-3 w-3 mr-1" />
                                            Audit
                                        </Button>
                                        <Link href="/insights" className="flex-1">
                                            <Button size="sm" variant="outline" className="w-full">
                                                View
                                                <ArrowRight className="h-3 w-3 ml-1" />
                                            </Button>
                                        </Link>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : (
                    <EmptyState
                        title="No documents found"
                        description={
                            searchQuery
                                ? 'Try adjusting your search query'
                                : 'Upload your first document to get started'
                        }
                        icon={<FileText className="h-12 w-12" />}
                        action={
                            <Link href="/upload">
                                <Button>Upload Document</Button>
                            </Link>
                        }
                    />
                )}
            </div>
        </Container>
    );
}

