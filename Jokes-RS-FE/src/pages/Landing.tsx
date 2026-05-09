import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { createSession } from '../services/api';
import { toast } from 'sonner';

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const setSession = useAppStore((state) => state.setSession);

  const handleStartSession = async () => {
    try {
      setLoading(true);
      const session = await createSession();
      setSession(session);
      navigate('/dashboard');
    } catch {
      // Mocking successful session if backend is not available for demo purposes
      console.warn("Backend not available, creating mock session");
      const mockSessionId = Math.floor(Math.random() * 10000).toString();
      setSession({ session_id: mockSessionId, user_id: 1, created_at: '', last_active_at: '', is_active: true });
      toast.success('Mock session created!');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background text-on-background font-body-md antialiased min-h-screen flex flex-col">
      <div className="fixed top-0 left-0 w-full h-1 bg-surface-container z-50">
        <div className="h-full bg-primary-container w-[35%]"></div>
      </div>
      
      <header className="bg-surface dark:bg-surface-dim docked full-width top-0 z-50 sticky">
        <div className="flex justify-between items-center w-full px-md py-sm max-w-container-max mx-auto">
          <div className="font-display-lg text-headline-md font-black text-primary dark:text-primary-fixed-dim">
            JokeRec
          </div>
          <div className="hidden md:flex gap-md items-center">
            <span className="text-on-surface-variant font-body-md hover:text-primary transition-colors duration-200 cursor-pointer">Explore</span>
            <span className="text-on-surface-variant font-body-md hover:text-primary transition-colors duration-200 cursor-pointer">About</span>
            <div className="flex items-center gap-xs px-sm py-xs bg-surface-container rounded-full">
              <span className="text-primary font-bold border-b-2 border-primary">Home</span>
            </div>
          </div>
          <div className="flex items-center gap-sm">
            <button className="bg-primary text-on-primary px-sm py-xs rounded-full font-label-caps text-xs scale-95 active:transition-transform transition-transform">
              Model: PMF
            </button>
          </div>
        </div>
      </header>
      
      <main className="max-w-container-max mx-auto px-md pt-xl flex-grow w-full">
        <section className="flex flex-col md:flex-row items-center gap-xl py-xl">
          <div className="flex-1 space-y-md">
            <h1 className="font-display-lg text-display-lg text-on-background tracking-tighter">
              Get Personalized Jokes Instantly
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-xl">
              Discover humor tailored to your taste with our AI-powered recommendation engine. Sophisticatedly silly, curated for your specific funny bone.
            </p>
            <div className="pt-sm flex gap-sm">
              <button 
                onClick={handleStartSession}
                disabled={loading}
                className="bg-primary-container text-on-primary-container px-lg py-sm rounded-full font-headline-md text-body-md flex items-center gap-xs hover:brightness-105 transition-all scale-95 active:transition-transform disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {loading ? 'Starting...' : 'Start Session'}
                <span className="material-symbols-outlined">bolt</span>
              </button>
              <button className="bg-surface-container-high text-on-surface px-lg py-sm rounded-full font-headline-md text-body-md hover:bg-surface-variant transition-all scale-95 active:transition-transform">
                How it works
              </button>
            </div>
          </div>
          
          <div className="flex-1 relative flex justify-center">
            <div className="relative w-full max-w-md aspect-square bg-surface-container-lowest rounded-[48px] overflow-hidden card-shadow flex items-center justify-center p-xl">
              <img className="w-full h-full object-contain" alt="A minimalist 3D rendering of a joyful yellow emoji" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAqkN7ZSfXEZcbOcDY7wT-YGxF1gNk5FUnFheM5Lk8Z7nVrl5SlZcZK3Z-0rWsCCGyjGTfIz9DhPotBYzIV3yct2lzNed4RnNogTsgMrBE54ZNRk2-U8dpPnmbY2iufzuGV8bf4J1M2FnTjAGFA8ecIJL_r7myc0QgYlDflbN3oXdHQ8wIQTHMCt2i8mwTmr1BkaovFCmuNdEQgUQC2RCCmYAheVwOfuCowhoMzMoSwPULaBimcFd1oHdL1HnebfZzYOQohLUeSXYWO" />
            </div>
            <div className="absolute -bottom-8 -left-8 p-md bg-white rounded-xl card-shadow max-w-[200px] border border-outline-variant">
              <p className="font-label-caps text-primary mb-xs">POPULAR NOW</p>
              <p className="font-body-md text-sm italic">"Why don't scientists trust atoms? Because they make up everything!"</p>
            </div>
          </div>
        </section>
        
        <section className="py-xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
            <div className="bg-white p-md rounded-[24px] card-shadow card-hover transition-all">
              <div className="w-12 h-12 bg-tertiary-container rounded-full flex items-center justify-center mb-sm text-on-tertiary-container">
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
              </div>
              <h3 className="font-headline-md text-body-lg mb-xs">Neural Wit</h3>
              <p className="font-body-md text-on-surface-variant">Our AI understands wordplay, satire, and situational comedy to find exactly what makes you laugh.</p>
            </div>
            <div className="bg-white p-md rounded-[24px] card-shadow card-hover transition-all border-2 border-primary-container">
              <div className="w-12 h-12 bg-primary-container rounded-full flex items-center justify-center mb-sm text-on-primary-container">
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>mood</span>
              </div>
              <h3 className="font-headline-md text-body-lg mb-xs">Mood Tracking</h3>
              <p className="font-body-md text-on-surface-variant">Adjust your feed based on your current vibe—from dry sarcasm to wholesome dad jokes.</p>
            </div>
            <div className="bg-white p-md rounded-[24px] card-shadow card-hover transition-all">
              <div className="w-12 h-12 bg-secondary-fixed-dim rounded-full flex items-center justify-center mb-sm text-on-secondary-fixed-variant">
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>bolt</span>
              </div>
              <h3 className="font-headline-md text-body-lg mb-xs">Zero Friction</h3>
              <p className="font-body-md text-on-surface-variant">No accounts required for quick sessions. Just jump in and start discovering.</p>
            </div>
          </div>
        </section>
        
        <section className="py-xl">
          <div className="bg-surface-container-lowest rounded-[32px] p-lg card-shadow flex flex-col md:flex-row gap-lg items-center">
            <div className="flex-1">
              <h2 className="font-headline-md text-display-lg text-primary mb-sm tracking-tight">Try a Sample Card</h2>
              <p className="font-body-lg text-on-surface-variant mb-md">Our interface is designed for focus. Tap to react and refine your recommendations.</p>
            </div>
            <div className="flex-1 w-full max-w-sm">
              <div className="bg-white p-md rounded-[24px] card-shadow border border-outline-variant">
                <div className="flex items-center gap-sm mb-md">
                  <div className="w-10 h-10 rounded-full bg-secondary-container"></div>
                  <div>
                    <p className="font-headline-md text-sm">Recommended for You</p>
                    <p className="font-body-md text-xs text-on-surface-variant">Category: Tech Humor</p>
                  </div>
                </div>
                <p className="font-body-lg mb-lg">What do you call a programmer from Finland? <br/><strong>Nerdic.</strong></p>
                <div className="flex items-center justify-between border-t border-outline-variant pt-md">
                  <div className="flex gap-xs">
                    <button className="p-xs rounded-full bg-surface-container hover:bg-green-100 transition-colors">
                      <span className="material-symbols-outlined text-green-700">sentiment_very_satisfied</span>
                    </button>
                    <button className="p-xs rounded-full bg-surface-container hover:bg-red-100 transition-colors">
                      <span className="material-symbols-outlined text-red-700">sentiment_very_dissatisfied</span>
                    </button>
                  </div>
                  <button className="text-on-surface-variant hover:text-primary transition-colors">
                    <span className="material-symbols-outlined">share</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <footer className="bg-surface-container dark:bg-surface-container-low w-full py-lg px-md flex flex-col items-center gap-sm mt-xl">
        <div className="font-headline-md text-primary font-black mb-sm">JokeRec</div>
        <div className="flex flex-wrap justify-center gap-md">
          <span className="text-on-surface-variant hover:text-primary transition-colors font-label-caps cursor-pointer">Privacy Policy</span>
          <span className="text-on-surface-variant hover:text-primary transition-colors font-label-caps cursor-pointer">Terms of Service</span>
          <span className="text-on-surface-variant hover:text-primary transition-colors font-label-caps cursor-pointer">API Docs</span>
        </div>
        <p className="text-on-surface-variant font-label-caps mt-md opacity-80">
          © 2024 JokeRec. Sophisticatedly Silly.
        </p>
      </footer>
    </div>
  );
};

export default Landing;
