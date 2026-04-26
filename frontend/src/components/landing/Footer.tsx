import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';

const footerLinks = [
  {
    heading: 'Product',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'How It Works', href: '#how-it-works' },
      { label: 'Pricing', href: '#' },
    ],
  },
  {
    heading: 'Account',
    links: [
      { label: 'Sign Up', action: 'signup' },
      { label: 'Log In', action: 'login' },
    ],
  },
  {
    heading: 'Company',
    links: [
      { label: 'About', href: '#' },
      { label: 'Privacy', href: '#' },
      { label: 'Terms', href: '#' },
    ],
  },
];

export const Footer: React.FC = () => {
  const navigate = useNavigate();

  const handleLinkClick = (link: { href?: string; action?: string; label: string }) => {
    if (link.action === 'signup') {
      navigate('/auth?mode=signup');
    } else if (link.action === 'login') {
      navigate('/auth');
    } else if (link.href?.startsWith('#')) {
      document.querySelector(link.href)?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer className="bg-black border-t border-white/5 px-4 pt-20 pb-10">
      <div className="max-w-6xl mx-auto">
        {/* Top row */}
        <div className="grid md:grid-cols-4 gap-12 pb-16 border-b border-white/5">
          {/* Brand */}
          <div className="md:col-span-1">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              <h3 className="text-xl font-bold text-white mb-3">CUE X</h3>
              <p className="text-sm text-white/30 leading-relaxed max-w-xs">
                AI-powered customer intelligence for modern marketing teams.
              </p>
                <a
                href="https://github.com/Heisenberg-Xd/Cue-X"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-5 inline-flex items-center gap-2 text-xs text-white/30 hover:text-white/60 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                GitHub Repo
              </a>
            </motion.div>
          </div>

          {/* Link groups */}
          {footerLinks.map((group, gi) => (
            <div key={group.heading}>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: gi * 0.05 }}
              >
                <p className="text-xs font-semibold text-white/30 uppercase tracking-widest mb-5">
                  {group.heading}
                </p>
                <ul className="space-y-3">
                  {group.links.map(link => (
                    <li key={link.label}>
                      <button
                        onClick={() => handleLinkClick(link)}
                        className="text-sm text-white/50 hover:text-white transition-colors text-left"
                      >
                        {link.label}
                      </button>
                    </li>
                  ))}
                </ul>
              </motion.div>
            </div>
          ))}
        </div>

        {/* Bottom row */}
        <div className="pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-white/20">
            © {new Date().getFullYear()} CUE X. All rights reserved.
          </p>
          <p className="text-xs text-white/20">
            Built with ♥ for data-driven teams.
          </p>
        </div>
      </div>
    </footer>
  );
};
