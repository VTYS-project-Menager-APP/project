import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Tag } from 'lucide-react';
import api from '../api';

const categories = ["Top", "Bottom", "Outerwear", "Shoes", "Accessory"];

const VirtualClosetGrid = () => {
  const [items, setItems] = useState([]);
  const [isAdding, setIsAdding] = useState(false);
  const [newItem, setNewItem] = useState({
    category: "Top",
    sub_category: "",
    primary_color_hex: "#000000",
    material: ""
  });

  useEffect(() => {
    fetchCloset();
  }, []);

  const fetchCloset = async () => {
    try {
      const res = await api.get('/style/closet');
      setItems(res.data);
    } catch (error) {
      console.error("Closet fetch error", error);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    try {
      await api.post('/style/closet/add-item', newItem);
      setIsAdding(false);
      setNewItem({
        category: "Top",
        sub_category: "",
        primary_color_hex: "#000000",
        material: ""
      });
      fetchCloset();
    } catch (error) {
      console.error("Add item error", error);
      alert("Kıyafet eklenirken hata oluştu.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Toolbar */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-700">Gardırobum ({items.length} Parça)</h3>
        <button
          onClick={() => setIsAdding(!isAdding)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          Yeni Ekle
        </button>
      </div>

      {/* Add Form */}
      {isAdding && (
        <form onSubmit={handleAddItem} className="bg-gray-50 p-6 rounded-xl border border-gray-200 animate-in fade-in slide-in-from-top-4 duration-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Kategori</label>
              <select
                className="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm py-2 px-3"
                value={newItem.category}
                onChange={(e) => setNewItem({...newItem, category: e.target.value})}
              >
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Alt Kategori (Örn: T-shirt)</label>
              <input
                type="text"
                required
                className="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm py-2 px-3"
                value={newItem.sub_category}
                onChange={(e) => setNewItem({...newItem, sub_category: e.target.value})}
                placeholder="Örn: Mavi Kot Ceket"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Renk</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  className="h-9 w-16 p-0 rounded border border-gray-300 cursor-pointer"
                  value={newItem.primary_color_hex}
                  onChange={(e) => setNewItem({...newItem, primary_color_hex: e.target.value})}
                />
                <span className="text-xs text-gray-500 font-mono">{newItem.primary_color_hex}</span>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Malzeme (Opsiyonel)</label>
              <input
                type="text"
                className="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm py-2 px-3"
                value={newItem.material}
                onChange={(e) => setNewItem({...newItem, material: e.target.value})}
                placeholder="Örn: Pamuk, Denim"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              İptal
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700"
            >
              Kaydet
            </button>
          </div>
        </form>
      )}

      {/* Grid */}
      {items.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
              <p className="text-gray-500">Henüz kıyafet eklenmemiş.</p>
          </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {items.map((item) => (
                <div key={item.id} className="bg-white border border-gray-100 rounded-lg p-3 hover:shadow-md transition-all group relative">
                    <div 
                        className="h-32 w-full rounded-md mb-3 flex items-center justify-center relative overflow-hidden"
                        style={{ backgroundColor: item.primary_color_hex + '20' }}
                    >
                         <div 
                            className="w-16 h-16 rounded-full shadow-lg"
                            style={{ backgroundColor: item.primary_color_hex }}
                         ></div>
                         <span className="absolute bottom-2 right-2 text-[10px] bg-white/80 px-1.5 py-0.5 rounded backdrop-blur-sm text-gray-600 font-mono">
                            {item.primary_color_hex}
                         </span>
                    </div>
                    <div className="space-y-1">
                        <div className="text-xs font-bold text-gray-800 truncate">{item.sub_category}</div>
                        <div className="flex items-center gap-1.5">
                            <span className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded-full">{item.category}</span>
                            {item.material && <span className="text-[10px] text-gray-400 truncate">{item.material}</span>}
                        </div>
                    </div>
                </div>
            ))}
        </div>
      )}
    </div>
  );
};

export default VirtualClosetGrid;

