import { Link, useLocation } from 'react-router-dom';
import { ChevronLeft, Menu, X } from 'lucide-react';
import { useState } from 'react';

interface NavBarProps {
  sessionId?: string;
  showBack?: boolean;
  onBackClick?: () => void;
}

export const NavBar = ({ sessionId, showBack = true, onBackClick }: NavBarProps) => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = sessionId
    ? [
        { label: 'Overview', href: `/dashboard/${sessionId}`, icon: '📊' },
        { label: 'Analytics', href: `/dashboard/${sessionId}/analytics`, icon: '📈' },
        { label: 'Chat', href: `/dashboard/${sessionId}/chat`, icon: '💬' },
      ]
    : [];

  const isActive = (href: string) => location.pathname === href;

  return (
    <nav className="bg-[#0A0A0A] border-b border-[#1E293B] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left Section */}
          <div className="flex items-center gap-4">
            {showBack && (
              <button
                onClick={onBackClick}
                className="p-2 hover:bg-[#1E293B] rounded-lg transition-colors text-[#64748B] hover:text-[#06B6D4]"
                title="Go back"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            )}

            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#06B6D4] to-[#0891B2] flex items-center justify-center">
                <span className="text-white font-bold text-sm">CUE</span>
              </div>
              <span className="font-bold text-[#FFFFFF] hidden sm:inline">CUE-X</span>
            </Link>
          </div>

          {/* Center Navigation - Desktop */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
                  isActive(item.href)
                    ? 'bg-[#06B6D4]/20 text-[#06B6D4] border border-[#06B6D4]/50'
                    : 'text-[#64748B] hover:text-[#FFFFFF] hover:bg-[#1E293B]'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-sm text-[#64748B]">
              {sessionId && <span>Session: {sessionId.slice(0, 8)}...</span>}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 hover:bg-[#1E293B] rounded-lg transition-colors text-[#64748B]"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 space-y-2 border-t border-[#1E293B] pt-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  isActive(item.href)
                    ? 'bg-[#06B6D4]/20 text-[#06B6D4]'
                    : 'text-[#64748B] hover:text-[#FFFFFF] hover:bg-[#1E293B]'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
};
