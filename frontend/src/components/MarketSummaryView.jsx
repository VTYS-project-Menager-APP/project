import React, { useEffect, useState } from 'react';
import api from '../api';
import CurrentRatesTable from './CurrentRatesTable';

export default function MarketSummaryView() {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchSummary = async () => {
        try {
            const response = await api.get('/market-analysis/summary');
            if (response.data.success) {
                setSummary(response.data.data);
            }
        } catch (error) {
            console.error('Özet çekme hatası:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSummary();
        const interval = setInterval(fetchSummary, 300000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-96">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-400"></div>
            </div>
        );
    }

    if (!summary) {
        return (
            <div className="text-center py-20">
                <p className="text-gray-500">Piyasa özeti hazırlanıyor...</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Güncel Kurlar */}
            <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Güncel Kurlar</h2>
                <CurrentRatesTable />
            </div>

            {/* AI Piyasa Analizi */}
            <div className="bg-white border border-gray-200 rounded-lg p-8">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
                    <svg className="w-6 h-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <h2 className="text-xl font-semibold text-gray-900">Fiyat Tahmini</h2>
                </div>

                {/* AI Analizi */}
                <div className="space-y-6">
                    <div>
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Piyasa Durumu</h3>
                        <p className="text-gray-800 leading-relaxed">
                            {summary.summary_text}
                        </p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-5 border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Öngörü</h3>
                        <p className="text-gray-800 leading-relaxed whitespace-pre-line">
                            {summary.advice_text}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
