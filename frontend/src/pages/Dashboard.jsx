import React, { useEffect, useState } from 'react';
import api from '../api';
import EventBar from '../components/EventBar';
import MarketAnalysisTabs from '../components/MarketAnalysisTabs';
import SmartTransportContainerV2 from '../components/SmartTransportContainerV2';
import AlarmNotification from '../components/AlarmNotification';

// Loading component
const LoadingSpinner = () => (
    <div className="flex justify-center items-center h-48">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
    </div>
);

export default function Dashboard() {
    const [transit, setTransit] = useState(null);
    const [transitLoading, setTransitLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const transitRes = await api.get('/transit/alarm-recommendation');
                setTransit(transitRes.data);
            } catch (e) {
                console.error(e);
                setTransit(null);
            } finally {
                setTransitLoading(false);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="max-w-[1600px] mx-auto p-4 md:p-8 space-y-6">
            {/* Header section - Clean & Professional */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4">
                <div>
                    <h1 className="text-3xl font-extrabold text-[#101828] tracking-tight">Menager Dashboard</h1>
                    <p className="text-[#475467] text-sm mt-1">Hoş geldiniz, işte günlük analizleriniz ve bildirimleriniz.</p>
                </div>
                <button
                    onClick={() => { localStorage.clear(); window.location.reload(); }}
                    className="bg-white border border-[#d0d5dd] hover:bg-gray-50 text-[#344054] px-4 py-2 rounded-[6px] transition-all duration-200 font-semibold text-sm shadow-sm"
                >
                    Güvenli Çıkış
                </button>
            </div>

            {/* Responsive Grid Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

                {/* Left Column - Main Content (8 cols) */}
                <div className="lg:col-span-8 space-y-6">
                    {/* Market Analysis - Clean & Modern */}
                    <div>
                        <MarketAnalysisTabs />
                    </div>

                    {/* Smart Transport Alarms with Map */}
                    <div className="bg-white border border-[#eaecf0] rounded-[6px] p-6 shadow-sm">
                        <SmartTransportContainerV2 />
                    </div>
                </div>

                {/* Right Column - Sidebar Content (4 cols) */}
                <div className="lg:col-span-4 space-y-6">
                    {/* Transit Advice - Sidebar Inset Card */}
                    <div className="bg-[#f9fafb] border border-[#eaecf0] rounded-[6px] p-6">
                        <h3 className="text-sm font-bold text-[#475467] uppercase tracking-wider mb-4 border-b border-[#eaecf0] pb-2">Ulaşım Tavsiyesi</h3>
                        {transitLoading ? (
                            <LoadingSpinner />
                        ) : transit ? (
                            <div className="space-y-6">
                                <div className="flex items-baseline space-x-2">
                                    <span className="text-5xl font-extrabold text-[#444ce7]">{transit.recommended_wakeup}</span>
                                    <span className="text-[#667085] text-xs font-semibold uppercase tracking-tighter">Uyanma</span>
                                </div>

                                <div className="space-y-3">
                                    <div className="flex justify-between p-3 bg-white border border-[#eaecf0] rounded-[6px]">
                                        <span className="text-[#667085] text-xs font-medium">Hedef Varış</span>
                                        <span className="text-[#101828] text-sm font-bold">{transit.target_arrival}</span>
                                    </div>
                                    <div className="flex justify-between p-3 bg-white border border-[#eaecf0] rounded-[6px]">
                                        <span className="text-[#667085] text-xs font-medium">Gecikme Payı</span>
                                        <span className="text-red-600 text-sm font-bold">+{transit.total_delay_added} dk</span>
                                    </div>
                                </div>

                                <div className="bg-white border border-[#eaecf0] rounded-[6px] p-4">
                                    <p className="text-xs font-bold text-[#101828] mb-3 uppercase tracking-widest">Gecikme Detayları</p>
                                    <ul className="space-y-3">
                                        {transit.reasons.map((r, i) => (
                                            <li key={i} className="flex items-start text-[#475467] text-xs leading-relaxed group">
                                                <div className="mt-1 mr-2 flex-shrink-0 w-1.5 h-1.5 bg-[#444ce7] rounded-full group-hover:scale-125 transition-transform"></div>
                                                {r}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-10">
                                <span className="text-3xl opacity-20 grayscale">🚌</span>
                                <p className="text-[#667085] text-xs mt-3">Bugünlük ulaşım önerisi bulunmuyor</p>
                            </div>
                        )}
                    </div>

                    {/* Event Bar - Side fixed or integrated */}
                    <div className="bg-white border border-[#eaecf0] rounded-[6px] overflow-hidden">
                        <div className="p-4 bg-[#f9fafb] border-b border-[#eaecf0]">
                            <h3 className="text-sm font-bold text-[#101828]">Ekinlik Takvimi</h3>
                        </div>
                        <div className="p-2">
                            <EventBar />
                        </div>
                    </div>
                </div>
            </div>

            {/* Float Notifications */}
            <AlarmNotification />
        </div>
    );
}
