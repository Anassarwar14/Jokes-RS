import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import RatingsHistory from './pages/RatingsHistory';
import ModelInfo from './pages/ModelInfo';
import { useAppStore } from './store/useAppStore';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const sessionId = useAppStore((state) => state.sessionId);
  if (!sessionId) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <Router>
      <Toaster position="top-center" richColors />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/history" 
          element={
            <ProtectedRoute>
              <RatingsHistory />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/models" 
          element={
            <ProtectedRoute>
              <ModelInfo />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;
