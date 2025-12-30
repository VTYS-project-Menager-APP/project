import React from 'react';
import { Cloud, Sun, Info } from 'lucide-react';

const OutfitGeneratorCard = ({ recommendation }) => {
  if (!recommendation) return null;

  const { palette_name, colors, outfit, weather_info, advice } = recommendation;

  return (
    <div className="space-y-6">
      {/* Weather & Advice */}
      <div className="bg-indigo-50 rounded-xl p-4 flex items-start gap-4">
        <div className="bg-white p-2 rounded-lg shadow-sm">
           <Sun className="w-6 h-6 text-orange-500" />
        </div>
        <div>
            <div className="text-sm font-semibold text-indigo-900 mb-1">{weather_info}</div>
            <p className="text-sm text-indigo-700 leading-relaxed">{advice}</p>
        </div>
      </div>

      {/* Outfit Card */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
        {/* Color Palette Header */}
        <div className="h-24 flex relative">
          {colors && colors.map((color, idx) => (
            <div
              key={idx}
              className="flex-1 relative group"
              style={{ backgroundColor: color }}
            >
              <div className="opacity-0 group-hover:opacity-100 absolute inset-0 flex items-center justify-center bg-black/20 text-white text-xs font-mono transition-opacity">
                {color}
              </div>
            </div>
          ))}
          <div className="absolute bottom-2 right-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded text-xs font-semibold shadow-sm text-gray-700">
             {palette_name}
          </div>
        </div>

        {/* Clothing Items Grid */}
        <div className="p-6 grid grid-cols-2 gap-4">
          <OutfitItem 
            label="Üst Giyim" 
            item={outfit.top} 
            placeholder="Bir üst seçilemedi" 
          />
          <OutfitItem 
            label="Alt Giyim" 
            item={outfit.bottom} 
            placeholder="Uygun alt bulunamadı" 
          />
          <OutfitItem 
            label="Ayakkabı" 
            item={outfit.shoes} 
            placeholder="Uygun ayakkabı bulunamadı" 
          />
          <OutfitItem 
            label="Dış Giyim" 
            item={outfit.outerwear} 
            placeholder="Gerekli değil" 
            isOptional 
          />
        </div>
      </div>
    </div>
  );
};

const OutfitItem = ({ label, item, placeholder, isOptional }) => {
    if (!item && isOptional) return null;
    
    return (
        <div className="border border-gray-100 rounded-lg p-3 hover:border-gray-200 transition-colors">
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider block mb-2">{label}</span>
            {item ? (
                <div className="flex items-center gap-3">
                    <div 
                        className="w-10 h-10 rounded-full border border-gray-200 shadow-sm"
                        style={{ backgroundColor: item.primary_color_hex }}
                    ></div>
                    <div>
                        <div className="text-sm font-semibold text-gray-800">{item.sub_category}</div>
                        <div className="text-xs text-gray-500">{item.category}</div>
                    </div>
                </div>
            ) : (
                <div className="text-sm text-gray-400 italic flex items-center gap-2">
                    <Info className="w-4 h-4" />
                    {placeholder}
                </div>
            )}
        </div>
    )
}

export default OutfitGeneratorCard;

