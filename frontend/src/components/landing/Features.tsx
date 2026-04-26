import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { Brain, Target, TrendingUp, Zap } from 'lucide-react';

const FeaturePoint: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
  delay?: number;
}> = ({ icon, title, description, delay = 0 }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay }}
      className="flex flex-col gap-4"
    >
      <div className="w-10 h-10 rounded-xl bg-black/10 flex items-center justify-center">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-black">{title}</h3>
      <p className="text-black/60 leading-relaxed text-[15px]">{description}</p>
    </motion.div>
  );
};

const DashboardMockup: React.FC = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={isInView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.8, delay: 0.2 }}
      className="relative w-full max-w-sm mx-auto"
    >
      {/* Phone shell */}
      <div className="relative z-10 bg-black rounded-[2.5rem] p-3 shadow-2xl border border-white/10">
        <div className="rounded-[2rem] overflow-hidden bg-[#0A0A0A]">
          {/* Status bar */}
          <div className="flex justify-between items-center px-5 py-3">
            <span className="text-white/40 text-xs font-medium">9:41</span>
            <div className="w-20 h-4 bg-black rounded-full" />
            <div className="flex gap-1">
              {[1,2,3].map(i => (
                <div key={i} className={`h-2 rounded-sm bg-white/40`} style={{ width: `${i * 3 + 2}px` }} />
              ))}
            </div>
          </div>

          {/* Dashboard content */}
          <div className="px-4 pb-6">
            <div className="mb-4">
              <p className="text-white/40 text-[10px] mb-1">Total Customers</p>
              <p className="text-white text-2xl font-bold">12,483</p>
              <p className="text-green-400 text-[10px] mt-0.5">↑ 14.2% this month</p>
            </div>

            {/* Segments */}
            <div className="space-y-2 mb-4">
              {[
                { label: 'Champions', pct: 28, color: '#FFFFFF' },
                { label: 'Loyal', pct: 45, color: '#A3A3A3' },
                { label: 'At Risk', pct: 18, color: '#3B82F6' },
                { label: 'Lost', pct: 9, color: '#525252' },
              ].map(seg => (
                <div key={seg.label}>
                  <div className="flex justify-between text-[10px] mb-1">
                    <span className="text-white/60">{seg.label}</span>
                    <span className="text-white/40">{seg.pct}%</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${seg.pct}%` }}
                      transition={{ duration: 1, delay: 0.8 }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: seg.color }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Pie placeholder */}
            <div className="flex items-center gap-3 p-3 rounded-xl border border-white/5 bg-white/3">
              <div className="relative w-12 h-12 flex-shrink-0">
                <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                  <circle cx="18" cy="18" r="15" fill="none" stroke="#ffffff10" strokeWidth="3" />
                  <circle cx="18" cy="18" r="15" fill="none" stroke="#3B82F6" strokeWidth="3"
                    strokeDasharray="45 100" strokeLinecap="round" />
                  <circle cx="18" cy="18" r="15" fill="none" stroke="#fff" strokeWidth="3"
                    strokeDasharray="30 100" strokeDashoffset="-45" strokeLinecap="round" />
                </svg>
              </div>
              <div>
                <p className="text-white/80 text-[10px] font-semibold">RFM Analysis</p>
                <p className="text-white/40 text-[10px]">Segment Score: 4.2 / 5</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Glow underneath phone */}
      <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 w-48 h-24 bg-black/30 blur-2xl rounded-full" />
    </motion.div>
  );
};

export const Features: React.FC = () => {
  const headingRef = useRef(null);
  const isHeadingInView = useInView(headingRef, { once: true, margin: '-80px' });

  const leftFeatures = [
    {
      icon: <Brain className="w-5 h-5 text-black/70" />,
      title: 'Data That Makes Sense',
      description: 'Transform complex datasets into simple, actionable insights your team can actually use.',
    },
    {
      icon: <Target className="w-5 h-5 text-black/70" />,
      title: 'Clarity Driven',
      description: 'Automatically group customers into meaningful segments like Champions, At Risk, and Loyal Customers—no manual work needed.',
    },
  ];

  const rightFeatures = [
    {
      icon: <TrendingUp className="w-5 h-5 text-black/70" />,
      title: 'Built for Real Business Growth',
      description: 'Designed to help marketing and product teams increase retention, improve targeting, and boost ROI.',
    },
    {
      icon: <Zap className="w-5 h-5 text-black/70" />,
      title: 'Precision Insights',
      description: 'Every segment is backed by data—so your decisions are not guesses, but strategies.',
    },
  ];

  return (
    <section id="features" className="bg-[#F7F7F7] py-32 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          ref={headingRef}
          initial={{ opacity: 0, y: 30 }}
          animate={isHeadingInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <p className="text-xs font-semibold text-black/30 uppercase tracking-widest mb-4">Features</p>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-black leading-tight">
            Understand your customers
            <br />like never before.
          </h2>
        </motion.div>

        {/* 3-column layout: features | phone mockup | features */}
        <div className="grid lg:grid-cols-3 gap-12 items-center">
          {/* Left features */}
          <div className="space-y-12">
            {leftFeatures.map((f, i) => (
              <FeaturePoint key={f.title} {...f} delay={i * 0.1} />
            ))}
          </div>

          {/* Center mockup */}
          <DashboardMockup />

          {/* Right features */}
          <div className="space-y-12">
            {rightFeatures.map((f, i) => (
              <FeaturePoint key={f.title} {...f} delay={i * 0.1 + 0.2} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
