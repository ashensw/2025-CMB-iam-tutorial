import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { AsgardeoProvider } from '@asgardeo/react'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AsgardeoProvider
      clientId='T54WRrMa4zZvS0_7PhjQF0u077Ua'
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
