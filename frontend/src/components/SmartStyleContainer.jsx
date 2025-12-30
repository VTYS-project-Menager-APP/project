import React, { useState, useEffect } from 'react';
import { Shirt, Palette, CloudSun, Plus, Search } from 'lucide-react';
import api from '../api';
import OutfitGeneratorCard from './OutfitGeneratorCard';
import VirtualClosetGrid from './VirtualClosetGrid';

const SmartStyleContainer = () => {
  const [activeTab, setActiveTab] = useState('recommendation');
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecommendation();
  }, []);

  const fetchRecommendation = async () => {
    setLoading(true);
    try {
      const res = await api.get('/style/daily-recommendation');
      setRecommendation(res.data);
    } catch (error) {
      console.error("Failed to fetch recommendation", error);
    } finally {
      setLoading(false);
    }
  };

  const syncPalettes = async () => {
      try {
          const res = await api.post('/style/sync-palettes');
          alert(res.data.message);
      } catch (error) {
          console.error(error);
          alert("Palet senkronizasyonu başarısız.");
      }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-gray-50 to-white">
        <div>
          <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <Palette className="w-5 h-5 text-indigo-600" />
            Smart Style Engine
          </h2>
          <p className="text-sm text-gray-500 mt-1">Sanzo Wada Renk Teorisi ile Kişisel Stil Asistanı</p>
        </div>
        <div className="flex gap-2">
            <button 
                onClick={syncPalettes}
                className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
                Paletleri Güncelle
            </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-100 px-6">
        <button
          onClick={() => setActiveTab('recommendation')}
          className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'recommendation'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <CloudSun className="w-4 h-4" />
          Günün Kombini
        </button>
        <button
          onClick={() => setActiveTab('closet')}
          className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'closet'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Shirt className="w-4 h-4" />
          Gardırop
        </button>
      </div>

      {/* Content */}
      <div className="p-6 min-h-[400px]">
        {activeTab === 'recommendation' && (
          <div className="max-w-2xl mx-auto">
            {loading ? (
               <div className="flex justify-center items-center h-64">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
               </div>
            ) : (
              <OutfitGeneratorCard recommendation={recommendation} />
            )}
          </div>
        )}

        {activeTab === 'closet' && (
          <VirtualClosetGrid />
        )}
      </div>
    </div>
  );
};

export default SmartStyleContainer;

