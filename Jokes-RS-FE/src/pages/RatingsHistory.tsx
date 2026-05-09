import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';

const RatingsHistory: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId, currentModel, ratingHistory } = useAppStore();
  const [filter, setFilter] = useState('All');
  const [sort, setSort] = useState('Newest');

  const getIconForRating = (rating: number) => {
    if (rating >= 5) return 'sentiment_very_satisfied';
    if (rating >= 0) return 'sentiment_satisfied';
    return 'sentiment_very_dissatisfied';
  };

  const getColorForRating = (rating: number) => {
    if (rating >= 5) return 'bg-primary-container text-on-primary-container';
    if (rating >= 0) return 'bg-secondary-container text-on-secondary-container';
    return 'bg-error-container text-on-error-container';
  };

  const getIconColorForRating = (rating: number) => {
    if (rating >= 5) return 'bg-secondary-container text-on-secondary-container';
    if (rating >= 0) return 'bg-secondary-container text-on-secondary-container';
    return 'bg-error-container text-on-error-container';
  };

  const timeAgo = (dateStr?: string) => {
    if (!dateStr) return 'Just now';
    const seconds = Math.floor((new Date().getTime() - new Date(dateStr).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} mins ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hours ago`;
    return `${Math.floor(hours / 24)} days ago`;
  };

  // Mock data if history is empty for demonstration purposes
  const displayHistory = ratingHistory.length > 0 ? ratingHistory : [
    {
      user_id: 1, joke_id: 1, rating: 8.5, created_at: new Date(Date.now() - 120000).toISOString(), updated_at: '',
      joke: { joke_id: 1, joke_text: "Why did the data scientist stay in the shower? The instructions said: Lather, Rinse, Repeat...", category: "Tech Humor" }
    },
    {
      user_id: 1, joke_id: 2, rating: -2.0, created_at: new Date(Date.now() - 900000).toISOString(), updated_at: '',
      joke: { joke_id: 2, joke_text: "I told my wife she was drawing her eyebrows too high. She looked surprised.", category: "Dad Jokes" }
    },
    {
      user_id: 1, joke_id: 3, rating: 6.2, created_at: new Date(Date.now() - 3600000).toISOString(), updated_at: '',
      joke: { joke_id: 3, joke_text: "Parallel lines have so much in common. It's a shame they'll never meet.", category: "Math Jokes" }
    }
  ];

  const navigateToDashboard = () => navigate('/dashboard');
  const navigateToModels = () => navigate('/models');

  return (
    <div className="font-body-md text-on-background selection:bg-primary-container min-h-screen bg-background pb-24 md:pb-0">
      <div className="fixed top-0 left-0 w-full h-1 bg-surface-container z-50">
        <div className="h-full bg-primary-container w-2/3"></div>
      </div>

      <header className="bg-surface dark:bg-surface-dim docked full-width top-0 z-30 sticky">
        <div className="flex justify-between items-center w-full px-md py-sm max-w-container-max mx-auto">
          <div className="flex items-center gap-sm">
            <span className="font-display-lg text-headline-md font-black text-primary dark:text-primary-fixed-dim cursor-pointer" onClick={() => navigate('/')}>JokeRec</span>
          </div>
          <div className="flex items-center gap-md">
            <span className="text-on-surface-variant font-body-md hidden sm:block">Session: #{sessionId?.slice(-4) || '8821'}</span>
            <span className="text-primary dark:text-primary-fixed-dim font-headline-md text-headline-md cursor-pointer" onClick={navigateToModels}>Model: {currentModel.toUpperCase()}</span>
          </div>
        </div>
      </header>

      <div className="flex max-w-container-max mx-auto px-md gap-lg">
        <aside className="hidden md:flex flex-col p-md w-64 bg-surface-container-low dark:bg-surface-container-highest docked left-0 h-[calc(100vh-80px)] sticky top-[80px] rounded-xl my-md shadow-sm">
          <div className="mb-lg">
            <h2 className="font-headline-md text-headline-md text-primary">Your Feed</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Personalized Jokes</p>
          </div>
          <nav className="flex flex-col gap-xs flex-grow">
            <span onClick={navigateToDashboard} className="flex items-center gap-sm px-md py-sm text-on-surface-variant hover:bg-surface-variant rounded-xl transition-all group cursor-pointer">
              <span className="material-symbols-outlined">auto_awesome</span>
              <span className="font-body-md">Top Recommendations</span>
            </span>
            <span className="flex items-center gap-sm px-md py-sm text-on-secondary-container bg-secondary-container rounded-xl font-bold transition-all cursor-pointer">
              <span className="material-symbols-outlined">history</span>
              <span className="font-body-md">Recent Ratings</span>
            </span>
          </nav>
          <button onClick={navigateToDashboard} className="mt-xl bg-primary-container text-on-primary-container font-bold py-sm px-md rounded-full flex items-center justify-center gap-xs transition-transform duration-200 scale-100 hover:scale-105 active:scale-95">
            <span className="material-symbols-outlined">casino</span>
            Surprise Me
          </button>
        </aside>

        <main className="flex-1 py-md max-w-3xl">
          <div className="mb-lg">
            <h1 className="font-display-lg text-headline-md font-black text-on-surface mb-xs">Rating History</h1>
            <p className="font-body-md text-on-surface-variant">Review and refine your sense of humor preferences.</p>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-sm mb-md bg-surface-container-low p-sm rounded-xl">
            <div className="flex items-center gap-sm">
              <div className="flex items-center gap-xs bg-surface-container-lowest px-md py-xs rounded-full border border-outline-variant">
                <span className="material-symbols-outlined text-[18px]">sort</span>
                <select 
                  className="bg-transparent border-none focus:ring-0 font-label-caps text-label-caps cursor-pointer outline-none"
                  value={sort}
                  onChange={(e) => setSort(e.target.value)}
                >
                  <option>Sort by: Newest</option>
                  <option>Sort by: Highest Rated</option>
                  <option>Sort by: Lowest Rated</option>
                </select>
              </div>
              <div className="flex items-center gap-xs bg-surface-container-lowest px-md py-xs rounded-full border border-outline-variant">
                <span className="material-symbols-outlined text-[18px]">filter_alt</span>
                <select 
                  className="bg-transparent border-none focus:ring-0 font-label-caps text-label-caps cursor-pointer outline-none"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option>Filter by: All</option>
                  <option>Filter by: Positive</option>
                  <option>Filter by: Negative</option>
                </select>
              </div>
            </div>
            <div className="hidden sm:block text-on-surface-variant font-label-caps uppercase tracking-widest">
              Showing {displayHistory.length} Ratings
            </div>
          </div>

          <div className="space-y-sm">
            {displayHistory.map((rating, idx) => (
              <React.Fragment key={idx}>
                <div className="bg-surface-container-lowest p-md rounded-xl joke-card-shadow joke-card-hover transition-all flex items-center gap-md">
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${getIconColorForRating(rating.rating)}`}>
                    <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                      {getIconForRating(rating.rating)}
                    </span>
                  </div>
                  <div className="flex-grow min-w-0">
                    <p className="font-body-md text-on-surface truncate pr-md">"{rating.joke?.joke_text}"</p>
                    <div className="flex items-center gap-sm mt-xs">
                      <span className="font-label-caps text-label-caps text-on-surface-variant">{timeAgo(rating.created_at)}</span>
                      <span className="w-1 h-1 bg-outline-variant rounded-full"></span>
                      <span className="font-label-caps text-label-caps text-primary font-bold">{rating.joke?.category || 'General'}</span>
                    </div>
                  </div>
                  <div className="text-right flex flex-col items-end gap-xs">
                    <div className={`${getColorForRating(rating.rating)} px-sm py-xs rounded-lg font-bold text-headline-md`}>
                      {rating.rating > 0 ? '+' : ''}{rating.rating.toFixed(1)}
                    </div>
                    <button className="font-label-caps text-label-caps text-on-surface-variant hover:text-primary transition-colors flex items-center gap-xs">
                      <span className="material-symbols-outlined text-[14px]">refresh</span>
                      RE-RATE
                    </button>
                  </div>
                </div>

                {idx === 2 && (
                  <div className="relative w-full h-48 rounded-3xl overflow-hidden my-lg shadow-lg group">
                    <img alt="Sophisticated humor background" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" src="https://lh3.googleusercontent.com/aida-public/AB6AXuABezMvCU6hKjMJBrNKQsJHGzaZ2tZlQNDq2Sce3b0l3dSbHtwvR55oUOn7VoZahw_fDY0XjqCg4M3FbaDKrzEyeWVtLMpONDhP_wlxZgmWoaXxTXGmZNffpqHJuhg94JWUTX-o61Phc-4eRQeUjnNGypMYRFoJtpONszI7pBI1FIPMc6ffj0rWipEybshY_04517j32VoqQL9kJFUdi4tvWB5E6MdTvAySIfbDGV53ZUEfGYeYFIlfATJOaJ0JHv3ysIr7bqMt6gzK" />
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/40 to-transparent flex items-center p-xl">
                      <div className="max-w-xs">
                        <h3 className="font-display-lg text-headline-md text-white mb-xs">Refine your taste.</h3>
                        <p className="text-white/90 font-body-md">Your ratings train our custom {currentModel.toUpperCase()} model to find your unique humor sweet spot.</p>
                      </div>
                    </div>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>

          {ratingHistory.length === 0 && (
            <div className="flex flex-col items-center justify-center py-xl text-center">
              <div className="w-24 h-24 bg-surface-container-high rounded-full flex items-center justify-center mb-md">
                <span className="material-symbols-outlined text-outline text-[48px]">history_toggle_off</span>
              </div>
              <h3 className="font-headline-md text-headline-md text-on-surface mb-xs">No ratings yet?</h3>
              <p className="font-body-md text-on-surface-variant max-w-xs mb-lg">Your history is looking a bit quiet. Head back to the feed and start sharing your thoughts!</p>
              <button onClick={navigateToDashboard} className="bg-primary text-on-primary px-lg py-sm rounded-full font-bold transition-transform active:scale-95">Go to Feed</button>
            </div>
          )}

          <div className="flex items-center justify-center gap-sm mt-xl">
            <button className="w-10 h-10 rounded-full border border-outline-variant flex items-center justify-center text-on-surface hover:bg-surface-variant transition-colors">
              <span className="material-symbols-outlined">chevron_left</span>
            </button>
            <span className="font-body-md text-on-surface px-md">Page 1 of 1</span>
            <button className="w-10 h-10 rounded-full border border-outline-variant flex items-center justify-center text-on-surface hover:bg-surface-variant transition-colors">
              <span className="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </main>
      </div>

      <nav className="md:hidden fixed bottom-0 left-0 w-full bg-surface border-t border-outline-variant/20 px-sm py-xs flex justify-around items-center z-40">
        <span onClick={navigateToDashboard} className="flex flex-col items-center p-xs text-on-surface-variant cursor-pointer">
          <span className="material-symbols-outlined">auto_awesome</span>
          <span className="text-[10px] font-bold">Feed</span>
        </span>
        <span className="flex flex-col items-center p-xs text-primary cursor-pointer">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>history</span>
          <span className="text-[10px] font-bold">History</span>
        </span>
        <span className="flex flex-col items-center p-xs text-on-surface-variant cursor-pointer">
          <span className="material-symbols-outlined">person</span>
          <span className="text-[10px] font-bold">Profile</span>
        </span>
      </nav>
    </div>
  );
};

export default RatingsHistory;
