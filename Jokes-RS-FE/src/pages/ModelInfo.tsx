import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { getModels } from '../services/api';

const ModelInfo: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId, currentModel, setCurrentModel, setModels } = useAppStore();

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await getModels();
        setModels(response.models);
      } catch {
        console.warn('Failed to fetch models');
      }
    };
    fetchModels();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSwitchModel = (modelId: string) => {
    setCurrentModel(modelId);
    navigate('/dashboard');
  };

  const navigateToDashboard = () => navigate('/dashboard');
  const navigateToHistory = () => navigate('/history');

  return (
    <div className="bg-background text-on-surface font-body-md min-h-screen flex flex-col">
      <header className="bg-surface sticky top-0 z-50 docked full-width top-0">
        <div className="flex justify-between items-center w-full px-md py-sm max-w-container-max mx-auto">
          <div className="flex items-center gap-sm">
            <span className="font-display-lg text-headline-md font-black text-primary cursor-pointer" onClick={() => navigate('/')}>JokeRec</span>
          </div>
          <nav className="hidden md:flex items-center gap-md">
            <span onClick={navigateToDashboard} className="text-on-surface-variant font-body-md hover:text-primary transition-colors duration-200 cursor-pointer">Home</span>
            <span className="text-primary font-bold border-b-2 border-primary hover:text-primary transition-colors duration-200 cursor-pointer">Models</span>
            <span onClick={navigateToHistory} className="text-on-surface-variant font-body-md hover:text-primary transition-colors duration-200 cursor-pointer">Stats</span>
          </nav>
          <div className="flex items-center gap-sm">
            <span className="font-label-caps text-on-surface-variant opacity-80">Session: #{sessionId?.slice(-4) || '8821'}</span>
            <div className="h-4 w-[1px] bg-outline-variant"></div>
            <span className="font-label-caps text-primary font-bold">Model: {currentModel.toUpperCase()}</span>
          </div>
        </div>
        <div className="w-full h-1 bg-surface-container-low">
          <div className="h-full bg-primary-container w-1/3"></div>
        </div>
      </header>

      <div className="flex flex-1 max-w-container-max w-full mx-auto relative">
        <aside className="fixed left-0 top-0 h-full z-40 flex-col p-md bg-surface-container-low w-64 hidden lg:flex mt-[72px]">
          <div className="mb-lg">
            <h2 className="font-headline-md text-headline-md text-primary">Your Feed</h2>
            <p className="font-body-md text-on-surface-variant opacity-70">Personalized Jokes</p>
          </div>
          <nav className="flex flex-col gap-xs mb-xl">
            <span onClick={navigateToDashboard} className="flex items-center gap-sm px-md py-sm text-on-surface-variant hover:bg-surface-variant rounded-xl transition-all duration-200 cursor-pointer">
              <span className="material-symbols-outlined">auto_awesome</span>
              <span className="font-body-md">Top Recommendations</span>
            </span>
            <span onClick={navigateToHistory} className="flex items-center gap-sm px-md py-sm text-on-surface-variant hover:bg-surface-variant rounded-xl transition-all duration-200 cursor-pointer">
              <span className="material-symbols-outlined">history</span>
              <span className="font-body-md">Recent Ratings</span>
            </span>
          </nav>
          <button onClick={navigateToDashboard} className="bg-primary-container text-on-primary-fixed font-bold py-sm px-md rounded-full flex items-center justify-center gap-xs scale-95 active:transition-transform transition-transform hover:scale-100">
            <span className="material-symbols-outlined">casino</span>
            Surprise Me
          </button>
        </aside>

        <main className="flex-1 lg:ml-64 px-md py-lg">
          <div className="max-w-3xl mx-auto space-y-lg">
            <section className="space-y-sm">
              <div className="inline-flex items-center gap-xs px-sm py-1 bg-secondary-container text-on-secondary-container rounded-full font-label-caps">
                <span className="material-symbols-outlined text-[14px]">info</span>
                Engine Architecture
              </div>
              <h1 className="font-display-lg text-display-lg text-on-surface">Recommendation Models</h1>
              <p className="font-body-lg text-on-surface-variant max-w-2xl">
                Our recommendation engine uses state-of-the-art machine learning to decode your sense of humor. Switch between architectures to explore different facets of comedy.
              </p>
            </section>

            <section className="grid grid-cols-1 gap-md">
              <article className={`bg-surface-container-lowest rounded-[24px] p-md md:p-xl ambient-shadow transition-all duration-200 border ${currentModel === 'pmf' ? 'border-primary-fixed border-opacity-100' : 'border-transparent hover:border-primary-fixed border-opacity-50'}`}>
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-md">
                  <div className="flex-1 space-y-md">
                    <div className="flex items-center gap-sm">
                      <div className="w-12 h-12 rounded-2xl bg-primary-fixed flex items-center justify-center text-on-primary-fixed">
                        <span className="material-symbols-outlined text-[28px]">groups</span>
                      </div>
                      <div>
                        <h3 className="font-headline-md text-headline-md text-on-surface">Probabilistic Matrix Factorization (PMF)</h3>
                        {currentModel === 'pmf' && <span className="font-label-caps text-primary font-bold">Currently Active</span>}
                      </div>
                    </div>
                    <p className="font-body-lg text-on-surface-variant">
                      A collaborative filtering model that predicts your humor preferences based on patterns from thousands of users.
                    </p>
                    <div className="flex flex-wrap gap-xs">
                      <span className="px-sm py-1 bg-surface-container text-on-surface-variant rounded-full text-sm font-label-caps">Social Signals</span>
                      <span className="px-sm py-1 bg-surface-container text-on-surface-variant rounded-full text-sm font-label-caps">High Efficiency</span>
                      <span className="px-sm py-1 bg-surface-container text-on-surface-variant rounded-full text-sm font-label-caps">Trend Analysis</span>
                    </div>
                  </div>
                  {currentModel === 'pmf' ? (
                    <button className="bg-surface-container-low text-on-surface-variant font-bold px-md py-sm rounded-full border border-outline-variant opacity-50 cursor-not-allowed flex items-center gap-xs">
                      <span className="material-symbols-outlined">check_circle</span>
                      Active
                    </button>
                  ) : (
                    <button onClick={() => handleSwitchModel('pmf')} className="bg-primary-container text-on-primary-fixed font-bold px-md py-sm rounded-full flex items-center gap-xs hover:shadow-lg transition-all active:scale-95">
                      <span className="material-symbols-outlined">swap_horiz</span>
                      Switch to PMF
                    </button>
                  )}
                </div>
              </article>

              <article className={`bg-surface-container-lowest rounded-[24px] p-md md:p-xl ambient-shadow transition-all duration-200 border ${currentModel === 'autoencoder' ? 'border-secondary border-opacity-100' : 'border-transparent hover:border-secondary border-opacity-50'}`}>
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-md">
                  <div className="flex-1 space-y-md">
                    <div className="flex items-center gap-sm">
                      <div className="w-12 h-12 rounded-2xl bg-secondary-fixed flex items-center justify-center text-on-secondary-fixed">
                        <span className="material-symbols-outlined text-[28px]">psychology</span>
                      </div>
                      <div>
                        <h3 className="font-headline-md text-headline-md text-on-surface">Autoencoder</h3>
                        {currentModel === 'autoencoder' && <span className="font-label-caps text-secondary font-bold">Deep Learning</span>}
                      </div>
                    </div>
                    <p className="font-body-lg text-on-surface-variant">
                      A deep learning model that learns the underlying structure of jokes to find hidden gems you'll love.
                    </p>
                    <div className="flex flex-wrap gap-xs">
                      <span className="px-sm py-1 bg-surface-container text-on-surface-variant rounded-full text-sm font-label-caps">Neural Networks</span>
                      <span className="px-sm py-1 bg-surface-container text-on-surface-variant rounded-full text-sm font-label-caps">Content Analysis</span>
                      <span className="px-sm py-1 bg-surface-container text-on-surface-variant rounded-full text-sm font-label-caps">Latent Space</span>
                    </div>
                  </div>
                  {currentModel === 'autoencoder' ? (
                    <button className="bg-surface-container-low text-on-surface-variant font-bold px-md py-sm rounded-full border border-outline-variant opacity-50 cursor-not-allowed flex items-center gap-xs">
                      <span className="material-symbols-outlined">check_circle</span>
                      Active
                    </button>
                  ) : (
                    <button onClick={() => handleSwitchModel('autoencoder')} className="bg-primary-container text-on-primary-fixed font-bold px-md py-sm rounded-full flex items-center gap-xs hover:shadow-lg transition-all active:scale-95">
                      <span className="material-symbols-outlined">swap_horiz</span>
                      Switch Model
                    </button>
                  )}
                </div>
              </article>
            </section>

            <section className="grid grid-cols-1 md:grid-cols-2 gap-md pt-lg">
              <div className="bg-surface-container rounded-[24px] p-md overflow-hidden relative min-h-[200px] flex items-end">
                <img className="absolute inset-0 w-full h-full object-cover opacity-20 mix-blend-multiply" alt="A clean and futuristic data visualization" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB5j4jIe3XG_UV2J3SzPnNy2NT-YzPgVwKT4OOKMalHX0RPIPzG7hruGngIX5vWZz0z1a_8BAB1lVtlX2KNsldGqZm7rxEwYbSd8LS6QExSAe3ZHsH0Vcglbd2A183DhqMTDAt1Boa0ZMADuaUDnE21hF49yvffJcr2AOsoAnFWRzWiVtH9vFxYGiVoQmGuyNOBp-HwtTYW19xz_XBhumkK1weFQHpTXP1g-KxgD3mKB244xZ0y1WmbpCqshL8yt-N7TQbpO0Vf7soi" />
                <div className="relative z-10">
                  <p className="font-label-caps text-primary">Technical Insight</p>
                  <h4 className="font-headline-md text-on-surface">Latent Features</h4>
                  <p className="text-sm opacity-70">We map jokes into a 64-dimensional space of "silliness."</p>
                </div>
              </div>
              <div className="bg-surface-container-high rounded-[24px] p-md overflow-hidden relative min-h-[200px] flex items-end">
                <img className="absolute inset-0 w-full h-full object-cover opacity-20 mix-blend-multiply" alt="An abstract representation of a digital brain" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAq6XnX2Zp8fDN0o1B48wCSEOkQ2GuK7iL3vpEKlWM2Hl05ERjZXHON1mCm-V7JEROT3sVxx31rkUSe11W3Fammks0uIRyCQrR0ubKTo8GcMA4fN3qt7Ob2_szf1RToU7C4NZD5XQ5YrXRxKPFg0ajTsQNpdZFBnOlfnNY-HT7b8eWWHKpI__YxSjDTIGUmQ9xv4WEHgs-jMQWSrgz6Cbggtq2i2oelUb2xPKp5NoRkXB8KJwM24w_7Vml9XwTe66gCIAL0ZsiFOy_I" />
                <div className="relative z-10">
                  <p className="font-label-caps text-secondary">Advanced Logic</p>
                  <h4 className="font-headline-md text-on-surface">Content Decoding</h4>
                  <p className="text-sm opacity-70">Detecting sarcasm and irony through semantic weight.</p>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>

      <footer className="bg-surface-container w-full py-lg px-md flex flex-col items-center gap-sm mt-xl">
        <span className="font-headline-md text-primary">JokeRec</span>
        <div className="flex gap-md">
          <span className="font-label-caps text-on-surface-variant hover:text-primary transition-colors cursor-pointer">Privacy Policy</span>
          <span className="font-label-caps text-on-surface-variant hover:text-primary transition-colors cursor-pointer">Terms of Service</span>
          <span className="font-label-caps text-on-surface-variant hover:text-primary transition-colors cursor-pointer">API Docs</span>
        </div>
        <p className="font-label-caps text-on-surface-variant opacity-60 mt-sm">© 2024 JokeRec. Sophisticatedly Silly.</p>
      </footer>
    </div>
  );
};

export default ModelInfo;
