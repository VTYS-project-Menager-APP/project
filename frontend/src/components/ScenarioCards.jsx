import React, { useEffect, useState } from 'react';
import api from '../api';

export default function ScenarioCards() {
    const [scenarios, setScenarios] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchScenarios = async () => {
            try {
                const response = await api.get('/market-analysis/scenarios');
                if (response.data.success) {
                    setScenarios(response.data.data);
                }
            } catch (error) {
                console.error('Scenarios fetch error:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchScenarios();
    }, []);

    if (loading) return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
                <div key={i} className="animate-pulse bg-gray-50 h-32 rounded-[6px] border border-[#eaecf0]"></div>
            ))}
        </div>
    );

    return (
        <div className="space-y-4">
            <h3 className="text-sm font-bold text-[#475467] uppercase tracking-wider flex items-center gap-2">
                Olası Senaryolar
                <span className="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded text-gray-500 font-medium">SİMÜLASYON</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {scenarios.map((s) => (
                    <div
                        key={s.id}
                        className={`group relative border border-[#eaecf0] rounded-[6px] p-4 bg-white transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 cursor-pointer`}
                    >
                        {/* Hover accent */}
                        <div className={`absolute top-0 left-0 w-1 h-full rounded-l-[6px] ${s.type === 'expected' ? 'bg-[#444ce7]' :
                            s.type === 'surprise' ? 'bg-[#d92d20]' : 'bg-[#f79009]'
                            }`}></div>

                        <div className="mb-3">
                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-[4px] ${s.type === 'expected' ? 'bg-[#eef4ff] text-[#444ce7]' :
                                s.type === 'surprise' ? 'bg-[#fef3f2] text-[#d92d20]' : 'bg-[#fffaeb] text-[#b54708]'
                                }`}>
                                {s.probability}
                            </span>
                        </div>

                        <h4 className="text-sm font-bold text-[#101828] mb-1 group-hover:text-[#444ce7] transition-colors">{s.title}</h4>
                        <div className="flex items-baseline gap-2 mb-2">
                            <span className="text-xs font-black text-[#101828]">{s.impact}</span>
                            <span className="text-[10px] text-[#667085] font-bold uppercase tracking-widest">Tahmin</span>
                        </div>

                        <p className="text-[11px] font-medium text-[#475467] leading-relaxed italic bg-gray-50 p-2 rounded border border-[#f2f4f7]">
                            "{s.advice}"
                        </p>

                        <div className="mt-4 pt-3 border-t border-[#f2f4f7] flex items-center justify-between">
                            <span className="text-[10px] text-[#98a2b3] font-bold uppercase tracking-tight">Strateji</span>
                            <span className="text-[10px] text-[#444ce7] font-extrabold group-hover:underline">Detaylar →</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
