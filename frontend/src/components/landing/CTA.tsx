import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../../utils/api';
import { ArrowRight, BarChart2, Users, Zap, TrendingUp } from 'lucide-react';

const statsData = [
  { value: '10x', label: 'Faster segmentation' },
  { value: '94%', label: 'Accuracy on RFM scoring' },
  { value: '3min', label: 'Upload to insights' },
  { value: '∞', label: 'Datasets supported' },
];

const processSteps = [
  {
    number: '01',
    icon: <Users className="w-5 h-5" />,
    title: 'Upload Your Data',
    description: 'Drop in any CSV with customer transaction history. We handle the rest.',
  },
  {
    number: '02',
    icon: <BarChart2 className="w-5 h-5" />,
    title: 'AI Segments Your Customers',
    description: 'Our RFM engine automatically groups customers into meaningful behavioral clusters.',
  },
  {
    number: '03',
    icon: <Zap className="w-5 h-5" />,
    title: 'Get Strategy Recommendations',
    description: 'The AI Strategy Agent generates targeted campaign ideas for every segment.',
  },
  {
    number: '04',
    icon: <TrendingUp className="w-5 h-5" />,
    title: 'Execute & Grow',
    description: 'Export insights, act on them, and watch your retention and revenue climb.',
  },
];

export const CTA: React.FC = () => {
  const navigate = useNavigate();
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' });

  const handleGetStarted = () => {
    if (isAuthenticated()) {
      navigate('/upload');
    } else {
      navigate('/auth?mode=signup');
    }
  };

  return (
    <>
      {/* HOW IT WORKS */}
      <section className="bg-black py-32 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <p className="text-xs font-semibold text-white/30 uppercase tracking-widest mb-4">How it works</p>
            <h2 className="text-4xl md:text-5xl font-bold text-white leading-tight">
              From data to decisions
              <br />
              <span className="text-white/30">in minutes.</span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {processSteps.map((step, i) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-80px' }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="relative p-6 rounded-2xl border border-white/8 bg-white/3 hover:bg-white/5 hover:border-white/15 transition-all group"
              >
                <div className="flex items-start justify-between mb-5">
                  <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/60 group-hover:text-white transition-colors">
                    {step.icon}
                  </div>
                  <span className="text-4xl font-bold text-white/5 group-hover:text-white/10 transition-colors select-none">
                    {step.number}
                  </span>
                </div>
                <h3 className="text-base font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-white/40 leading-relaxed">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* STATS STRIP */}
      <section className="bg-[#0A0A0A] border-y border-white/5 py-16 px-4">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {statsData.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold text-white mb-2">{stat.value}</div>
              <div className="text-xs text-white/40 uppercase tracking-widest">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* MAIN CTA */}
      <section ref={sectionRef} className="bg-black py-32 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7 }}
          >
            {/* Glow ring */}
            <div className="relative inline-flex items-center justify-center mb-10">
              <div className="absolute w-48 h-48 rounded-full bg-blue-500/20 blur-3xl" />
              <div className="relative w-20 h-20 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                <BarChart2 className="w-9 h-9 text-white" />
              </div>
            </div>

            <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
              Ready to understand
              <br />your customers?
            </h2>
            <p className="text-lg text-white/40 mb-10 max-w-xl mx-auto leading-relaxed">
              Join forward-thinking teams using CUE X to build smarter marketing strategies backed by real data.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={handleGetStarted}
                className="group flex items-center gap-2 px-8 py-4 bg-white text-black text-sm font-semibold rounded-full hover:bg-white/90 transition-all hover:scale-105 shadow-2xl shadow-white/10"
              >
                Get Started for Free
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate('/auth')}
                className="px-8 py-4 border border-white/15 text-white/70 text-sm font-medium rounded-full hover:border-white/30 hover:text-white transition-all hover:scale-105"
              >
                Sign In
              </button>
            </div>

            <p className="mt-6 text-xs text-white/25">
              No credit card required · Free to start · Upload your first dataset today
            </p>
          </motion.div>
        </div>
      </section>
    </>
  );
};
