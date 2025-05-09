import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles/main.css';
import App from './App';

const rootElement = document.getElementById('root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(<App />);
}