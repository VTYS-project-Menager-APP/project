import React, { useState } from 'react';
import CurrentRatesTable from './CurrentRatesTable';
import MarketPulse from './MarketPulse';
import ScenarioCards from './ScenarioCards';
import EventImpactList from './EventImpactList';
import UpcomingEventsList from './UpcomingEventsList';

export default function MarketAnalysisTabs() {
    const [view, setView] = useState('overview'); // 'overview' or 'detailed'

    return (
        <div className="w-full space-y-8">
            {/* View Switcher - Minimalist */}
            <div className="flex justify-between items-center mb-2">
                <div className="flex space-x-1 bg-[#f2f4f7] p-1 rounded-[6px] inline-flex">
                    <button
                        onClick={() => setView('overview')}
                        className={`px-4 py-1.5 text-xs font-bold transition-all duration-200 rounded-[4px] ${view === 'overview'
                            ? 'bg-white text-[#101828] shadow-sm'
                            : 'text-[#667085] hover:text-[#101828]'
                            }`}
                    >
                        Özet Görünüm
                    </button>
                    <button
                        onClick={() => setView('detailed')}
                        className={`px-4 py-1.5 text-xs font-bold transition-all duration-200 rounded-[4px] ${view === 'detailed'
                            ? 'bg-white text-[#101828] shadow-sm'
                            : 'text-[#667085] hover:text-[#101828]'
                            }`}
                    >
                        Detaylı Analiz
                    </button>
                </div>
            </div>

            {view === 'overview' ? (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
                    {/* Top Section: Compact Market Rates */}
                    <div className="grid grid-cols-1 gap-4">
                        <CurrentRatesTable compact={true} />
                    </div>

                    {/* Middle Section: Market Pulse (The "Why") */}
                    <MarketPulse />

                    {/* Bottom Section: Scenarios */}
                    <ScenarioCards />
                </div>
            ) : (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="bg-white border border-[#eaecf0] rounded-[6px] p-4">
                            <h3 className="text-sm font-bold text-[#101828] mb-4 uppercase tracking-widest border-b pb-2">Gelecek Olaylar</h3>
                            <UpcomingEventsList />
                        </div>
                        <div className="bg-white border border-[#eaecf0] rounded-[6px] p-4">
                            <h3 className="text-sm font-bold text-[#101828] mb-4 uppercase tracking-widest border-b pb-2">Olay Analizi</h3>
                            <EventImpactList showAll={true} />
                        </div>
                    </div>
                    <div className="bg-white border border-[#eaecf0] rounded-[6px] p-4">
                        <h3 className="text-sm font-bold text-[#101828] mb-4 uppercase tracking-widest border-b pb-2">Geçmiş Analizler (Korelasyon)</h3>
                        <EventImpactList isHistorical={true} />
                    </div>
                </div>
            )}
        </div>
    );
}
