import React, { useState, useEffect } from 'react';
import api from '../api';
import { Clock, Bus, MapPin, Bell, Plus, Trash2, CheckCircle, AlertCircle, Map, X, Navigation2 } from 'lucide-react';
import AlarmSound from './AlarmSound';
import MapPicker from './MapPicker';

const SmartTransportContainerV2 = () => {
  const [alarms, setAlarms] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeAlarm, setActiveAlarm] = useState(null);
  
  // Map picker states
  const [showOriginMap, setShowOriginMap] = useState(false);
  const [showDestMap, setShowDestMap] = useState(false);
  
  // Form states
  const [formData, setFormData] = useState({
    alarm_name: '',
    origin_location: '',
    destination_location: '',
    origin_coords: null, // { lat, lon }
    dest_coords: null,   // { lat, lon }
    target_arrival_time: '',
    travel_time_to_stop: 10,
    selected_hat_kodlari: []
  });

  const [searchingRoutes, setSearchingRoutes] = useState(false);
  const [availableRoutes, setAvailableRoutes] = useState([]);
  const [indirectRoutes, setIndirectRoutes] = useState([]); // New state for indirect routes
  const [showIndirectRoutes, setShowIndirectRoutes] = useState(false); // Toggle visibility
  const [routeSearchResult, setRouteSearchResult] = useState(null);

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
        setActiveAlarm(response.data.triggered_alarms[0]);
      }
    } catch (error) {
      console.error('Active alarm check error:', error);
    }
  };

  // Handle origin location selection from map
  const handleOriginSelect = (location) => {
    setFormData({
      ...formData,
      origin_location: location.address,
      origin_coords: { lat: location.lat, lon: location.lng }
    });
    setShowOriginMap(false);
    
    // If both locations selected, auto-search routes
    if (formData.dest_coords) {
      handleSearchRoutesByLocation({
        lat: location.lat,
        lon: location.lng
      }, formData.dest_coords);
    }
  };

  // Handle destination location selection from map
  const handleDestSelect = (location) => {
    setFormData({
      ...formData,
      destination_location: location.address,
      dest_coords: { lat: location.lat, lon: location.lng }
    });
    setShowDestMap(false);
    
    // If both locations selected, auto-search routes
    if (formData.origin_coords) {
      handleSearchRoutesByLocation(
        formData.origin_coords,
        { lat: location.lat, lon: location.lng }
      );
    }
  };

  // Search routes based on coordinates
  const handleSearchRoutesByLocation = async (originCoords, destCoords) => {
    setSearchingRoutes(true);
    try {
      const response = await api.post('/transport/smart/routes/search-by-location', {
        origin_lat: originCoords.lat,
        origin_lon: originCoords.lon,
        dest_lat: destCoords.lat,
        dest_lon: destCoords.lon,
        radius_meters: 500
      });
      
      const routes = response.data.available_routes || [];
      const indirect = response.data.origin_only_routes || [];
      
      setAvailableRoutes(routes);
      setIndirectRoutes(indirect);
      setRouteSearchResult(response.data);
      
      // Auto-select all direct routes
      setFormData(prev => ({
        ...prev,
        selected_hat_kodlari: routes.map(r => r.hat_kodu)
      }));
      
      if (routes.length === 0) {
        if (indirect.length > 0) {
          setShowIndirectRoutes(true); // Auto show indirect if no direct
          alert('Direkt hat bulunamadı, ancak bu yöne giden diğer hatlar listelendi (Aktarma gerekebilir).');
        } else {
          alert('Bu konumlar arasında otobüs hattı bulunamadı. Lütfen farklı konumlar deneyin.');
        }
      } else {
        setShowIndirectRoutes(false); // Hide indirect by default if direct exists
      }
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

    if (!formData.origin_coords || !formData.dest_coords) {
      alert('Lütfen haritadan başlangıç ve hedef konumlarını seçin!');
      return;
    }

    try {
      await api.post('/transport/smart/alarms', {
        alarm_name: formData.alarm_name,
        origin_location: formData.origin_location,
        destination_location: formData.destination_location,
        target_arrival_time: formData.target_arrival_time,
        travel_time_to_stop: formData.travel_time_to_stop,
        selected_hat_kodlari: formData.selected_hat_kodlari,
        // Store coordinates for future reference (optional)
        origin_durak_kodu: `COORD_${formData.origin_coords.lat.toFixed(4)}_${formData.origin_coords.lon.toFixed(4)}`,
        destination_durak_kodu: `COORD_${formData.dest_coords.lat.toFixed(4)}_${formData.dest_coords.lon.toFixed(4)}`
      });
      
      setShowCreateForm(false);
      setFormData({
        alarm_name: '',
        origin_location: '',
        destination_location: '',
        origin_coords: null,
        dest_coords: null,
        target_arrival_time: '',
        travel_time_to_stop: 10,
        selected_hat_kodlari: []
      });
      setAvailableRoutes([]);
      setRouteSearchResult(null);
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
              📍 Haritadan Konum Seç - Tüm Hatları Bul
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
            📍 Haritadan Konum Seç - Akıllı Alarm Oluştur
          </h3>

          {/* Alarm Name */}
          <div className="space-y-1">
            <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
              Alarm Adı
            </label>
            <input
              type="text"
              className="w-full bg-white border border-[#d0d5dd] rounded-[6px] px-3 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none transition-all"
              placeholder="Örn: İşe Gidiş Sabah"
              value={formData.alarm_name}
              onChange={(e) => setFormData({ ...formData, alarm_name: e.target.value })}
            />
          </div>

          {/* Location Selection with Map */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Origin Location */}
            <div className="space-y-2">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Başlangıç Konumu
              </label>
              <button
                onClick={() => setShowOriginMap(true)}
                className="w-full bg-white border-2 border-dashed border-[#444ce7] hover:bg-[#444ce7]/5 rounded-[6px] px-4 py-3 text-sm transition-all flex items-center gap-3 group"
              >
                <div className="bg-[#444ce7] group-hover:scale-110 transition-transform p-2 rounded-full">
                  <Map size={18} className="text-white" />
                </div>
                <div className="text-left flex-1">
                  {formData.origin_location ? (
                    <>
                      <p className="text-[9px] font-black text-[#444ce7] uppercase">SEÇİLDİ</p>
                      <p className="text-xs font-bold text-[#101828] truncate">{formData.origin_location.split(',')[0]}</p>
                    </>
                  ) : (
                    <>
                      <p className="text-xs font-bold text-[#475467]">Haritadan Seç</p>
                      <p className="text-[9px] text-[#667085]">Başlangıç noktanızı seçin</p>
                    </>
                  )}
                </div>
              </button>
            </div>

            {/* Destination Location */}
            <div className="space-y-2">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                Hedef Konum (İş Yeri)
              </label>
              <button
                onClick={() => setShowDestMap(true)}
                className="w-full bg-white border-2 border-dashed border-[#10b981] hover:bg-[#10b981]/5 rounded-[6px] px-4 py-3 text-sm transition-all flex items-center gap-3 group"
              >
                <div className="bg-[#10b981] group-hover:scale-110 transition-transform p-2 rounded-full">
                  <MapPin size={18} className="text-white" />
                </div>
                <div className="text-left flex-1">
                  {formData.destination_location ? (
                    <>
                      <p className="text-[9px] font-black text-[#10b981] uppercase">SEÇİLDİ</p>
                      <p className="text-xs font-bold text-[#101828] truncate">{formData.destination_location.split(',')[0]}</p>
                    </>
                  ) : (
                    <>
                      <p className="text-xs font-bold text-[#475467]">Haritadan Seç</p>
                      <p className="text-[9px] text-[#667085]">İş yerinizi seçin</p>
                    </>
                  )}
                </div>
              </button>
            </div>
          </div>

          {/* Route Search Status */}
          {searchingRoutes && (
            <div className="bg-blue-50 border border-blue-200 rounded-[6px] p-4 flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-3 border-blue-600 border-t-transparent"></div>
              <div>
                <p className="text-sm font-bold text-blue-900">Otobüs hatları aranıyor...</p>
                <p className="text-xs text-blue-700">Yakınındaki duraklar ve hatlar bulunuyor</p>
              </div>
            </div>
          )}

          {/* Available Routes (Direct) */}
          {availableRoutes.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[10px] font-black text-[#10b981] uppercase tracking-wider flex items-center gap-1">
                  <CheckCircle size={12} />
                  Direkt Giden Hatlar ({availableRoutes.length})
                </label>
                <button
                  onClick={() => {
                    const allSelected = availableRoutes.every(r => 
                      formData.selected_hat_kodlari.includes(r.hat_kodu)
                    );
                    setFormData(prev => ({
                      ...prev,
                      selected_hat_kodlari: allSelected 
                        ? prev.selected_hat_kodlari.filter(k => !availableRoutes.find(ar => ar.hat_kodu === k))
                        : [...new Set([...prev.selected_hat_kodlari, ...availableRoutes.map(r => r.hat_kodu)])]
                    }));
                  }}
                  className="text-[9px] font-black text-[#444ce7] hover:text-[#3538cd] uppercase tracking-wider"
                >
                  {availableRoutes.every(r => formData.selected_hat_kodlari.includes(r.hat_kodu)) ? 
                    'SEÇİMİ KALDIR' : 'HEPSİNİ SEÇ'}
                </button>
              </div>
              
              <div className="bg-white border border-[#eaecf0] rounded-[6px] p-4">
                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                  {availableRoutes.map((route) => (
                    <button
                      key={route.hat_kodu}
                      onClick={() => handleToggleRoute(route.hat_kodu)}
                      className={`px-3 py-2 rounded-[6px] text-xs font-black transition-all ${
                        formData.selected_hat_kodlari.includes(route.hat_kodu)
                          ? 'bg-[#10b981] text-white shadow-md scale-105'
                          : 'bg-[#f9fafb] border border-[#d0d5dd] text-[#475467] hover:border-[#10b981]'
                      }`}
                    >
                      {route.hat_kodu}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Indirect Routes (Transfer Needed) */}
          {(showIndirectRoutes || indirectRoutes.length > 0) && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between cursor-pointer" onClick={() => setShowIndirectRoutes(!showIndirectRoutes)}>
                <label className="text-[10px] font-black text-[#f59e0b] uppercase tracking-wider flex items-center gap-1">
                  <Navigation2 size={12} />
                  Diğer Hatlar / Aktarmalı ({indirectRoutes.length})
                </label>
                <span className="text-[9px] text-[#667085] underline">
                  {showIndirectRoutes ? 'Gizle' : 'Göster'}
                </span>
              </div>
              
              {showIndirectRoutes && (
                <div className="bg-orange-50/50 border border-orange-100 rounded-[6px] p-4">
                  <p className="text-[10px] text-orange-800 mb-3 font-medium">
                    ⚠️ Bu hatlar doğrudan hedefe gitmeyebilir. Aktarma yapmanız gerekebilir.
                  </p>
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                    {indirectRoutes.map((route) => (
                      <button
                        key={route.hat_kodu}
                        onClick={() => handleToggleRoute(route.hat_kodu)}
                        className={`px-3 py-2 rounded-[6px] text-xs font-black transition-all ${
                          formData.selected_hat_kodlari.includes(route.hat_kodu)
                            ? 'bg-[#f59e0b] text-white shadow-md scale-105'
                            : 'bg-white border border-orange-200 text-[#475467] hover:border-[#f59e0b]'
                        }`}
                      >
                        {route.hat_kodu}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Time Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-black text-[#475467] uppercase tracking-wider">
                İşe Varış Saati (HH:MM)
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
              className="bg-[#444ce7] hover:bg-[#3538cd] text-white px-6 py-2 rounded-[6px] text-xs font-bold transition-all shadow-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleCreateAlarm}
              disabled={!formData.origin_coords || !formData.dest_coords || formData.selected_hat_kodlari.length === 0}
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
            <Map size={32} className="text-[#98a2b3] mb-3" />
            <p className="text-xs font-bold text-[#475467] uppercase tracking-widest">
              Henüz akıllı alarmınız yok
            </p>
            <p className="text-[10px] text-[#98a2b3] mt-1">
              Haritadan konum seçin ve otomatik hat eşleştirme ile alarm kurun
            </p>
          </div>
        ) : (
          alarms.map((alarm) => (
            <div
              key={alarm.alarm_id}
              className={`bg-white border rounded-[6px] overflow-hidden transition-all hover:shadow-md ${
                alarm.should_trigger ? 'border-red-400 shadow-lg shadow-red-100 animate-pulse' : 'border-[#eaecf0]'
              }`}
            >
              {/* Header */}
              <div className="p-4 bg-[#fcfcfd] border-b border-[#eaecf0] flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div
                    className={`px-3 py-1 rounded-[4px] text-[9px] font-black uppercase tracking-wider flex items-center gap-1.5 border ${getStatusColor(
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
                    <span className="text-[#101828] font-bold truncate">{alarm.origin}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin size={12} className="text-[#10b981]" />
                    <span className="text-[#667085] font-semibold">Nereye:</span>
                    <span className="text-[#101828] font-bold truncate">{alarm.destination}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock size={12} className="text-[#f97316]" />
                    <span className="text-[#667085] font-semibold">Hedef Saat:</span>
                    <span className="text-[#101828] font-bold">{alarm.target_arrival_time}</span>
                  </div>
                </div>

                {/* Status Message */}
                <div
                  className={`p-3 rounded-[6px] text-[10px] font-bold border ${
                    alarm.should_trigger
                      ? 'bg-red-50 text-red-700 border-red-200'
                      : 'bg-[#f2f4f7] text-[#475467] border-[#eaecf0]'
                  }`}
                >
                  {alarm.message}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Map Picker Modals */}
      {showOriginMap && (
        <MapPicker
          isOpen={showOriginMap}
          onClose={() => setShowOriginMap(false)}
          onSelectLocation={handleOriginSelect}
          title="Başlangıç Konumu Seç"
          type="origin"
        />
      )}

      {showDestMap && (
        <MapPicker
          isOpen={showDestMap}
          onClose={() => setShowDestMap(false)}
          onSelectLocation={handleDestSelect}
          title="Hedef Konum Seç (İş Yeri)"
          type="destination"
          initialPosition={formData.origin_coords}
        />
      )}

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

export default SmartTransportContainerV2;

