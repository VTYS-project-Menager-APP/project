import React, { useState, useEffect } from 'react';
import api from '../api';
import { Clock, Bus, MapPin, Bell, Plus, Trash2 } from 'lucide-react';

const TransportContainer = () => {
  const [routes, setRoutes] = useState([]);
  const [alarms, setAlarms] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [travelTime, setTravelTime] = useState(10);
  const [notificationBefore, setNotificationBefore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [routesLoaded, setRoutesLoaded] = useState(false);

  useEffect(() => {
    if (!routesLoaded) {
      fetchRoutes();
    }
    fetchAlarms();
    const interval = setInterval(fetchAlarms, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchRoutes = async () => {
    try {
      const response = await api.get('/transport/routes');
      setRoutes(response.data);
      setRoutesLoaded(true);
    } catch (error) {
      console.error('Routes fetch error:', error);
    }
  };

  const fetchAlarms = async () => {
    try {
      const response = await api.get('/transport/alarms');
      setAlarms(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Alarms fetch error:', error);
      setLoading(false);
    }
  };

  const handleCreateAlarm = async () => {
    if (!selectedRoute) return;
    try {
      await api.post('/transport/alarms', {
        route_id: selectedRoute.id,
        travel_time_to_stop: parseInt(travelTime),
        notification_minutes_before: parseInt(notificationBefore)
      });
      setShowAddForm(false);
      setSelectedRoute(null);
      setTravelTime(10);
      fetchAlarms();
    } catch (error) {
      console.error('Create alarm error:', error);
    }
  };

  const handleDeleteAlarm = async (alarmId) => {
    if (!confirm('Bu alarmı silmek istediğinizden emin misiniz?')) return;
    try {
      await api.delete(`/transport/alarms/${alarmId}`);
      fetchAlarms();
    } catch (error) {
      console.error('Delete alarm error:', error);
    }
  };

  const formatTime = (datetime) => {
    if (!datetime) return '--:--';
    const date = new Date(datetime);
    return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  };

  const getTimeUntilText = (nextBus) => {
    if (!nextBus) return 'Bugün saat yok';
    const minutes = nextBus.minutes_until_departure;
    if (minutes < 0) return 'Otobüs kalktı';
    if (minutes === 0) return 'Şimdi kalkıyor!';
    if (minutes < 60) return `${minutes} dk içinde`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours} sa ${mins} dk içinde`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-[#f2f4f7] p-2 rounded-[6px] border border-[#eaecf0] text-[#444ce7]">
            <Bus size={24} />
          </div>
          <div>
            <h2 className="text-sm font-black text-[#101828] uppercase tracking-wider">Ulaşım Alarmları</h2>
            <p className="text-[10px] text-[#667085] font-medium uppercase tracking-tighter">Otobüslerinizi anlık takip edin</p>
          </div>
        </div>
        <button
          className="flex items-center gap-2 bg-[#444ce7] hover:bg-[#3538cd] text-white px-4 py-2 rounded-[6px] text-xs font-bold transition-all shadow-sm"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          <Plus size={16} />
          YENİ ALARM
        </button>
      </div>

      {showAddForm && (
        <div className="bg-[#f9fafb] border border-[#eaecf0] p-6 rounded-[6px] space-y-4 mb-6">
          <h3 className="text-xs font-black text-[#101828] uppercase tracking-widest border-b border-[#eaecf0] pb-2 mb-4">Yeni Alarm Oluştur</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">Hat Seçimi</label>
              <select
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                value={selectedRoute?.id || ''}
                onChange={(e) => {
                  const route = routes.find(r => r.id === parseInt(e.target.value));
                  setSelectedRoute(route);
                }}
              >
                <option value="">Hat Seçiniz...</option>
                {routes.map(route => (
                  <option key={route.id} value={route.id}>
                    {route.route_number} - {route.route_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">Yürüme Mesafesi (Dakika)</label>
              <input
                type="number"
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                value={travelTime}
                onChange={(e) => setTravelTime(e.target.value)}
              />
            </div>
          </div>

          {selectedRoute && (
            <div className="flex items-center gap-2 bg-white border border-[#eaecf0] p-3 rounded-[6px] text-xs text-[#101828] font-bold">
              <MapPin size={14} className="text-[#444ce7]" />
              <span>{selectedRoute.departure_location}</span>
              <span className="text-[#98a2b3]">→</span>
              <span>{selectedRoute.arrival_location}</span>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button className="px-4 py-2 text-xs font-bold text-[#475467] hover:bg-gray-100 rounded-[6px] transition-all" onClick={() => setShowAddForm(false)}>
              İPTAL
            </button>
            <button
              className="bg-[#10b981] hover:bg-[#059669] text-white px-6 py-2 rounded-[6px] text-xs font-bold transition-all shadow-sm flex items-center gap-2"
              onClick={handleCreateAlarm}
              disabled={!selectedRoute}
            >
              <Bell size={14} />
              ALARM KUR
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-full py-10 text-center text-[#667085] text-xs font-bold animate-pulse">YÜKLENİYOR...</div>
        ) : alarms.length === 0 ? (
          <div className="col-span-full py-16 bg-[#f9fafb] border border-dashed border-[#eaecf0] rounded-[6px] text-center flex flex-col items-center">
            <Bus size={32} className="text-[#98a2b3] mb-3" />
            <p className="text-xs font-bold text-[#475467] uppercase tracking-widest">Henüz bir alarmınız yok</p>
          </div>
        ) : (
          alarms.map(alarm => (
            <div key={alarm.alarm_id} className="bg-white border border-[#eaecf0] rounded-[6px] overflow-hidden group hover:border-[#444ce7] transition-all">
              <div className="p-4 bg-[#fcfcfd] border-b border-[#eaecf0] flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className="bg-[#101828] text-white text-[10px] font-black px-2 py-1 rounded-[4px]">
                    {alarm.route_number}
                  </div>
                  <h3 className="text-xs font-bold text-[#101828] truncate max-w-[150px]">{alarm.route_name}</h3>
                </div>
                <button
                  className="p-1.5 text-[#98a2b3] hover:text-red-500 hover:bg-red-50 rounded-[4px] transition-all"
                  onClick={() => handleDeleteAlarm(alarm.alarm_id)}
                >
                  <Trash2 size={14} />
                </button>
              </div>

              <div className="p-4 space-y-3">
                <div className="flex items-center gap-2 text-[10px] font-bold text-[#475467]">
                  <MapPin size={12} className="text-[#98a2b3]" />
                  <span className="truncate">{alarm.departure_location} → {alarm.arrival_location}</span>
                </div>

                {alarm.next_bus ? (
                  <div className="bg-[#f2f4f7] rounded-[6px] p-3 border border-[#eaecf0] group-hover:bg-[#eef4ff] group-hover:border-[#c7d7fe] transition-all">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[9px] font-black text-[#667085] uppercase tracking-widest">KALKIŞ</span>
                      <span className="text-sm font-black text-[#101828]">{formatTime(alarm.next_bus.next_departure)}</span>
                    </div>
                    <div className="text-center font-bold text-[#444ce7] text-[11px] mt-2">
                      {getTimeUntilText(alarm.next_bus)}
                    </div>

                    {alarm.next_bus.minutes_until_departure <= alarm.travel_time_to_stop + 5 &&
                      alarm.next_bus.minutes_until_departure > 0 && (
                        <div className="mt-2 py-1.5 bg-[#fef3f2] text-[#b42318] rounded-[4px] text-[9px] font-black text-center uppercase tracking-tighter animate-pulse border border-[#fecdca]">
                          Hemen çıkarsan yetişebilirsin!
                        </div>
                      )}
                  </div>
                ) : (
                  <div className="py-4 text-center text-[10px] font-bold text-[#98a2b3] uppercase tracking-widest bg-gray-50 rounded-[6px]">
                    Sefer Bulunmuyor
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TransportContainer;
