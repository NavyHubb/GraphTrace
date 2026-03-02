"use client";

import React from 'react';
import { useStore } from '@/store/useStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from '@/components/ui/button';
import { Activity, Box, Globe, MousePointerClick, Sparkles, Loader2, CheckCircle2 } from 'lucide-react';
import { IntegrationScenarioView } from '../agent/IntegrationScenarioView';
import { HappyCaseTableView } from '../agent/HappyCaseTableView';

export function Dashboard() {
    const { 
        projectNodes, 
        generateBatchIntegrationScenarios, 
        generateHappyCaseScenarios,
        isAgentRunning, 
        integrationScenarios,
        happyCaseScenarios
    } = useStore();

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

                {/* Actions and Results Grouping to reduce white space */}
                <div className="space-y-6">
                    {/* Actions Grid */}
                    <div className="grid gap-6 md:grid-cols-2">
                        {/* Bulk Generate Card (Original) */}
                        <div className="flex flex-col justify-between p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100 shadow-sm relative overflow-hidden group">
                            <div className="z-10">
                                <h3 className="text-lg font-bold text-blue-900 flex items-center gap-2">
                                    <Sparkles className="h-5 w-5 text-blue-600" />
                                    정밀 분석 시나리오 생성 (Bulk)
                                </h3>
                                <p className="text-sm text-blue-700 mt-2 leading-relaxed">
                                    모든 {modifiedMethods}개 변경 지점에 대해 영향 경로를 추정하고 다각도의 통합 테스트 시나리오를 상세하게 생성합니다.
                                </p>
                            </div>
                            <Button
                                size="lg"
                                className="mt-6 bg-blue-600 hover:bg-blue-700 shadow-md transition-all hover:scale-[1.02] z-10 w-full"
                                onClick={() => generateBatchIntegrationScenarios()}
                                disabled={isAgentRunning || modifiedMethods === 0}
                            >
                                {isAgentRunning ? (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                ) : (
                                    <Sparkles className="mr-2 h-4 w-4" />
                                )}
                                {isAgentRunning ? '생성 중...' : 'Bulk Generate'}
                            </Button>
                            <Sparkles className="absolute -right-4 -bottom-4 h-24 w-24 text-blue-200/20 rotate-12 transition-transform group-hover:scale-110" />
                        </div>

                        {/* Happy Case Card (New & Independent) */}
                        <div className="flex flex-col justify-between p-6 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border border-emerald-100 shadow-sm relative overflow-hidden group">
                            <div className="z-10">
                                <h3 className="text-lg font-bold text-emerald-900 flex items-center gap-2">
                                    <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                                    Happy Case 일괄 생성
                                </h3>
                                <p className="text-sm text-emerald-700 mt-2 leading-relaxed">
                                    200 OK 성공 케이스에 대해서만 빠르게 테스트 데이터를 생성합니다. 테이블 뷰 형식으로 제공됩니다.
                                </p>
                            </div>
                            <Button
                                size="lg"
                                className="mt-6 bg-emerald-600 hover:bg-emerald-700 shadow-md transition-all hover:scale-[1.02] z-10 w-full"
                                onClick={() => generateHappyCaseScenarios()}
                                disabled={isAgentRunning || modifiedMethods === 0}
                            >
                                {isAgentRunning ? (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                ) : (
                                    <CheckCircle2 className="mr-2 h-4 w-4" />
                                )}
                                {isAgentRunning ? '생성 중...' : 'Happy Case 생성'}
                            </Button>
                            <CheckCircle2 className="absolute -right-4 -bottom-4 h-24 w-24 text-emerald-200/20 rotate-12 transition-transform group-hover:scale-110" />
                        </div>
                    </div>

                    {/* Results View - Happy Case (Independent) */}
                    {happyCaseScenarios.length > 0 && (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 w-full">
                            <HappyCaseTableView />
                        </div>
                    )}

                    {/* Results View - Integration Scenarios */}
                    {(integrationScenarios.length > 0 || (isAgentRunning && happyCaseScenarios.length === 0)) && (
                        <Card className="border-2 border-primary/20 shadow-lg overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500 w-full">
                            <IntegrationScenarioView />
                        </Card>
                    )}
                </div>

                {/* Guide / Empty State Helper */}
                {!isAgentRunning && integrationScenarios.length === 0 && happyCaseScenarios.length === 0 && (
                    <Card className="items-center justify-center flex flex-col p-10 border-dashed border-2 bg-slate-50/50">
                        <div className="bg-blue-100 p-4 rounded-full mb-4">
                            <MousePointerClick className="h-8 w-8 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">어떻게 탐색하나요?</h3>
                        <p className="text-muted-foreground text-center max-w-md">
                            왼쪽 사이드바에서 <strong>메서드</strong>나 <strong>엔드포인트</strong>를 선택하여 호출 그래프를 시각화하거나, 위 버튼들을 클릭하여 변경 사항에 대한 테스트 시나리오를 생성해 보세요.
                        </p>
                    </Card>
                )}

            </div>
        </div>
    );
}
