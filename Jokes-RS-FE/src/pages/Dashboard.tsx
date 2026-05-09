import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { getRecommendations, submitRating } from '../services/api';
import { toast } from 'sonner';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId, userId, currentModel, recommendations, setRecommendations, addRatingToHistory } = useAppStore();
  
  const [loading, setLoading] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [sliderValue, setSliderValue] = useState(0);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      // Ensure we have a session ID, in real app would use this.
      // Mocking fetch if backend not available
      try {
        const response = await getRecommendations(userId || 1, currentModel, 10);
        setRecommendations(response.recommendations);
      } catch {
        console.warn('Backend failed, using mock data');
        setRecommendations([
          { joke_id: 1, rank: 1, predicted_rating: 0.94, joke_text: "Why did the AI go to the party? Because it heard there would be some great bytes!" },
          { joke_id: 2, rank: 2, predicted_rating: 0.88, joke_text: "What's the object-oriented way to become wealthy? Inheritance..." },
          { joke_id: 3, rank: 3, predicted_rating: 0.82, joke_text: "Why did the programmer quit his job? He didn't get arrays..." }
        ]);
      }
      setCurrentIndex(0);
    } catch {
      toast.error('Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentModel]);

  const currentRec = recommendations[currentIndex];

  const handleRatingSubmit = async () => {
    if (!currentRec) return;
    try {
      await submitRating({
        session_id: sessionId || 'mock',
        user_id: userId || 1,
        joke_id: currentRec.joke_id,
        rating: sliderValue
      });
      addRatingToHistory({
        user_id: userId || 1,
        joke_id: currentRec.joke_id,
        rating: sliderValue,
        joke: { joke_id: currentRec.joke_id, joke_text: currentRec.joke_text },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      toast.success('Rating submitted!');
      handleNext();
    } catch {
      toast.error('Failed to submit rating');
      // For demo purposes, we'll still go next on error so flow isn't stuck
      handleNext();
    }
  };

  const handleNext = () => {
    setSliderValue(0);
    if (currentIndex < recommendations.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      toast.info('Fetching more jokes...');
      fetchRecommendations();
    }
  };

  const navigateToModels = () => navigate('/models');
  const navigateToHistory = () => navigate('/history');

  return (
    <div className="bg-background text-on-surface font-body-md min-h-screen">
      <div className="fixed top-0 left-0 w-full h-1 bg-primary-container z-50 overflow-hidden">
        <div className="h-full bg-primary w-1/3 transition-all duration-500"></div>
      </div>

      <header className="bg-surface dark:bg-surface-dim docked full-width top-0 z-30">
        <div className="flex justify-between items-center w-full px-md py-sm max-w-container-max mx-auto">
          <div className="flex items-center gap-md">
            <span className="font-display-lg text-headline-md font-black text-primary dark:text-primary-fixed-dim cursor-pointer" onClick={() => navigate('/')}>JokeRec</span>
            <nav className="hidden md:flex items-center gap-sm ml-lg">
              <span className="text-primary font-bold border-b-2 border-primary hover:text-primary transition-colors duration-200 py-1 cursor-pointer">Recommendations</span>
              <span onClick={navigateToHistory} className="text-on-surface-variant font-body-md hover:text-primary transition-colors duration-200 py-1 cursor-pointer">History</span>
              <span onClick={navigateToModels} className="text-on-surface-variant font-body-md hover:text-primary transition-colors duration-200 py-1 cursor-pointer">Models</span>
            </nav>
          </div>
          <div className="flex items-center gap-sm">
            <div className="hidden sm:flex flex-col items-end mr-sm">
              <span className="text-label-caps text-on-surface-variant opacity-70">Session: #{sessionId?.slice(-4) || '8821'}</span>
              <div className="flex items-center gap-xs">
                <span className="material-symbols-outlined text-sm text-primary">psychology</span>
                <span className="text-label-caps font-bold text-primary">Model: {currentModel.toUpperCase()}</span>
              </div>
            </div>
            <button onClick={navigateToModels} className="bg-primary-container text-on-primary-container px-sm py-xs rounded-full font-bold flex items-center gap-xs transition-transform scale-95 active:scale-90 hover:brightness-105">
              <span className="material-symbols-outlined text-md">tune</span>
              <span className="text-label-caps">{currentModel.toUpperCase()}</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-container-max mx-auto flex flex-col md:flex-row gap-lg px-md py-lg relative">
        <aside className="w-full md:w-72 shrink-0 space-y-lg">
          <section className="bg-surface-container-low dark:bg-surface-container-highest rounded-3xl p-md shadow-sm">
            <div className="mb-md">
              <h2 className="font-headline-md text-headline-md text-primary">Your Feed</h2>
              <p className="text-on-surface-variant text-body-md">Personalized Jokes</p>
            </div>
            <div className="space-y-sm">
              <div className="text-on-secondary-container bg-secondary-container rounded-xl font-bold flex items-center gap-sm p-sm transition-all hover:bg-secondary-container/90 cursor-pointer">
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
                <span>Top Recommendations</span>
              </div>
              <div onClick={navigateToHistory} className="text-on-surface-variant hover:bg-surface-variant rounded-xl flex items-center gap-sm p-sm transition-all cursor-pointer">
                <span className="material-symbols-outlined">history</span>
                <span>Recent Ratings</span>
              </div>
            </div>
            <button onClick={fetchRecommendations} className="w-full mt-lg bg-primary-container text-on-primary-container py-md rounded-full font-bold flex justify-center items-center gap-sm shadow-sm hover:brightness-95 transition-all">
              <span className="material-symbols-outlined">casino</span>
              Surprise Me
            </button>
          </section>

          <section className="space-y-md hidden md:block">
            <h3 className="text-label-caps text-on-surface-variant font-bold px-sm">RANKED PREVIEWS</h3>
            <div className="space-y-sm">
              {recommendations.slice(0, 3).map((rec, idx) => (
                <div key={idx} className="bg-white rounded-xl p-sm border border-outline-variant/30 hover:border-primary transition-colors cursor-pointer group">
                  <div className="flex justify-between items-start mb-xs">
                    <span className="text-label-caps text-primary">#{idx + 1} Rec</span>
                    <span className="material-symbols-outlined text-sm text-on-surface-variant">trending_up</span>
                  </div>
                  <p className="text-body-md line-clamp-2">{rec.joke_text}</p>
                </div>
              ))}
            </div>
          </section>
        </aside>

        <main className="flex-1 min-w-0">
          <div className="relative group">
            <div className="absolute -top-4 -left-4 w-12 h-12 bg-primary-container rounded-full blur-xl opacity-40"></div>
            <div className="absolute -bottom-8 -right-4 w-24 h-24 bg-secondary-container rounded-full blur-2xl opacity-20"></div>

            <div className="bg-white rounded-[24px] p-lg md:p-[40px] shadow-[0px_4px_20px_rgba(0,0,0,0.04)] relative z-10 border border-outline-variant/10 transition-transform duration-300 hover:-translate-y-1">
              <div className="flex justify-between items-center mb-lg">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>format_quote</span>
                  <span className="text-label-caps text-on-surface-variant">Recommended for you</span>
                </div>
                <div className="bg-surface-container-low px-sm py-xs rounded-full flex items-center gap-xs cursor-pointer hover:bg-surface-variant">
                  <span className="material-symbols-outlined text-md text-on-surface-variant">share</span>
                  <span className="text-label-caps">Share</span>
                </div>
              </div>

              <div className="min-h-[160px] flex items-center justify-center text-center">
                <h1 className="font-headline-md text-headline-md md:text-display-lg leading-tight text-on-surface">
                  {currentRec?.joke_text || "Generating fresh humor..."}
                </h1>
              </div>

              {currentRec && (
                <div className="mt-xl pt-lg border-t border-outline-variant/20">
                  <div className="flex flex-col items-center gap-lg">
                    <div className="w-full max-w-md">
                      <div className="flex justify-between items-center mb-sm">
                        <span className="text-2xl grayscale hover:grayscale-0 transition-all cursor-default" title="Not funny">😠</span>
                        <span className="text-label-caps text-on-surface-variant">
                          Rating: <span className="text-primary font-bold">{sliderValue}</span>
                        </span>
                        <span className="text-2xl grayscale hover:grayscale-0 transition-all cursor-default" title="Hilarious">😂</span>
                      </div>
                      <input 
                        className="w-full cursor-pointer accent-primary" 
                        max="10" 
                        min="-10" 
                        type="range" 
                        value={sliderValue}
                        onChange={(e) => setSliderValue(Number(e.target.value))}
                      />
                      <div className="flex justify-between mt-xs px-1">
                        <span className="text-[10px] text-on-surface-variant">-10</span>
                        <span className="text-[10px] text-on-surface-variant">0</span>
                        <span className="text-[10px] text-on-surface-variant">+10</span>
                      </div>
                    </div>

                    <div className="flex flex-wrap justify-center gap-md w-full">
                      <button 
                        onClick={handleRatingSubmit}
                        className="flex-1 min-w-[140px] bg-primary text-on-primary py-md rounded-full font-bold shadow-md hover:brightness-110 active:scale-95 transition-all flex items-center justify-center gap-sm"
                      >
                        <span className="material-symbols-outlined text-md">check_circle</span>
                        Submit Rating
                      </button>
                      <button 
                        onClick={handleNext}
                        className="flex-1 min-w-[140px] bg-surface-container-high text-on-surface-variant py-md rounded-full font-bold hover:bg-outline-variant/20 active:scale-95 transition-all flex items-center justify-center gap-sm"
                      >
                        <span className="material-symbols-outlined text-md">skip_next</span>
                        Next Joke
                      </button>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-lg flex justify-center gap-sm flex-wrap">
                <button className="bg-surface-container-low hover:bg-green-100 hover:text-green-800 transition-colors py-2 px-4 rounded-full flex items-center gap-xs text-on-surface-variant border border-transparent hover:border-green-200">
                  <span className="material-symbols-outlined text-md">sentiment_very_satisfied</span>
                  <span className="text-label-caps">Classic</span>
                </button>
                <button className="bg-surface-container-low hover:bg-yellow-100 hover:text-yellow-800 transition-colors py-2 px-4 rounded-full flex items-center gap-xs text-on-surface-variant border border-transparent hover:border-yellow-200">
                  <span className="material-symbols-outlined text-md">psychology</span>
                  <span className="text-label-caps">Smart</span>
                </button>
                <button className="bg-surface-container-low hover:bg-red-100 hover:text-red-800 transition-colors py-2 px-4 rounded-full flex items-center gap-xs text-on-surface-variant border border-transparent hover:border-red-200">
                  <span className="material-symbols-outlined text-md">mood_bad</span>
                  <span className="text-label-caps">Dad Joke</span>
                </button>
              </div>
            </div>

            {loading && (
              <div className="absolute inset-0 bg-surface/60 backdrop-blur-[2px] z-20 rounded-[24px] flex items-center justify-center">
                <div className="flex flex-col items-center gap-sm">
                  <div className="w-12 h-12 border-4 border-primary-container border-t-primary rounded-full animate-spin"></div>
                  <span className="text-label-caps font-bold text-primary">Fetching Fresh Bytes...</span>
                </div>
              </div>
            )}
          </div>

          <div className="mt-lg grid grid-cols-1 md:grid-cols-3 gap-md">
            <div className="bg-white p-md rounded-2xl border border-outline-variant/10 shadow-sm flex flex-col items-center text-center">
              <span className="material-symbols-outlined text-secondary text-2xl mb-xs">verified</span>
              <span className="text-label-caps text-on-surface-variant font-bold mb-1">RELEVANCE SCORE</span>
              <span className="text-headline-md text-secondary">
                {currentRec ? `${(currentRec.predicted_rating * 100).toFixed(0)}%` : '--'}
              </span>
            </div>
            <div className="bg-white p-md rounded-2xl border border-outline-variant/10 shadow-sm flex flex-col items-center text-center">
              <span className="material-symbols-outlined text-tertiary text-2xl mb-xs">schedule</span>
              <span className="text-label-caps text-on-surface-variant font-bold mb-1">AVG. READING TIME</span>
              <span className="text-headline-md text-tertiary">5s</span>
            </div>
            <div className="bg-white p-md rounded-2xl border border-outline-variant/10 shadow-sm flex flex-col items-center text-center">
              <span className="material-symbols-outlined text-primary text-2xl mb-xs">group</span>
              <span className="text-label-caps text-on-surface-variant font-bold mb-1">COMMUNITY SCORE</span>
              <span className="text-headline-md text-primary">8.2</span>
            </div>
          </div>

          <div className="mt-lg grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="bg-tertiary-container rounded-[24px] p-md flex flex-col justify-between overflow-hidden relative group min-h-[180px]">
              <div className="relative z-10">
                <h3 className="font-headline-md text-on-tertiary-container">Weekly Top Humor</h3>
                <p className="text-body-md text-on-tertiary-container/80 mt-xs">Discover the algorithms favorite puns of the week.</p>
              </div>
              <div className="absolute -bottom-8 -right-8 opacity-10 group-hover:opacity-20 transition-opacity">
                <span className="material-symbols-outlined text-[160px]">emoji_events</span>
              </div>
              <button className="relative z-10 self-start mt-lg bg-on-tertiary-container text-white px-md py-xs rounded-full text-label-caps font-bold">View List</button>
            </div>
            <div className="bg-secondary-container rounded-[24px] p-md flex flex-col justify-between overflow-hidden relative group min-h-[180px]">
              <div className="relative z-10">
                <h3 className="font-headline-md text-on-secondary-container">Model Tuning</h3>
                <p className="text-body-md text-on-secondary-container/80 mt-xs">Switch to Autoencoder for more abstract humor styles.</p>
              </div>
              <div className="absolute -bottom-8 -right-8 opacity-10 group-hover:opacity-20 transition-opacity">
                <span className="material-symbols-outlined text-[160px]">settings_input_component</span>
              </div>
              <button onClick={navigateToModels} className="relative z-10 self-start mt-lg bg-on-secondary-container text-secondary-container px-md py-xs rounded-full text-label-caps font-bold">Switch Now</button>
            </div>
          </div>
        </main>
      </div>

      <nav className="md:hidden fixed bottom-0 left-0 w-full bg-white border-t border-outline-variant/20 flex justify-around items-center py-sm z-40 px-md">
        <button className="flex flex-col items-center gap-1 text-primary">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>home</span>
          <span className="text-[10px] font-bold">Home</span>
        </button>
        <button onClick={navigateToModels} className="flex flex-col items-center gap-1 text-on-surface-variant">
          <span className="material-symbols-outlined">explore</span>
          <span className="text-[10px] font-bold">Explore</span>
        </button>
        <button onClick={navigateToHistory} className="flex flex-col items-center gap-1 text-on-surface-variant">
          <span className="material-symbols-outlined">history</span>
          <span className="text-[10px] font-bold">History</span>
        </button>
        <button className="flex flex-col items-center gap-1 text-on-surface-variant">
          <span className="material-symbols-outlined">person</span>
          <span className="text-[10px] font-bold">Profile</span>
        </button>
      </nav>
    </div>
  );
};

export default Dashboard;
