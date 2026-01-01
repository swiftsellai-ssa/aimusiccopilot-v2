// frontend/components/AuthForm.tsx
'use client';
import { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

interface AuthFormProps {
  onLoginSuccess: (token: string) => void;
}

export default function AuthForm({ onLoginSuccess }: AuthFormProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }
    
    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);

    try {
      if (isLogin) {
        // LOGIN
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await axios.post('http://localhost:8000/token', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        const token = response.data.access_token;
        localStorage.setItem('token', token);
        localStorage.setItem('user_email', email); // Store email for display
        
        toast.success('Welcome back to AI Music Copilot!');
        onLoginSuccess(token);

      } else {
        // REGISTER
        await axios.post('http://localhost:8000/register', {
          email,
          password
        });
        
        toast.success('Account created! Please log in.');
        setIsLogin(true);
        // Clear password for security
        setPassword('');
      }
    } catch (error: any) {
      console.error('Auth error:', error);
      
      if (error.response?.status === 400) {
        toast.error('Invalid email or password');
      } else if (error.response?.status === 409) {
        toast.error('Email already registered');
      } else {
        toast.error(error.response?.data?.detail || 'Authentication failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md bg-gradient-to-b from-neutral-900 to-black p-8 rounded-2xl border border-neutral-800 shadow-2xl">
      <h2 className="text-3xl font-bold mb-2 text-center bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
        {isLogin ? 'Welcome Back' : 'Create Account'}
      </h2>
      <p className="text-xs text-neutral-500 text-center mb-6">
        {isLogin ? 'Log in to access your music projects' : 'Join the AI music revolution'}
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm text-neutral-400 mb-2">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 bg-black/50 border border-neutral-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            placeholder="producer@studio.com"
            autoComplete="email"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm text-neutral-400 mb-2">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 bg-black/50 border border-neutral-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            placeholder="••••••••"
            autoComplete={isLogin ? "current-password" : "new-password"}
            minLength={6}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`
            w-full py-3 mt-4 rounded-xl font-bold transition-all duration-200
            ${loading 
              ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed' 
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white shadow-lg hover:shadow-xl'
            }
          `}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-neutral-500 border-t-white rounded-full animate-spin" />
              Processing...
            </span>
          ) : (
            isLogin ? 'Log In' : 'Sign Up'
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="text-sm text-neutral-500 hover:text-white transition-colors"
        >
          {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Log In"}
        </button>
      </div>
    </div>
  );
}