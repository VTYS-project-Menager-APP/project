import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Tag, Upload, X } from 'lucide-react';
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
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);

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

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
      
      // Optional: Auto-detect color from image (Advanced feature, skipped for now)
    }
  };
  
  const clearFile = () => {
      setSelectedFile(null);
      setPreviewUrl(null);
  }

  const handleAddItem = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Create FormData
      const formData = new FormData();
      formData.append('category', newItem.category);
      formData.append('sub_category', newItem.sub_category);
      formData.append('primary_color_hex', newItem.primary_color_hex);
      if (newItem.material) formData.append('material', newItem.material);
      if (selectedFile) formData.append('file', selectedFile);

      await api.post('/style/closet/add-item', formData, {
          headers: {
              'Content-Type': 'multipart/form-data',
          },
      });

      setIsAdding(false);
      setNewItem({
        category: "Top",
        sub_category: "",
        primary_color_hex: "#000000",
        material: ""
      });
      clearFile();
      fetchCloset();
    } catch (error) {
      console.error("Add item error", error);
      alert("Kıyafet eklenirken hata oluştu.");
    } finally {
        setLoading(false);
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div className="space-y-4">
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
            
            {/* Image Upload Section */}
            <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Kıyafet Görseli</label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg bg-white relative hover:bg-gray-50 transition-colors">
                    {previewUrl ? (
                        <div className="relative w-full h-full flex justify-center">
                            <img src={previewUrl} alt="Preview" className="max-h-48 object-contain rounded-md" />
                            <button 
                                type="button" 
                                onClick={clearFile}
                                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 shadow-sm"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-1 text-center">
                            <Upload className="mx-auto h-12 w-12 text-gray-400" />
                            <div className="flex text-sm text-gray-600">
                                <label
                                    htmlFor="file-upload"
                                    className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                                >
                                    <span>Dosya Yükle</span>
                                    <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/*" onChange={handleFileChange} />
                                </label>
                                <p className="pl-1">veya sürükle bırak</p>
                            </div>
                            <p className="text-xs text-gray-500">PNG, JPG, GIF (max 5MB)</p>
                        </div>
                    )}
                </div>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              disabled={loading}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              İptal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading && <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>}
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
                        className="h-32 w-full rounded-md mb-3 flex items-center justify-center relative overflow-hidden bg-gray-100"
                    >
                         {item.image_url ? (
                             <img 
                                src={`http://localhost:8000${item.image_url}`} 
                                alt={item.sub_category} 
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                    e.target.onerror = null; 
                                    e.target.style.display = 'none';
                                    e.target.nextSibling.style.display = 'flex';
                                }}
                             />
                         ) : null}
                         
                         {/* Fallback Color Block (If no image or image error) */}
                         <div 
                            className="w-16 h-16 rounded-full shadow-lg absolute"
                            style={{ backgroundColor: item.primary_color_hex, display: item.image_url ? 'none' : 'flex' }}
                         ></div>
                         
                         {/* Small color tag if image exists */}
                         {item.image_url && (
                             <span 
                                className="absolute bottom-1 right-1 w-4 h-4 rounded-full border border-white shadow-sm"
                                style={{ backgroundColor: item.primary_color_hex }}
                             ></span>
                         )}
                    </div>
                    <div className="space-y-1">
                        <div className="text-xs font-bold text-gray-800 truncate">{item.sub_category}</div>
                        <div className="flex items-center gap-1.5">
                            <span className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded-full">{item.category}</span>
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
