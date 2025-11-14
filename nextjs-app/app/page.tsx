'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Container } from '@/components/layout/Container';
import { ArrowRight, Brain, Shield, Zap, TrendingUp, FileSearch, Database, Lock } from 'lucide-react';

export default function LandingPage() {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Multimodal GenAI processes receipts, invoices, and transaction records with intelligent reasoning',
    },
    {
      icon: Shield,
      title: 'Secure & Compliant',
      description: 'End-to-end encryption, secure enclaves, and zero-knowledge proofs with full auditability',
    },
    {
      icon: Zap,
      title: 'Real-Time Intelligence',
      description: 'Autonomous risk assessment, anomaly detection, and expense optimization at scale',
    },
    {
      icon: TrendingUp,
      title: 'Predictive Insights',
      description: 'Generates intelligent, explainable financial summaries and predicts anomalies',
    },
    {
      icon: FileSearch,
      title: 'Multi-Agent Audits',
      description: 'Comprehensive audits using specialized AI agents for compliance, fraud, and pattern detection',
    },
    {
      icon: Database,
      title: 'RAG-Powered Context',
      description: 'Retrieval-Augmented Generation provides context-aware insights from your financial history',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 md:py-32">
        <Container>
          <div className="text-center space-y-8 max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold text-black dark:text-white">
              LUMEN
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400">
              The AI Financial Intelligence Layer
            </p>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Transform raw financial documents into structured intelligence and actionable insights
              using multimodal GenAI, RAG, and behavioral intelligence.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/dashboard">
                <Button size="lg" className="w-full sm:w-auto">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/audit">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  Run Audit
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <Container>
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Core Capabilities
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Everything you need for intelligent financial management
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <Icon className="h-8 w-8 mb-2 text-black dark:text-white" />
                    <CardTitle>{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                </Card>
              );
            })}
          </div>
        </Container>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <Container>
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { step: '1', title: 'Upload', desc: 'Upload financial documents (PDF, images)' },
              { step: '2', title: 'Process', desc: 'AI extracts and structures data automatically' },
              { step: '3', title: 'Analyze', desc: 'Multi-agent system audits and detects anomalies' },
              { step: '4', title: 'Insights', desc: 'Get actionable insights and predictions' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-16 h-16 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600 dark:text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-black dark:bg-white text-white dark:text-black">
        <Container>
          <div className="text-center space-y-6 max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold">
              Ready to Transform Your Financial Intelligence?
            </h2>
            <p className="text-lg opacity-90">
              Start using LUMEN today and experience the future of financial document analysis
            </p>
            <Link href="/dashboard">
              <Button size="lg" variant="outline" className="bg-white dark:bg-black text-black dark:text-white border-white dark:border-black">
                Go to Dashboard
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </Container>
      </section>
    </div>
  );
}
