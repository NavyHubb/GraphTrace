"use client";

import React from 'react';
import { useStore } from '@/store/useStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from '@/components/ui/button';
import { Activity, Box, Globe, MousePointerClick, Sparkles, Loader2 } from 'lucide-react';
import { IntegrationScenarioView } from '../agent/IntegrationScenarioView';

export function Dashboard() {
    const { projectNodes, generateBatchIntegrationScenarios, isAgentRunning, integrationScenarios } = useStore();

    const totalMethods = projectNodes.length; // All nodes are methods, some have endpoints
    const totalEndpoints = projectNodes.filter(n => n.type === 'ENDPOINT').length;
    const modifiedMethods = projectNodes.filter(n => n.status === 'MODIFIED').length;
    // const newMethods = projectNodes.filter(n => n.status === 'NEW').length; // Optional to show separately

    return (
        <div className="p-8 h-full bg-slate-50 overflow-y-auto">
            <div className="max-w-5xl mx-auto space-y-8 pb-20">

                {/* Header */}
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Project Dashboard</h1>
                    <p className="text-slate-500">
                        Welcome to TcAgent. Here is a summary of the analyzed project.
                    </p>
                </div>

                {/* Stats Grid */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Methods</CardTitle>
                            <Box className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{totalMethods}</div>
                            <p className="text-xs text-muted-foreground">
                                Identified functions & constructors
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Endpoints</CardTitle>
                            <Globe className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{totalEndpoints}</div>
                            <p className="text-xs text-muted-foreground">
                                Rest API Entry Points
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Modifications</CardTitle>
                            <Activity className={`h-4 w-4 ${modifiedMethods > 0 ?'text-orange-500' : 'text-muted-foreground'}`} />
                        </CardHeader>
                        <CardContent>
                            <div className={`text-2xl font-bold ${modifiedMethods > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                                {modifiedMethods > 0 ? `${modifiedMethods} Modified` : 'Stable'}
                            </div>
                            <p className="text-xs text-muted-foreground">
                                {modifiedMethods > 0 ? 'Ready for Regression Testing' : 'No logic changes detected'}
                            </p>
                        </CardContent>
                    </Card>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100 shadow-sm relative overflow-hidden">
                    <div className="z-10">
                        <h3 className="text-lg font-semibold text-blue-900">Generate Integration Tests (Batch)</h3>
                        <p className="text-sm text-blue-700 mt-1">
                            Automatically generate comprehensive integration tests for all {modifiedMethods} modified points.
                        </p>
                    </div>
                    <Button
                        size="lg"
                        className="bg-blue-600 hover:bg-blue-700 shadow-md transition-all hover:scale-105 z-10"
                        onClick={() => generateBatchIntegrationScenarios()}
                        disabled={isAgentRunning || modifiedMethods === 0}
                    >
                        {isAgentRunning ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                            <Sparkles className="mr-2 h-4 w-4" />
                        )}
                        {isAgentRunning ? 'Generating...' : 'Bulk Generate'}
                    </Button>
                    <Sparkles className="absolute -right-4 -bottom-4 h-32 w-32 text-blue-200/30 rotate-12" />
                </div>

                {/* Results View */}
                { (integrationScenarios.length > 0 || isAgentRunning) && (
                    <Card className="border-2 border-primary/20 shadow-lg">
                        <IntegrationScenarioView />
                    </Card>
                )}

                {/* Guide / Empty State Helper */}
                {!isAgentRunning && integrationScenarios.length === 0 && (
                    <Card className="items-center justify-center flex flex-col p-10 border-dashed border-2 bg-slate-50/50">
                        <div className="bg-blue-100 p-4 rounded-full mb-4">
                            <MousePointerClick className="h-8 w-8 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">How to explore?</h3>
                        <p className="text-muted-foreground text-center max-w-md">
                            Select a <strong>Method</strong> or <strong>Endpoint</strong> from the left sidebar to visualize its call graph and dependency chain, or click the button above to test all changes.
                        </p>
                    </Card>
                )}

            </div>
        </div>
    );
}
