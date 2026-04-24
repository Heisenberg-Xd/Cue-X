import { Link } from 'react-router-dom';
import { GLSLHills } from '../components/ui/glsl-hills';

const Home = () => {
  return (
    <div className="relative flex h-screen w-full flex-col items-center justify-center overflow-hidden bg-black text-white selection:bg-white/20 font-['Inter']">
      <GLSLHills />
      <div className="space-y-6 z-10 text-center absolute flex flex-col items-center justify-center pointer-events-none">
        
        <div className="space-y-4 flex flex-col items-center">
          <span className="text-[#FF9900] font-mono text-xs md:text-sm uppercase tracking-[0.3em] font-semibold bg-[#FF9900]/10 px-4 py-1.5 rounded-full border border-[#FF9900]/20">Customer Intelligence</span>
          <h1 className="font-semibold text-5xl md:text-7xl whitespace-pre-wrap leading-tight">
            <span className="font-thin block mb-2">Know Your Customers.</span>
            <span className="block font-bold">
              Own Your Market.
            </span>
          </h1>
        </div>
        
        <p className="text-sm md:text-base text-white/60 max-w-lg font-light leading-relaxed px-4 pt-4">
          Transform raw purchase data into actionable segments. Upload your dataset and let AI reveal the hidden patterns in customer behavior.
        </p>

        <div className="pt-8 pointer-events-auto">
          <Link
            to="/upload"
            className="group relative inline-flex items-center justify-center gap-2 px-8 py-3.5 text-sm font-medium text-white transition-all duration-300 ease-out hover:scale-105"
          >
            <span className="absolute inset-0 w-full h-full border border-white/20 rounded-full bg-white/5 backdrop-blur-md transition-all group-hover:bg-white/10 group-hover:border-white/40"></span>
            <span className="relative">Enter Intelligence Pipeline</span>
            <svg className="relative w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
