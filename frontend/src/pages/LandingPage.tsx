import React from 'react';
import { Hero } from '../components/landing/Hero';
import { Features } from '../components/landing/Features';
import { CTA } from '../components/landing/CTA';
import { Footer } from '../components/landing/Footer';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black antialiased">
      <Hero />
      <Features />
      <CTA />
      <Footer />
    </div>
  );
};

export default LandingPage;
