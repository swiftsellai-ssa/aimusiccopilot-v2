'use client';

import React, { useState, useEffect } from 'react';
import EnhancedGenerator from '@/components/EnhancedGenerator';

export default function Home() {
  // Authentication State
  const [token, setToken] = useState<string | null>(null);
  const [isLoginView, setIsLoginView] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Check for existing token on load
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  // Logout Function
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  // Login / Register Logic
  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const endpoint = isLoginView ? '/token' : '/register';
      // Ensure we point to the correct API URL (Localhost or Render)
      const url = `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`;

      let body;
      let headers = {};

      if (isLoginView) {
        // Login requires Form Data (OAuth2 standard)
        const formData = new URLSearchParams();
        formData.append('username', email); // FastAPI expects 'username' field
        formData.append('password', password);
        body = formData;
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
      } else {
        // Register requires JSON
        body = JSON.stringify({ email, password });
        headers = { 'Content-Type': 'application/json' };
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: body,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Authentication failed');
      }

      const data = await response.json();

      if (isLoginView) {
        // LOGIN SUCCESS
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
      } else {
        // REGISTER SUCCESS -> Switch to Login view
        alert("Account created successfully! You can now log in.");
        setIsLoginView(true);
      }

    } catch (error) {
      console.error(error);
      alert(error instanceof Error ? error.message : "Connection error");
    } finally {
      setIsLoading(false);
    }
  };

  // --- SCENARIO 1: USER IS LOGGED IN ---
  if (token) {
    return (
      <div className="relative">
        {/* Logout Button (Top Right) */}
        <button
          onClick={handleLogout}
          className="absolute top-4 right-4 z-50 px-4 py-2 bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white rounded-full text-sm font-medium transition-all"
        >
          Logout
        </button>

        {/* The New Engine */}
        <EnhancedGenerator />
      </div>
    );
  }

  // --- SCENARIO 2: LOGIN / REGISTER SCREEN ---
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl w-full max-w-md border border-gray-700">

        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            {isLoginView ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-gray-400 mt-2">amc - AI Music Co-pilot v2</p>
        </div>

        <form onSubmit={handleAuth} className="space-y-6">
          <div>
            <label className="block text-gray-400 text-sm font-bold mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:border-blue-500"
              placeholder="name@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-gray-400 text-sm font-bold mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:border-blue-500"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 rounded-lg font-bold text-white transition-all ${isLoading
              ? 'bg-gray-600 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-[1.02]'
              }`}
          >
            {isLoading ? 'Processing...' : (isLoginView ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLoginView(!isLoginView)}
            className="text-gray-400 hover:text-white text-sm underline"
          >
            {isLoginView
              ? "Don't have an account? Register"
              : "Already have an account? Login"}
          </button>
        </div>

      </div>
    </div>
  );
}