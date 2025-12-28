import React, { useEffect, useState } from 'react';
import api from '../api';

export default function CurrentRatesTable({ compact = false }) {
    const [rates, setRates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);

    const fetchRates = async () => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await api.get('/market-analysis/current-rates', {
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (response.data.success) {
                setRates(response.data.data);
                setLastUpdate(new Date());
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Kur çekme hatası:', error);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRates();
        const interval = setInterval(fetchRates, 60000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className={`flex justify-center items-center ${compact ? 'h-24' : 'h-48'}`}>
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (compact) {
        return (
            <div className="flex flex-wrap gap-4">
                {rates.map((rate) => (
                    <div key={rate.symbol} className="bg-[#f9fafb] border border-[#eaecf0] rounded-[6px] px-4 py-3 flex items-center gap-4 min-w-[180px] hover:bg-white hover:shadow-sm transition-all">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-bold text-[#667085] uppercase tracking-wider">{rate.name}</span>
                            <span className="text-sm font-extrabold text-[#101828]">
                                {rate.price.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                        </div>
                        <div className={`flex items-center text-[11px] font-bold ${rate.daily_change_percent >= 0 ? 'text-[#027a48]' : 'text-[#b42318]'}`}>
                            {rate.daily_change_percent >= 0 ? '▲' : '▼'} {Math.abs(rate.daily_change_percent).toFixed(2)}%
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-bold text-[#475467] uppercase tracking-wider">Anlık Piyasa Kurları</h3>
                {lastUpdate && (
                    <span className="text-[10px] font-medium text-[#98a2b3] bg-gray-50 px-2 py-1 rounded-[4px] border border-[#eaecf0]">
                        SON GÜNCELLEME: {lastUpdate.toLocaleTimeString('tr-TR')}
                    </span>
                )}
            </div>

            {/* Table - Clean & Inset look */}
            <div className="border border-[#eaecf0] rounded-[6px] overflow-hidden bg-white">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-[#f9fafb] border-b border-[#eaecf0]">
                            <th className="py-3 px-4 text-[11px] font-bold text-[#667085] uppercase tracking-wider">Enstrüman</th>
                            <th className="text-right py-3 px-4 text-[11px] font-bold text-[#667085] uppercase tracking-wider">Fiyat</th>
                            <th className="text-right py-3 px-4 text-[11px] font-bold text-[#667085] uppercase tracking-wider">Günlük Değişim</th>
                            <th className="text-right py-3 px-4 text-[11px] font-bold text-[#667085] uppercase tracking-wider">Yüzde</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-[#eaecf0]">
                        {rates.map((rate) => (
                            <tr
                                key={rate.symbol}
                                className="hover:bg-[#fcfcfd] transition-colors group"
                            >
                                <td className="py-3.5 px-4 text-sm">
                                    <div className="flex flex-col">
                                        <span className="font-bold text-[#101828]">{rate.name}</span>
                                        <span className="text-[11px] text-[#667085] font-medium">{rate.symbol}</span>
                                    </div>
                                </td>
                                <td className="text-right py-3.5 px-4 text-sm font-bold text-[#101828]">
                                    {rate.price.toLocaleString('tr-TR', {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    })}
                                </td>
                                <td className={`text-right py-3.5 px-4 text-sm font-bold ${rate.daily_change >= 0 ? 'text-[#067647]' : 'text-[#b42318]'
                                    }`}>
                                    {rate.daily_change >= 0 ? '+' : ''}
                                    {rate.daily_change.toFixed(2)}
                                </td>
                                <td className="text-right py-3.5 px-4">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-[4px] text-xs font-bold leading-5 ${rate.daily_change_percent >= 0
                                        ? 'bg-[#ecfdf3] text-[#027a48]'
                                        : 'bg-[#fef3f2] text-[#b42318]'
                                        }`}>
                                        {rate.daily_change_percent >= 0 ? '▲' : '▼'}
                                        {Math.abs(rate.daily_change_percent).toFixed(2)}%
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
