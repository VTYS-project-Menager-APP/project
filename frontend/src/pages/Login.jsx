import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const [isLogin, setIsLogin] = useState(true);
    const [name, setName] = useState('');

    const handleAuth = async (e) => {
        e.preventDefault();
        try {
            if (isLogin) {
                // Login Flow
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);

                const response = await api.post('/auth/token', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });

                localStorage.setItem('token', response.data.access_token);
                navigate('/');
                window.location.reload();
            } else {
                // Register Flow
                const res = await api.post('/auth/register', {
                    email,
                    password,
                    name
                });

                localStorage.setItem('token', res.data.access_token);
                navigate('/');
                window.location.reload();
            }

        } catch (error) {
            console.error(error);
            alert(isLogin ? 'Giriş Başarısız' : 'Kayıt Başarısız: ' + (error.response?.data?.detail || 'Bilinmeyen Hata'));
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-600 to-indigo-800">
            <div className="bg-white/10 backdrop-blur-lg p-10 rounded-3xl shadow-2xl w-full max-w-md border border-white/20">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-extrabold text-white mb-2 tracking-tight">Menager</h1>
                    <p className="text-blue-100 opacity-80">Hayatını Yönet, Geleceğine Yön Ver</p>
                </div>

                <h2 className="text-2xl font-bold mb-6 text-white text-center">
                    {isLogin ? 'Giriş Yap' : 'Hesap Oluştur'}
                </h2>

                <form onSubmit={handleAuth} className="space-y-5">
                    {!isLogin && (
                        <div>
                            <label className="block mb-1 text-sm font-medium text-blue-100">İsim Soyisim</label>
                            <input
                                className="w-full px-4 py-3 bg-white/20 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 text-white placeholder-blue-200 transition"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                type="text"
                                placeholder="Adınız"
                                required={!isLogin}
                            />
                        </div>
                    )}

                    <div>
                        <label className="block mb-1 text-sm font-medium text-blue-100">E-posta</label>
                        <input
                            className="w-full px-4 py-3 bg-white/20 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 text-white placeholder-blue-200 transition"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            type="email"
                            placeholder="ornek@email.com"
                            required
                        />
                    </div>
                    <div>
                        <label className="block mb-1 text-sm font-medium text-blue-100">Şifre</label>
                        <input
                            className="w-full px-4 py-3 bg-white/20 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 text-white placeholder-blue-200 transition"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            type="password"
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    <button className="w-full bg-blue-500 hover:bg-blue-400 text-white font-bold py-3.5 rounded-xl shadow-lg transition duration-300 transform hover:scale-[1.02] mt-4">
                        {isLogin ? 'Giriş Yap' : 'Kayıt Ol'}
                    </button>
                </form>

                <p className="text-center text-sm text-blue-100 mt-6 cursor-pointer hover:text-white transition" onClick={() => setIsLogin(!isLogin)}>
                    {isLogin ? "Hesabın yok mu? Kayıt Ol" : "Zaten hesabın var mı? Giriş Yap"}
                </p>
            </div>
        </div>
    );
}
