import React, { useEffect, useRef, useState } from 'react';
import { Bell, X, BellRing } from 'lucide-react';

/**
 * AlarmSound Component
 * Plays alarm sound and shows notification when transport alarm triggers
 */
const AlarmSound = ({ alarmData, onDismiss }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (alarmData && !isPlaying) {
      playAlarm();
    }
  }, [alarmData]);

  const playAlarm = () => {
    if (audioRef.current) {
      audioRef.current.play().catch(err => {
        console.error('Audio playback error:', err);
      });
      setIsPlaying(true);
    }
  };

  const stopAlarm = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
    if (onDismiss) {
      onDismiss();
    }
  };

  if (!alarmData) return null;

  return (
    <>
      {/* Audio element - browser-based alarm sound */}
      <audio
        ref={audioRef}
        loop
        onEnded={() => setIsPlaying(false)}
      >
        {/* Using a data URL for a simple beep sound */}
        <source
          src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIGGS57OihUhELTKXh8bllHgU2jdXvy3cqBSh+zPLaizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy2Io5ChVCnODxu2cfBTCJ0fPXjz8KFWSz6OmlVxELTqXh8blkHAU2jdXvy3cqBSh+zPLYizsKE1u06OunWBMKQ5zf8sFuJAUti9Hx1Y1ACRVjuuzoqVgSCkud4PG5ZBwFN4/W88x2KgUofcvy"
          type="audio/wav"
        />
      </audio>

      {/* Fullscreen overlay notification */}
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
        <div className="bg-white rounded-[12px] max-w-md w-full shadow-2xl border border-red-200 animate-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="bg-gradient-to-r from-red-500 to-red-600 p-6 rounded-t-[12px] relative overflow-hidden">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLW9wYWNpdHk9IjAuMSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-20"></div>
            
            <div className="relative flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-white/20 backdrop-blur p-3 rounded-full animate-pulse">
                  <BellRing size={28} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-black text-white tracking-tight">
                    🚨 ALARM!
                  </h3>
                  <p className="text-sm text-white/90 font-semibold mt-0.5">
                    Ulaşım Bildirimi
                  </p>
                </div>
              </div>
              
              <button
                onClick={stopAlarm}
                className="bg-white/20 hover:bg-white/30 backdrop-blur p-2 rounded-full transition-all"
              >
                <X size={20} className="text-white" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            {/* Alarm Name */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-xs font-black text-red-900 uppercase tracking-widest mb-1">
                {alarmData.alarm_name || 'Ulaşım Alarmı'}
              </p>
              <p className="text-2xl font-black text-red-600 leading-tight">
                {alarmData.message}
              </p>
            </div>

            {/* Route Info */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">
                  HAT NUMARASI
                </p>
                <p className="text-lg font-black text-gray-900">
                  {alarmData.hat_kodu}
                </p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">
                  HEDEF SAAT
                </p>
                <p className="text-lg font-black text-gray-900">
                  {alarmData.target_arrival}
                </p>
              </div>
            </div>

            {/* Location Info */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500 font-semibold">Nereden:</span>
                <span className="text-gray-900 font-bold">{alarmData.origin}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500 font-semibold">Nereye:</span>
                <span className="text-gray-900 font-bold">{alarmData.destination}</span>
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={stopAlarm}
              className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white py-3.5 rounded-lg font-black text-sm uppercase tracking-wider transition-all transform active:scale-95 shadow-lg hover:shadow-xl"
            >
              ALARMI KAPAT
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default AlarmSound;

