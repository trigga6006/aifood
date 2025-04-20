import React from 'react';
import { createBrowserRouter, RouterProvider, Route, createRoutesFromElements } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';

// React Router v7 uses a different approach than v6
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Dashboard />} />
  )
);

function App() {
  return (
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <RouterProvider router={router} />
    </div>
  );
}

export default App;