
import React, { useEffect, useState } from 'react';
import api from '../api';

const EventBar = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const response = await api.get('/etkinlik/events?limit=10');
                setEvents(response.data);
            } catch (error) {
                console.error("Error fetching events:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchEvents();
    }, []);

    if (loading) return <div className="p-4 text-center text-gray-500">Etkinlikler yükleniyor...</div>;
    if (events.length === 0) return null;

    return (
        <div className="bg-white shadow-md rounded-lg p-4 mt-6">
            <h2 className="text-xl font-bold mb-4 text-purple-700">Kültür ve Sanat Etkinlikleri</h2>
            <div className="flex overflow-x-auto space-x-4 pb-4">
                {events.map((event) => (
                    <div key={event.id} className="min-w-[250px] max-w-[250px] bg-gray-50 rounded p-3 border border-gray-200 flex flex-col justify-between">
                        <div>
                            <h3 className="font-semibold text-md truncate" title={event.name}>{event.name}</h3>
                            <p className="text-sm text-gray-600 mt-1">{event.venue?.name}</p>
                            <p className="text-xs text-gray-500 mt-1">{new Date(event.start).toLocaleDateString()}</p>
                        </div>
                        <a
                            href={event.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-3 text-xs bg-purple-600 text-white py-1 px-2 rounded text-center hover:bg-purple-700 transition"
                        >
                            Detaylar
                        </a>
                    </div>
                ))}
            </div>
            <div className="text-right mt-2">
                <span className="text-xs text-gray-400 italic">İçerikler <strong>etkinlik.io</strong>'dan alınmıştır</span>
            </div>
        </div>
    );
};

export default EventBar;
