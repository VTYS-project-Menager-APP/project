import React, { useState, useEffect } from 'react';
import api from '../api';
import { Clock, Bus, MapPin, Bell, Plus, Trash2, CheckCircle, AlertCircle, Search, X } from 'lucide-react';
import AlarmSound from './AlarmSound';

const SmartTransportContainer = () => {
  const [alarms, setAlarms] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeAlarm, setActiveAlarm] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({
    alarm_name: '',
    origin_location: '',
    destination_location: '',
    origin_durak_kodu: '',
    destination_durak_kodu: '',
    target_arrival_time: '',
    travel_time_to_stop: 10,
    selected_hat_kodlari: []
  });

  const [searchingRoutes, setSearchingRoutes] = useState(false);
  const [availableRoutes, setAvailableRoutes] = useState([]);

  useEffect(() => {
    fetchAlarms();
    // Check for active alarms every 30 seconds
    const interval = setInterval(checkActiveAlarms, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlarms = async () => {
    try {
      const response = await api.get('/transport/smart/alarms');
      setAlarms(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Alarm fetch error:', error);
      setLoading(false);
    }
  };

  const checkActiveAlarms = async () => {
    try {
      const response = await api.get('/transport/smart/check-active');
      if (response.data.has_active_trigger && response.data.triggered_alarms.length > 0) {
        // Trigger alarm notification
        setActiveAlarm(response.data.triggered_alarms[0]);
      }
    } catch (error) {
      console.error('Active alarm check error:', error);
    }
  };

  const handleSearchRoutes = async () => {
    if (!formData.origin_durak_kodu || !formData.destination_durak_kodu) {
      alert('Lütfen başlangıç ve hedef durak kodlarını girin!');
      return;
    }

    setSearchingRoutes(true);
    try {
      const response = await api.post('/transport/smart/routes/search', {
        origin_durak_kodu: formData.origin_durak_kodu,
        destination_durak_kodu: formData.destination_durak_kodu
      });
      setAvailableRoutes(response.data.routes || []);
    } catch (error) {
      console.error('Route search error:', error);
      alert('Hat arama sırasında hata oluştu!');
    } finally {
      setSearchingRoutes(false);
    }
  };

  const handleToggleRoute = (hatKodu) => {
    setFormData(prev => {
      const isSelected = prev.selected_hat_kodlari.includes(hatKodu);
      return {
        ...prev,
        selected_hat_kodlari: isSelected
          ? prev.selected_hat_kodlari.filter(h => h !== hatKodu)
          : [...prev.selected_hat_kodlari, hatKodu]
      };
    });
  };

  const handleCreateAlarm = async () => {
    if (!formData.alarm_name || !formData.target_arrival_time || formData.selected_hat_kodlari.length === 0) {
      alert('Lütfen tüm gerekli alanları doldurun!');
      return;
    }

    try {
      await api.post('/transport/smart/alarms', formData);
      setShowCreateForm(false);
      setFormData({
        alarm_name: '',
        origin_location: '',
        destination_location: '',
        origin_durak_kodu: '',
        destination_durak_kodu: '',
        target_arrival_time: '',
        travel_time_to_stop: 10,
        selected_hat_kodlari: []
      });
      setAvailableRoutes([]);
      fetchAlarms();
    } catch (error) {
      console.error('Create alarm error:', error);
      alert('Alarm oluşturma hatası!');
    }
  };

  const handleDeleteAlarm = async (alarmId) => {
    if (!confirm('Bu alarmı silmek istediğinizden emin misiniz?')) return;
    
    try {
      await api.delete(`/transport/smart/alarms/${alarmId}`);
      fetchAlarms();
    } catch (error) {
      console.error('Delete alarm error:', error);
      alert('Alarm silme hatası!');
    }
  };

  const handleToggleAlarmEnabled = async (alarmId, currentEnabled) => {
    try {
      await api.put(`/transport/smart/alarms/${alarmId}`, {
        alarm_enabled: !currentEnabled
      });
      fetchAlarms();
    } catch (error) {
      console.error('Toggle alarm error:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'triggered':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'ready':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'triggered':
        return <AlertCircle size={16} />;
      default:
        return <CheckCircle size={16} />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-[#f2f4f7] p-2 rounded-[6px] border border-[#eaecf0] text-[#444ce7]">
            <Bus size={24} />
          </div>
          <div>
            <h2 className="text-sm font-black text-[#101828] uppercase tracking-wider">
              Akıllı Ulaşım Alarmları
            </h2>
            <p className="text-[10px] text-[#667085] font-medium uppercase tracking-tighter">
              İBB Gerçek Zamanlı Otobüs Takibi
            </p>
          </div>
        </div>
        <button
          className="flex items-center gap-2 bg-[#444ce7] hover:bg-[#3538cd] text-white px-4 py-2 rounded-[6px] text-xs font-bold transition-all shadow-sm"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          <Plus size={16} />
          YENİ ALARM
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="bg-[#f9fafb] border border-[#eaecf0] p-6 rounded-[6px] space-y-4">
          <h3 className="text-xs font-black text-[#101828] uppercase tracking-widest border-b border-[#eaecf0] pb-2 mb-4">
            Akıllı Alarm Oluştur
          </h3>

          {/* Alarm Name */}
          <div className="space-y-1">
            <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
              Alarm Adı
            </label>
            <input
              type="text"
              className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
              placeholder="Örn: İşe Gidiş"
              value={formData.alarm_name}
              onChange={(e) => setFormData({ ...formData, alarm_name: e.target.value })}
            />
          </div>

          {/* Location Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Başlangıç Konumu
              </label>
              <input
                type="text"
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                placeholder="Ev adresi"
                value={formData.origin_location}
                onChange={(e) => setFormData({ ...formData, origin_location: e.target.value })}
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Hedef Konum
              </label>
              <input
                type="text"
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                placeholder="İş yeri adresi"
                value={formData.destination_location}
                onChange={(e) => setFormData({ ...formData, destination_location: e.target.value })}
              />
            </div>
          </div>

          {/* Durak Codes */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Başlangıç Durak Kodu
              </label>
              <input
                type="text"
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                placeholder="Örn: KYK101"
                value={formData.origin_durak_kodu}
                onChange={(e) => setFormData({ ...formData, origin_durak_kodu: e.target.value })}
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Hedef Durak Kodu
              </label>
              <input
                type="text"
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                placeholder="Örn: MAL202"
                value={formData.destination_durak_kodu}
                onChange={(e) => setFormData({ ...formData, destination_durak_kodu: e.target.value })}
              />
            </div>
          </div>

          {/* Search Routes Button */}
          <button
            className="w-full bg-[#10b981] hover:bg-[#059669] text-white px-4 py-2 rounded-[6px] text-xs font-bold transition-all flex items-center justify-center gap-2"
            onClick={handleSearchRoutes}
            disabled={searchingRoutes}
          >
            <Search size={14} />
            {searchingRoutes ? 'ARANIY OR...' : 'HATLARI BUL'}
          </button>

          {/* Available Routes */}
          {availableRoutes.length > 0 && (
            <div className="space-y-2">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Bulunan Hatlar (Birden fazla seçebilirsiniz)
              </label>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                {availableRoutes.map((route) => (
                  <button
                    key={route.hat_kodu}
                    onClick={() => handleToggleRoute(route.hat_kodu)}
                    className={`px-3 py-2 rounded-[6px] text-xs font-bold transition-all ${
                      formData.selected_hat_kodlari.includes(route.hat_kodu)
                        ? 'bg-[#444ce7] text-white'
                        : 'bg-white border border-[#d0d5dd] text-[#475467] hover:border-[#444ce7]'
                    }`}
                  >
                    {route.hat_kodu}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Time Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Varış Saati (HH:MM)
              </label>
              <input
                type="time"
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                value={formData.target_arrival_time}
                onChange={(e) => setFormData({ ...formData, target_arrival_time: e.target.value })}
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Durağa Yürüme Süresi (Dakika)
              </label>
              <input
                type="number"
                className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
                value={formData.travel_time_to_stop}
                onChange={(e) => setFormData({ ...formData, travel_time_to_stop: parseInt(e.target.value) })}
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              className="px-4 py-2 text-xs font-bold text-[#475467] hover:bg-gray-100 rounded-[6px] transition-all"
              onClick={() => setShowCreateForm(false)}
            >
              İPTAL
            </button>
            <button
              className="bg-[#444ce7] hover:bg-[#3538cd] text-white px-6 py-2 rounded-[6px] text-xs font-bold transition-all shadow-sm flex items-center gap-2"
              onClick={handleCreateAlarm}
            >
              <Bell size={14} />
              ALARMI OLUŞTUR
            </button>
          </div>
        </div>
      )}

      {/* Alarms List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-full py-10 text-center text-[#667085] text-xs font-bold animate-pulse">
            YÜKLENİYOR...
          </div>
        ) : alarms.length === 0 ? (
          <div className="col-span-full py-16 bg-[#f9fafb] border border-dashed border-[#eaecf0] rounded-[6px] text-center flex flex-col items-center">
            <Bus size={32} className="text-[#98a2b3] mb-3" />
            <p className="text-xs font-bold text-[#475467] uppercase tracking-widest">
              Henüz akıllı alarmınız yok
            </p>
            <p className="text-[10px] text-[#98a2b3] mt-1">
              Yeni alarm oluşturun ve otobüslerinizi otomatik takip edin
            </p>
          </div>
        ) : (
          alarms.map((alarm) => (
            <div
              key={alarm.alarm_id}
              className={`bg-white border rounded-[6px] overflow-hidden transition-all hover:shadow-md ${
                alarm.should_trigger ? 'border-red-400 shadow-lg shadow-red-100' : 'border-[#eaecf0]'
              }`}
            >
              {/* Header */}
              <div className="p-4 bg-[#fcfcfd] border-b border-[#eaecf0] flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div
                    className={`px-3 py-1 rounded-[4px] text-[9px] font-black uppercase tracking-wider flex items-center gap-1.5 ${getStatusColor(
                      alarm.status
                    )}`}
                  >
                    {getStatusIcon(alarm.status)}
                    {alarm.status}
                  </div>
                  <h3 className="text-sm font-black text-[#101828]">{alarm.alarm_name}</h3>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    className={`p-1.5 rounded-[4px] transition-all ${
                      alarm.alarm_enabled
                        ? 'text-[#10b981] hover:bg-[#10b981]/10'
                        : 'text-[#98a2b3] hover:bg-gray-100'
                    }`}
                    onClick={() => handleToggleAlarmEnabled(alarm.alarm_id, alarm.alarm_enabled)}
                  >
                    <Bell size={14} />
                  </button>
                  <button
                    className="p-1.5 text-[#98a2b3] hover:text-red-500 hover:bg-red-50 rounded-[4px] transition-all"
                    onClick={() => handleDeleteAlarm(alarm.alarm_id)}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="p-4 space-y-3">
                {/* Routes */}
                <div className="flex flex-wrap gap-2">
                  {alarm.routes.map((route) => (
                    <span
                      key={route.hat_kodu}
                      className="bg-[#444ce7] text-white text-[10px] font-black px-2 py-1 rounded-[4px]"
                    >
                      {route.hat_kodu}
                    </span>
                  ))}
                </div>

                {/* Locations */}
                <div className="space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <MapPin size={12} className="text-[#444ce7]" />
                    <span className="text-[#667085] font-semibold">Nereden:</span>
                    <span className="text-[#101828] font-bold">{alarm.origin}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin size={12} className="text-[#10b981]" />
                    <span className="text-[#667085] font-semibold">Nereye:</span>
                    <span className="text-[#101828] font-bold">{alarm.destination}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock size={12} className="text-[#f97316]" />
                    <span className="text-[#667085] font-semibold">Hedef Saat:</span>
                    <span className="text-[#101828] font-bold">{alarm.target_arrival_time}</span>
                  </div>
                </div>

                {/* Status Message */}
                <div
                  className={`p-3 rounded-[6px] text-[10px] font-bold ${
                    alarm.should_trigger
                      ? 'bg-red-50 text-red-700 border border-red-200 animate-pulse'
                      : 'bg-[#f2f4f7] text-[#475467] border border-[#eaecf0]'
                  }`}
                >
                  {alarm.message}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Alarm Sound Component */}
      {activeAlarm && (
        <AlarmSound
          alarmData={activeAlarm}
          onDismiss={() => setActiveAlarm(null)}
        />
      )}
    </div>
  );
};

export default SmartTransportContainer;

