import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, Circle, Popup } from 'react-leaflet';
import { MapPin, X, Navigation, Check, Bus } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import api from '../api';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom marker icons
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"><div style="width: 10px; height: 10px; background: white; border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);"></div></div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
  });
};

const originIcon = createCustomIcon('#444ce7'); // Blue for origin
const destinationIcon = createCustomIcon('#10b981'); // Green for destination

// Stop icon
const stopIcon = L.divIcon({
  className: 'stop-marker',
  html: `<div style="background-color: #f97316; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6v6"></path><path d="M15 6v6"></path><path d="M2 12h19.6"></path><path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"></path><circle cx="7" cy="18" r="2"></circle><path d="M9 18h5"></path><circle cx="17" cy="18" r="2"></circle></svg></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

// Component to handle map clicks
const MapClickHandler = ({ onLocationSelect }) => {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onLocationSelect({ lat, lng });
    },
  });
  return null;
};

const MapPicker = ({ 
  isOpen, 
  onClose, 
  onSelectLocation, 
  title = "Konum Seç",
  initialPosition = null,
  type = 'origin' // 'origin' or 'destination'
}) => {
  // Istanbul center as default
  const [position, setPosition] = useState(initialPosition || { lat: 41.0082, lng: 28.9784 });
  const [selectedPosition, setSelectedPosition] = useState(initialPosition);
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [stops, setStops] = useState([]);
  const [selectedStopLines, setSelectedStopLines] = useState([]);
  const [loadingLines, setLoadingLines] = useState(false);
  const mapRef = useRef(null);

  // Fetch lines passing through a stop
  const fetchStopRoutes = async (durakKodu) => {
    setLoadingLines(true);
    setSelectedStopLines([]);
    try {
      const response = await api.get(`/transport/smart/durak/${durakKodu}/hatlar`);
      setSelectedStopLines(response.data.hatlar || []);
    } catch (error) {
      console.error('Error fetching stop routes:', error);
    } finally {
      setLoadingLines(false);
    }
  };

  // Fetch nearby stops
  const fetchNearbyStops = async (lat, lng) => {
    try {
      const response = await api.get('/transport/smart/nearby-stops', {
        params: { lat, lon: lng, radius: 500 }
      });
      setStops(response.data.stops || []);
    } catch (error) {
      console.error('Error fetching nearby stops:', error);
    }
  };

  // Get user's current location
  const getCurrentLocation = () => {
    setLoading(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newPos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setPosition(newPos);
          setSelectedPosition(newPos);
          reverseGeocode(newPos);
          fetchNearbyStops(newPos.lat, newPos.lng);
          setLoading(false);
        },
        (error) => {
          console.error('Error getting location:', error);
          setLoading(false);
          alert('Konum alınamadı. Lütfen manuel olarak seçin.');
        }
      );
    } else {
      alert('Tarayıcınız konum servislerini desteklemiyor.');
      setLoading(false);
    }
  };

  // Reverse geocoding - Convert coordinates to address
  const reverseGeocode = async (coords) => {
    try {
      // Using Nominatim (OpenStreetMap) for free geocoding
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.lat}&lon=${coords.lng}&zoom=18&addressdetails=1`,
        {
          headers: {
            'Accept-Language': 'tr'
          }
        }
      );
      const data = await response.json();
      
      if (data.display_name) {
        setAddress(data.display_name);
      }
    } catch (error) {
      console.error('Geocoding error:', error);
      setAddress('Adres bulunamadı');
    }
  };

  // Forward geocoding - Search address
  const searchAddress = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}, Istanbul&limit=5`,
        {
          headers: {
            'Accept-Language': 'tr'
          }
        }
      );
      const data = await response.json();

      if (data.length > 0) {
        const newPos = {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon)
        };
        setPosition(newPos);
        setSelectedPosition(newPos);
        setAddress(data[0].display_name);
        fetchNearbyStops(newPos.lat, newPos.lng);
      } else {
        alert('Adres bulunamadı. Lütfen farklı bir arama yapın.');
      }
    } catch (error) {
      console.error('Search error:', error);
      alert('Arama sırasında hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  // Handle map click
  const handleMapClick = (coords) => {
    setSelectedPosition(coords);
    reverseGeocode(coords);
    fetchNearbyStops(coords.lat, coords.lng);
  };

  // Confirm selection
  const handleConfirm = () => {
    if (selectedPosition) {
      onSelectLocation({
        ...selectedPosition,
        address: address
      });
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-[12px] max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#444ce7] to-[#3538cd] p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 backdrop-blur p-2 rounded-full">
              <MapPin size={20} className="text-white" />
            </div>
            <div>
              <h3 className="text-lg font-black text-white tracking-tight">
                {title}
              </h3>
              <p className="text-xs text-white/80 font-semibold">
                {type === 'origin' ? 'Başlangıç noktanızı seçin' : 'Varış noktanızı seçin'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="bg-white/20 hover:bg-white/30 backdrop-blur p-2 rounded-full transition-all"
          >
            <X size={20} className="text-white" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-4 bg-[#f9fafb] border-b border-[#eaecf0]">
          <div className="flex gap-2">
            <input
              type="text"
              className="flex-1 bg-white border border-[#d0d5dd] rounded-[6px] px-4 py-2 text-sm focus:ring-2 focus:ring-[#444ce7]/20 outline-none"
              placeholder="Adres ara (örn: Kadıköy İskele, Taksim Meydanı)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchAddress()}
            />
            <button
              onClick={searchAddress}
              disabled={loading}
              className="bg-[#444ce7] hover:bg-[#3538cd] text-white px-4 py-2 rounded-[6px] text-xs font-bold transition-all disabled:opacity-50"
            >
              ARA
            </button>
            <button
              onClick={getCurrentLocation}
              disabled={loading}
              className="bg-[#10b981] hover:bg-[#059669] text-white px-4 py-2 rounded-[6px] text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Navigation size={16} />
              KONUMUM
            </button>
          </div>
        </div>

        {/* Map */}
        <div className="relative h-[400px]">
          {loading && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center">
              <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#444ce7] border-t-transparent"></div>
            </div>
          )}
          
          <MapContainer
            center={[position.lat, position.lng]}
            zoom={15}
            className="h-full w-full"
            ref={mapRef}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapClickHandler onLocationSelect={handleMapClick} />
            
            {/* Stops */}
            {stops.map((stop) => (
              <Marker
                key={stop.durak_kodu}
                position={[stop.lat, stop.lon]}
                icon={stopIcon}
                eventHandlers={{
                  click: () => {
                    handleMapClick({ lat: stop.lat, lng: stop.lon });
                    fetchStopRoutes(stop.durak_kodu);
                  },
                }}
              >
                <Popup>
                  <div className="min-w-[150px]">
                    <div className="text-xs font-black text-gray-900">{stop.durak_adi}</div>
                    <div className="text-[10px] text-gray-500 mb-2 font-mono">{stop.durak_kodu}</div>
                    
                    <div className="border-t border-gray-100 pt-2 mt-1">
                      <div className="flex items-center gap-1 mb-1.5">
                        <Bus size={10} className="text-blue-600" />
                        <span className="text-[9px] font-bold text-gray-600 uppercase">GEÇEN HATLAR</span>
                      </div>
                      
                      {loadingLines ? (
                        <div className="text-[9px] text-gray-400 animate-pulse">Yükleniyor...</div>
                      ) : (
                        <div className="flex flex-wrap gap-1">
                          {selectedStopLines.length > 0 ? selectedStopLines.map(line => (
                            <span 
                              key={line.hatKodu || line.hat_kodu || line} 
                              className="bg-blue-50 text-blue-700 border border-blue-100 text-[9px] font-bold px-1.5 py-0.5 rounded-[3px]"
                            >
                              {line.hatKodu || line.hat_kodu || line}
                            </span>
                          )) : (
                            <span className="text-[9px] text-gray-400 italic">Hat bilgisi bulunamadı</span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}

            {selectedPosition && (
              <>
                <Marker 
                  position={[selectedPosition.lat, selectedPosition.lng]}
                  icon={type === 'origin' ? originIcon : destinationIcon}
                />
                {/* Circle to show approximate area */}
                <Circle
                  center={[selectedPosition.lat, selectedPosition.lng]}
                  radius={200} // 200 meters
                  pathOptions={{
                    color: type === 'origin' ? '#444ce7' : '#10b981',
                    fillColor: type === 'origin' ? '#444ce7' : '#10b981',
                    fillOpacity: 0.1
                  }}
                />
              </>
            )}
          </MapContainer>
        </div>

        {/* Selected Address Display */}
        {selectedPosition && address && (
          <div className="p-4 bg-[#f9fafb] border-t border-[#eaecf0]">
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-[6px] ${
                type === 'origin' ? 'bg-[#444ce7]/10 text-[#444ce7]' : 'bg-[#10b981]/10 text-[#10b981]'
              }`}>
                <MapPin size={20} />
              </div>
              <div className="flex-1">
                <p className="text-[10px] font-black text-[#667085] uppercase tracking-wider mb-1">
                  SEÇİLEN KONUM
                </p>
                <p className="text-sm font-bold text-[#101828]">
                  {address}
                </p>
                <p className="text-xs text-[#667085] mt-1 font-mono">
                  {selectedPosition.lat.toFixed(6)}, {selectedPosition.lng.toFixed(6)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="p-4 bg-white border-t border-[#eaecf0] flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-bold text-[#475467] hover:bg-gray-100 rounded-[6px] transition-all"
          >
            İPTAL
          </button>
          <button
            onClick={handleConfirm}
            disabled={!selectedPosition}
            className="bg-[#10b981] hover:bg-[#059669] text-white px-6 py-2 rounded-[6px] text-sm font-bold transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            <Check size={16} />
            KONUMU ONAYLA
          </button>
        </div>

        {/* Info Tip */}
        <div className="px-4 pb-4">
          <div className="bg-blue-50 border border-blue-200 rounded-[6px] p-3">
            <p className="text-[10px] text-blue-900 font-semibold">
              💡 <span className="font-black">İPUCU:</span> Haritaya tıklayarak konum seçebilir, 
              adres arayabilir veya mevcut konumunuzu kullanabilirsiniz. 
              Seçilen konum etrafındaki duraklar otomatik bulunacak.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapPicker;

