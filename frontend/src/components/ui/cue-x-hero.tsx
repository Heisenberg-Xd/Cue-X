import { motion } from 'framer-motion';
import { Sparkles, Brain, Cpu, Database } from 'lucide-react';

export const CueXHero = () => {
  return (
    <div className="relative min-h-[70vh] flex flex-col items-center justify-center overflow-hidden px-6 pt-20">
      {/* Background elements */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute top-1/2 right-1/4 w-80 h-80 bg-purple-600/10 blur-[120px] rounded-full animate-pulse delay-1000" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 text-center max-w-4xl space-y-8"
      >
        <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-blue-500/5 border border-blue-500/10 text-blue-400 text-sm font-medium backdrop-blur-sm">
          <Sparkles className="w-4 h-4" />
          <span>Intelligent Customer Segmentation</span>
        </div>

        <h1 className="text-6xl md:text-8xl font-black tracking-tight leading-tight">
          CUE-X <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-indigo-600">
            Analytics Engine
          </span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto font-light leading-relaxed">
          The Customer Understanding Engine (CUE-X) leverages advanced K-Means clustering 
          to decode complex purchase behaviors into actionable segments.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-8 pt-6">
          {[
            { icon: Brain, label: "Neural Pattern Detection" },
            { icon: Cpu, label: "K-Means Core" },
            { icon: Database, label: "Behavioral Mapping" }
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3 text-gray-400 group">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                <item.icon className="w-5 h-5 text-blue-400" />
              </div>
              <span className="font-medium">{item.label}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
