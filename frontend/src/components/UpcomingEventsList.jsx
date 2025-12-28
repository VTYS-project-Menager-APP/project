import React, { useEffect, useState } from 'react';
import api from '../api';

export default function UpcomingEventsList() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchEvents = async () => {
        try {
            const response = await api.get('/market-analysis/upcoming-events');
            if (response.data.success) {
                setEvents(response.data.data);
            }
        } catch (error) {
            console.error('Gelecek olaylar çekme hatası:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-48">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-end mb-6 px-1">
                <div>
                    <h3 className="text-sm font-bold text-[#475467] uppercase tracking-wider">Gelecek Kritik Olaylar</h3>
                    <p className="text-[10px] text-[#98a2b3] font-medium mt-1 uppercase tracking-tighter">AI Destekli Piyasa Beklentileri</p>
                </div>
                <div className="bg-[#f2f4f7] text-[#101828] px-2 py-1 rounded-[4px] text-[10px] font-black">
                    {events.length} AKTİF TAKVİM
                </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
                {events.map((event) => (
                    <div
                        key={event.id}
                        className="bg-white border border-[#eaecf0] rounded-[6px] p-5 hover:border-[#444ce7] transition-all group"
                    >
                        <div className="flex flex-col md:flex-row gap-6">
                            {/* Date Badge - Minimalist */}
                            <div className="flex-shrink-0 flex md:flex-col items-center justify-center bg-[#f9fafb] border border-[#eaecf0] p-3 rounded-[6px] min-w-[80px]">
                                <span className="text-[10px] uppercase font-black tracking-widest text-[#667085]">
                                    {new Date(event.event_date).toLocaleDateString('tr-TR', { month: 'short' })}
                                </span>
                                <span className="text-2xl font-black text-[#101828]">
                                    {new Date(event.event_date).toLocaleDateString('tr-TR', { day: 'numeric' })}
                                </span>
                            </div>

                            {/* Content */}
                            <div className="flex-1">
                                <div className="flex flex-wrap items-center gap-2 mb-3">
                                    <span className="px-2 py-0.5 rounded-[4px] bg-[#f2f4f7] text-[#344054] text-[9px] font-bold uppercase tracking-wider border border-[#eaecf0]">
                                        {event.category}
                                    </span>
                                    <span className="px-2 py-0.5 rounded-[4px] bg-[#eef4ff] text-[#3538cd] text-[9px] font-bold uppercase tracking-wider border border-[#c7d7fe]">
                                        {event.impact_prediction}
                                    </span>
                                </div>

                                <h4 className="text-base font-bold text-[#101828] mb-2 group-hover:text-[#444ce7] transition-colors">
                                    {event.title}
                                </h4>
                                <p className="text-[#475467] text-xs leading-relaxed mb-4">
                                    {event.description}
                                </p>

                                {/* AI Advice Box - Inset style */}
                                <div className="bg-[#fcfcfd] border border-[#eaecf0] rounded-[6px] p-4 flex items-start gap-3">
                                    <div className="bg-white p-1.5 rounded-[4px] border border-[#eaecf0] text-[#444ce7] flex-shrink-0">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                    <div className="min-w-0">
                                        <h5 className="text-[10px] font-black text-[#444ce7] uppercase tracking-widest mb-1">AI Strateji Notu</h5>
                                        <p className="text-[#344054] text-xs font-medium leading-relaxed italic">
                                            "{event.ai_advice}"
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {events.length === 0 && (
                <div className="text-center py-20 bg-[#f9fafb] rounded-[6px] border border-dashed border-[#eaecf0]">
                    <div className="text-3xl mb-3 grayscale opacity-30">📅</div>
                    <div className="text-sm font-bold text-[#475467]">Gelecek olay kaydı yok</div>
                    <p className="text-[10px] text-[#98a2b3] mt-1">Takvim verileri güncellendiğinde burada görünecektir.</p>
                </div>
            )}
        </div>
    );
}
