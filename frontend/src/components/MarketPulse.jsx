import React, { useEffect, useState } from 'react';
import api from '../api';

export default function MarketPulse() {
    const [pulse, setPulse] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPulse = async () => {
            try {
                const response = await api.get('/market-analysis/market-pulse');
                if (response.data.success) {
                    setPulse(response.data.data);
                }
            } catch (error) {
                console.error('Pulse fetch error:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchPulse();
    }, []);

    if (loading) return (
        <div className="animate-pulse bg-[#f9fafb] h-32 rounded-[6px] border border-[#eaecf0] flex items-center justify-center">
            <span className="text-gray-400 text-sm">Piyasa Nabzı Analiz Ediliyor...</span>
        </div>
    );

    if (!pulse) return null;

    return (
        <div className="bg-gradient-to-br from-[#f8f9ff] to-white border border-[#e0e4ff] rounded-[8px] p-6 shadow-sm relative overflow-hidden group">
            {/* Background Accent */}
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-[#444ce7] opacity-[0.03] rounded-full group-hover:scale-110 transition-transform duration-500"></div>

            <div className="flex items-start gap-4 relative z-10">
                <div className="flex-shrink-0 mt-1">
                    {pulse.sentiment === 'positive' && (
                        <div className="w-10 h-10 rounded-full bg-[#ecfdf3] flex items-center justify-center text-[#027a48]">
                            <span className="text-xl">📈</span>
                        </div>
                    )}
                    {pulse.sentiment === 'negative' && (
                        <div className="w-10 h-10 rounded-full bg-[#fef3f2] flex items-center justify-center text-[#b42318]">
                            <span className="text-xl">📉</span>
                        </div>
                    )}
                    {pulse.sentiment === 'neutral' && (
                        <div className="w-10 h-10 rounded-full bg-[#f2f4f7] flex items-center justify-center text-[#475467]">
                            <span className="text-xl">📊</span>
                        </div>
                    )}
                </div>

                <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                        <h3 className="font-extrabold text-[#101828] text-base mb-1">{pulse.title}</h3>
                        <span className="text-[10px] font-bold text-[#444ce7] px-2 py-0.5 bg-[#eef4ff] rounded-full uppercase tracking-wider">Günün Özeti</span>
                    </div>
                    <p className="text-[#475467] text-sm leading-relaxed font-medium">
                        {pulse.content}
                    </p>

                    {pulse.highlights && pulse.highlights.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-4">
                            {pulse.highlights.map((h, i) => (
                                <span key={i} className="inline-flex items-center px-2 py-1 rounded-[4px] bg-white border border-[#eaecf0] text-[11px] font-bold text-[#344054] shadow-sm">
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#444ce7] mr-1.5"></span>
                                    {h}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
