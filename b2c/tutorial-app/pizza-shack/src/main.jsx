import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { AsgardeoProvider } from '@asgardeo/react'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AsgardeoProvider
      clientId='Rxzf4BLJUao3_Fr5nq3bWiVmPYEa'
      baseUrl='https://api.asgardeo.io/t/wso2conasia'
      preferences={{
        theme: {
          mode: 'light',
        }
      }}
    >
      <App />
    </AsgardeoProvider>
  </StrictMode>,
)
