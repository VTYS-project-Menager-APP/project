import React, { useState, useEffect } from 'react';
import api from '../api';
import { Bell, X, Bus, Clock } from 'lucide-react';

const AlarmNotification = () => {
  const [notifications, setNotifications] = useState([]);
  const [permission, setPermission] = useState(Notification.permission);

  useEffect(() => {
    // Tarayıcı bildirim izni iste
    if (permission === 'default') {
      Notification.requestPermission().then(result => {
        setPermission(result);
      });
    }

    // Her 30 saniyede bir bildirimleri kontrol et (10sn yerine)
    const interval = setInterval(checkNotifications, 30000);
    checkNotifications(); // İlk çalıştırma

    return () => clearInterval(interval);
  }, []);

  const checkNotifications = async () => {
    try {
      const response = await api.get('/notifications');
      const newNotifications = response.data.notifications || [];

      if (newNotifications.length > 0) {
        setNotifications(prev => [...newNotifications, ...prev].slice(0, 5));

        // Tarayıcı bildirimi gönder
        newNotifications.forEach(notif => {
          if (permission === 'granted' && notif.type === 'transport_alarm') {
            showBrowserNotification(notif);
          }
        });

        // Ses çal (isteğe bağlı)
        playNotificationSound();
      }
    } catch (error) {
      console.error('Notification check error:', error);
    }
  };

  const showBrowserNotification = (notif) => {
    const notification = new Notification(notif.title, {
      body: `${notif.message}\n${notif.action_message}`,
      icon: '/bus-icon.png',
      tag: 'transport-alarm',
      requireInteraction: true
    });

    notification.onclick = () => {
      window.focus();
      notification.close();
    };
  };

  const playNotificationSound = () => {
    // Basit bir bip sesi (isteğe bağlı)
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRg0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PUp/q7KhVEwtJouLyt2sjBTGN1fLOeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZ');
      audio.play();
    } catch (error) {
      console.log('Audio play failed:', error);
    }
  };

  const dismissNotification = (index) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  };

  if (notifications.length === 0) return null;

  return (
    <div className="notification-container">
      {notifications.map((notif, index) => (
        <div key={index} className="notification-card">
          <div className="notification-icon">
            <Bus size={24} />
          </div>
          <div className="notification-content">
            <div className="notification-title">{notif.title}</div>
            <div className="notification-message">{notif.message}</div>
            {notif.action_message && (
              <div className="notification-action">{notif.action_message}</div>
            )}
            {notif.timing && (
              <div className="notification-time">
                <Clock size={14} />
                {notif.timing.minutes_until_departure} dakika içinde kalkıyor
              </div>
            )}
          </div>
          <button
            className="dismiss-btn"
            onClick={() => dismissNotification(index)}
          >
            <X size={18} />
          </button>
        </div>
      ))}

      <style jsx>{`
        .notification-container {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 10000;
          display: flex;
          flex-direction: column;
          gap: 12px;
          max-width: 400px;
        }

        .notification-card {
          display: flex;
          gap: 12px;
          background: white;
          padding: 16px;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.15);
          animation: slideIn 0.3s ease-out;
          border-left: 4px solid #3b82f6;
        }

        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        .notification-icon {
          flex-shrink: 0;
          width: 48px;
          height: 48px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .notification-content {
          flex: 1;
          min-width: 0;
        }

        .notification-title {
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 4px;
        }

        .notification-message {
          color: #374151;
          font-size: 14px;
          margin-bottom: 8px;
        }

        .notification-action {
          background: #fef3c7;
          color: #92400e;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 500;
          margin-bottom: 8px;
        }

        .notification-time {
          display: flex;
          align-items: center;
          gap: 4px;
          color: #6b7280;
          font-size: 12px;
        }

        .dismiss-btn {
          flex-shrink: 0;
          width: 32px;
          height: 32px;
          background: transparent;
          border: none;
          color: #9ca3af;
          cursor: pointer;
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .dismiss-btn:hover {
          background: #f3f4f6;
          color: #374151;
        }
      `}</style>
    </div>
  );
};

export default AlarmNotification;
