import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../../utils/api';
import { ArrowRight, Sparkles } from 'lucide-react';

export const Hero: React.FC = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (isAuthenticated()) {
      navigate('/upload');
    } else {
      navigate('/auth?mode=signup');
    }
  };

  const handleLogin = () => {
    if (isAuthenticated()) {
      navigate('/upload');
    } else {
      navigate('/auth');
    }
  };

  return (
    <section className="relative min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden px-4">
      {/* Background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[900px] rounded-full border border-white/5" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full border border-white/5" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full border border-white/5" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full border border-white/5" />
        {/* Center glow */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-gradient-to-t from-blue-600/20 via-purple-600/10 to-transparent blur-3xl" />
        {/* Dot grid */}
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.15) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      {/* Nav pill */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="absolute top-6 left-1/2 -translate-x-1/2 z-20 flex items-center gap-6 px-6 py-3 rounded-full border border-white/10 bg-white/5 backdrop-blur-xl"
      >
        <span className="text-sm font-semibold text-white tracking-wide">CUE X</span>
        <div className="w-px h-4 bg-white/20" />
        <button
          onClick={handleLogin}
          className="text-sm text-white/60 hover:text-white transition-colors"
        >
          Login
        </button>
        <button
          onClick={handleGetStarted}
          className="text-sm text-white bg-white/10 hover:bg-white/20 border border-white/20 px-4 py-1.5 rounded-full transition-all"
        >
          Get Started
        </button>
      </motion.nav>

      {/* Main content */}
      <div className="relative z-10 text-center max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 text-xs text-white/60 mb-8"
        >
          <Sparkles className="w-3 h-3 text-blue-400" />
          AI-powered Customer Intelligence
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-5xl md:text-7xl lg:text-8xl font-bold text-white leading-[1.05] tracking-tight mb-6"
        >
          Turn raw customer data
          <br />
          into revenue-driving{' '}
          <em className="not-italic text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 font-bold italic" style={{ fontFamily: 'Georgia, serif' }}>
            decisions.
          </em>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          CUE X uses AI to automatically segment your customers, uncover hidden
          patterns, and recommend high-impact marketing strategies.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <button
            onClick={handleGetStarted}
            className="group flex items-center gap-2 px-8 py-4 bg-white text-black text-sm font-semibold rounded-full hover:bg-white/90 transition-all hover:scale-105 shadow-lg shadow-white/10"
          >
            Get Started
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={() => {
              document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="flex items-center gap-2 px-8 py-4 border border-white/15 text-white/70 text-sm font-medium rounded-full hover:border-white/30 hover:text-white transition-all hover:scale-105"
          >
            Learn More
          </button>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <span className="text-xs text-white/30 tracking-widest uppercase">Scroll</span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="w-px h-8 bg-gradient-to-b from-white/30 to-transparent"
        />
      </motion.div>
    </section>
  );
};
