import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './app.tsx'

createRoot(document.getElementById('root')!).render(
  // Temporarily disable StrictMode to prevent Onfido double initialization in development
  // <StrictMode>
    <App />
  // </StrictMode>,
)