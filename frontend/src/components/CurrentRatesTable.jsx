import React, { useEffect, useState } from 'react';
import api from '../api';

export default function CurrentRatesTable() {
    const [rates, setRates] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchRates = async () => {
        try {
            const response = await api.get('/market-analysis/current-rates');
            if (response.data.success) {
                setRates(response.data.data);
            }
        } catch (error) {
            console.error('Kur çekme hatası:', error);
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
            <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400"></div>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-2 gap-6">
            {rates.map((rate) => (
                <div 
                    key={rate.symbol} 
                    className="bg-white border border-gray-200 rounded-lg p-6"
                >
                    <div className="text-sm text-gray-500 mb-2">{rate.name}</div>
                    <div className="text-3xl font-bold text-gray-900 mb-2">
                        {rate.price.toLocaleString('tr-TR', { 
                            minimumFractionDigits: 2, 
                            maximumFractionDigits: 2 
                        })}
                    </div>
                    <div className={`text-sm font-semibold ${
                        rate.daily_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                        {rate.daily_change_percent >= 0 ? '↑' : '↓'} 
                        {Math.abs(rate.daily_change_percent).toFixed(2)}%
                    </div>
                </div>
            ))}
        </div>
    );
}
