import React, { useEffect, useState } from 'react';
import api from '../api';

export default function EventImpactList({ showAll = false, showTopOnly = false, isHistorical = false }) {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedEvent, setSelectedEvent] = useState(null);

    const fetchEvents = async () => {
        try {
            let endpoint = '';
            if (isHistorical) {
                endpoint = '/market-analysis/historical-correlation?limit=20';
            } else if (showTopOnly) {
                endpoint = '/market-analysis/top-impact-events?limit=5';
            } else {
                endpoint = '/market-analysis/current-events?limit=10';
            }

            const response = await api.get(endpoint);
            if (response.data.success) {
                // Map historical data to common format
                const mappedData = isHistorical
                    ? response.data.data.map(item => ({
                        id: item.event_title + item.event_date,
                        title: item.event_title,
                        description: item.insight || `Normal seyir. Geçmişte bu olay %${item.percent_change.toFixed(2)} değişim yaşatmıştı.`,
                        category: item.category,
                        predicted_impact: Math.abs(item.percent_change),
                        published_at: item.event_date,
                        percent_change: item.percent_change
                    }))
                    : response.data.data;

                setEvents(mappedData);
            }
        } catch (error) {
            console.error('Olay çekme hatası:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();

        // Her 5 dakikada bir güncelle (daha az sıklıkla)
        const interval = setInterval(fetchEvents, 300000);

        return () => clearInterval(interval);
    }, [showTopOnly]);

    const getImpactColor = (impact) => {
        if (impact >= 7) return 'bg-red-100 text-red-700 border-red-200';
        if (impact >= 4) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
        return 'bg-green-100 text-green-700 border-green-200';
    };

    const getImpactLabel = (impact) => {
        if (impact >= 7) return 'Yüksek Etki';
        if (impact >= 4) return 'Orta Etki';
        return 'Düşük Etki';
    };

    const getCategoryIcon = (category) => {
        const icons = {
            'altın': '🏆',
            'döviz': '💵',
            'para_politikası': '🏦',
            'borsa': '📈',
            'genel_ekonomi': '📊'
        };
        return icons[category] || '📰';
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-48">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex justify-between items-end mb-4 px-1">
                <div>
                    <h3 className="text-sm font-bold text-[#475467] uppercase tracking-wider">
                        {isHistorical ? 'Kaggle Veri Bankası' : showTopOnly ? 'Yüksek Etkili Olaylar' : 'Piyasa Haber Akışı'}
                    </h3>
                    {isHistorical && (
                        <p className="text-[10px] text-[#98a2b3] font-medium mt-1 uppercase tracking-tighter">
                            8,000+ kayıt üzerinden tarihsel korelasyon verileri
                        </p>
                    )}
                </div>
                <span className="text-[10px] font-black text-[#101828] bg-[#f2f4f7] px-2 py-1 rounded-[4px]">
                    {events.length} KAYIT
                </span>
            </div>

            {/* Events List */}
            <div className="grid grid-cols-1 gap-3">
                {events.map((event) => (
                    <div
                        key={event.id}
                        className="bg-white border border-[#eaecf0] rounded-[6px] p-4 hover:border-[#444ce7] transition-all cursor-pointer group"
                        onClick={() => setSelectedEvent(event.id === selectedEvent ? null : event.id)}
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-2">
                                    <span className="text-lg">{getCategoryIcon(event.category)}</span>
                                    <span className="text-[10px] font-black uppercase tracking-widest text-[#667085]">
                                        {event.category}
                                    </span>
                                </div>

                                <h4 className="font-bold text-[#101828] text-sm mb-2 group-hover:text-[#444ce7] transition-colors leading-snug">
                                    {event.title}
                                </h4>

                                {(selectedEvent === event.id || isHistorical) && (
                                    <div className={`mb-3 p-3 rounded-[4px] border ${isHistorical ? 'bg-[#f0f2ff] border-[#e0e4ff]' : 'bg-[#f9fafb] border-[#eaecf0]'}`}>
                                        <div className="flex items-start gap-2">
                                            {isHistorical && <span className="text-blue-600 mt-0.5 font-bold">💡</span>}
                                            <p className={`text-xs leading-relaxed font-medium ${isHistorical ? 'text-[#344054]' : 'text-[#475467]'}`}>
                                                {event.description}
                                            </p>
                                        </div>
                                    </div>
                                )}

                                <div className="flex items-center space-x-3 text-[10px] font-bold text-[#98a2b3] uppercase tracking-tighter">
                                    <span>
                                        {new Date(event.published_at).toLocaleDateString('tr-TR', {
                                            day: 'numeric',
                                            month: 'short',
                                            year: 'numeric'
                                        })}
                                    </span>
                                    {event.url && (
                                        <a
                                            href={event.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-[#444ce7] hover:underline flex items-center"
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            RAPORA GİT <span className="ml-1 text-[8px]">↗</span>
                                        </a>
                                    )}
                                </div>
                            </div>

                            {/* Impact Score or Change */}
                            <div className="ml-4 flex-shrink-0">
                                <div className={`px-3 py-2 rounded-[6px] border ${event.percent_change >= 0 || event.predicted_impact >= 7
                                    ? 'bg-[#ecfdf3] border-[#abefc6] text-[#067647]'
                                    : 'bg-[#fef3f2] border-[#fecdca] text-[#b42318]'
                                    }`}>
                                    <div className="text-center min-w-[50px]">
                                        <div className="text-lg font-black tracking-tighter">
                                            {event.percent_change !== undefined
                                                ? `${event.percent_change > 0 ? '+' : ''}${event.percent_change.toFixed(2)}%`
                                                : event.predicted_impact.toFixed(1)
                                            }
                                        </div>
                                        <div className="text-[8px] font-black uppercase whitespace-nowrap opacity-80">
                                            {isHistorical ? 'Değişim' : 'Etki Skoru'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {events.length === 0 && (
                <div className="text-center py-20 bg-[#f9fafb] rounded-[6px] border border-dashed border-[#eaecf0]">
                    <div className="text-3xl mb-3 grayscale opacity-30">🔍</div>
                    <div className="text-sm font-bold text-[#475467]">Veri bulunamadı</div>
                    <p className="text-[10px] text-[#98a2b3] mt-1">Sistem piyasa verilerini taramaya devam ediyor.</p>
                </div>
            )}
        </div>
    );
}
