"use client";

import React from 'react';
import { useStore } from '@/store/useStore';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, FlaskConical } from "lucide-react";

export function HappyCaseTableView() {
    const { happyCaseScenarios } = useStore();

    if (happyCaseScenarios.length === 0) {
        return null;
    }

    return (
        <Card className="shadow-md border-primary/20">
            <CardHeader className="bg-primary/5 pb-4">
                <div className="flex items-center gap-2">
                    <FlaskConical className="h-5 w-5 text-primary" />
                    <CardTitle className="text-xl">Happy Case 테스트 시나리오 (일괄)</CardTitle>
                    <Badge variant="outline" className="ml-2 font-mono">
                        {happyCaseScenarios.length} Cases
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="p-0">
                <Table className="table-fixed w-full">
                    <TableHeader className="bg-muted/50">
                        <TableRow>
                            <TableHead className="w-[80px] font-bold text-center">ID</TableHead>
                            <TableHead className="w-auto font-bold text-center">테스트 케이스</TableHead>
                            <TableHead className="w-[30%] font-bold text-center">입력 데이터</TableHead>
                            <TableHead className="w-[30%] font-bold text-center">예상 결과</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {happyCaseScenarios.map((scenario, index) => (
                            <TableRow key={index} className="hover:bg-muted/30 transition-colors">
                                <TableCell className="font-mono text-xs font-bold text-center align-top pt-4">
                                    <Badge variant="secondary">{scenario.test_case_id}</Badge>
                                </TableCell>
                                <TableCell className="align-top pt-4">
                                    <div className="space-y-2 break-all whitespace-normal">
                                        <div className="flex flex-wrap items-center gap-2">
                                            <Badge variant="outline" className={getMethodColor(scenario.http_method)}>
                                                {scenario.http_method}
                                            </Badge>
                                            <span className="text-[11px] font-mono text-muted-foreground break-all" title={scenario.endpoint}>
                                                {scenario.endpoint}
                                            </span>
                                        </div>
                                        <p className="text-sm font-medium leading-relaxed">
                                            {scenario.test_case}
                                        </p>
                                    </div>
                                </TableCell>
                                <TableCell className="align-top">
                                    <div className="relative group">
                                        <pre className="text-[11px] font-mono bg-slate-950 text-slate-100 p-3 rounded-md overflow-x-auto max-h-[200px] whitespace-pre-wrap">
                                            {formatJson(scenario.input_data)}
                                        </pre>
                                    </div>
                                </TableCell>
                                <TableCell className="align-top text-center">
                                    <div className="relative group">
                                        <pre className="text-[11px] font-mono bg-green-950/20 text-green-700 p-3 rounded-md overflow-x-auto max-h-[200px] border border-green-200/50 whitespace-pre-wrap text-left">
                                            {formatJson(scenario.expected_result)}
                                        </pre>
                                        <div className="mt-2 flex items-center justify-center gap-1 text-[10px] text-green-600 font-bold uppercase">
                                            <CheckCircle2 className="h-3 w-3" />
                                            <span>200 OK Expected</span>
                                        </div>
                                    </div>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}

function formatJson(data: string) {
    try {
        // 만약 이미 객체라면 stringify, 아니라면 parse 시도 후 stringify
        const obj = typeof data === 'string' ? JSON.parse(data) : data;
        return JSON.stringify(obj, null, 2);
    } catch (e) {
        return data; // JSON이 아니면 그냥 출력
    }
}

function getMethodColor(method: string) {
    switch (method?.toUpperCase()) {
        case 'GET': return 'text-blue-600 border-blue-200 bg-blue-50';
        case 'POST': return 'text-green-600 border-green-200 bg-green-50';
        case 'PUT': return 'text-yellow-600 border-yellow-200 bg-yellow-50';
        case 'DELETE': return 'text-red-600 border-red-200 bg-red-50';
        default: return 'text-slate-600';
    }
}
