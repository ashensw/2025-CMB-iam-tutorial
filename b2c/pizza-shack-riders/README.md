# Pizza Shack Riders - Delivery Partner Registration App

A modern React application for Pizza Shack delivery rider registration with integrated age verification using Onfido and WSO2 Asgardeo authentication. This app allows potential delivery partners to register for various delivery plans after completing a secure age verification process.

## Features

✅ **Modern Glassmorphic UI** - Clean, professional design matching Pizza Shack branding  
✅ **Secure Authentication** - Powered by WSO2 Asgardeo React SDK v5.4.0  
✅ **Age Verification** - Integrated Onfido identity verification before registration  
✅ **Delivery Plan Selection** - Multiple rider options (Bicycle, Car, Delivery Van)  
✅ **Responsive Design** - Optimized for mobile and desktop use  
✅ **Complete Registration Flow** - Login → Age Verification → Plan Selection → Success  

## User Journey

1. **Landing Page**: Clean login interface with Pizza Shack branding
2. **Authentication**: Secure login via WSO2 Asgardeo
3. **Plan Selection**: View available delivery plans (initially disabled)
4. **Age Verification**: Complete Onfido identity verification process
5. **Registration**: Select and register for a delivery plan
6. **Success**: Confirmation with next steps and onboarding information

## Technology Stack

- **Frontend**: React 19 + TypeScript + Vite
- **Authentication**: WSO2 Asgardeo React SDK 5.4.0
- **Identity Verification**: Onfido SDK
- **Styling**: Modern CSS with design tokens
- **UI Components**: Oxygen UI React components

## Prerequisites

- Node.js 18+ 
- NPM or Yarn
- WSO2 Identity Server / Asgardeo account
- Onfido account and API keys

## Getting Started

### 1. WSO2 Asgardeo Configuration

1. **Register Your Application**:
   - Go to [Asgardeo Console](https://console.asgardeo.io/)
   - Create a new Single Page Application
   - Configure redirect URLs: `http://localhost:5174`
   - Note your `CLIENT_ID` and `BASE_URL`

2. **Configure User Attributes**:
   - Ensure user profiles have: `given_name`, `family_name`, `birthdate`
   - These are required for Onfido verification matching
   - **📖 See [USER_SETUP_GUIDE.md](./USER_SETUP_GUIDE.md) for detailed user setup instructions**

### 2. Onfido Configuration

1. **Create Onfido Account**: [Onfido Dashboard](https://onfido.com/)
2. **Configure Identity Verification Provider** in Asgardeo:
   - Follow [Onfido Connector Documentation](https://github.com/wso2-extensions/identity-verification-onfido/blob/main/docs/config.md)
   - Configure attribute mappings:
     - `first_name` → `http://wso2.org/claims/givenname`
     - `last_name` → `http://wso2.org/claims/lastname`  
     - `dob` → `http://wso2.org/claims/dob`
   - Note your `IDENTITY_VERIFICATION_PROVIDER_ID`

### 3. Application Setup

1. **Clone and Install**:
   ```bash
   cd pizza-shack-riders
   npm install
   ```

2. **Configuration**:
   Create `public/runtime-config.json`:
   ```json
   {
       "clientID": "YOUR_ASGARDEO_CLIENT_ID",
       "baseUrl": "https://api.asgardeo.io/t/YOUR_ORG",
       "signInRedirectURL": "http://localhost:5174",
       "signOutRedirectURL": "http://localhost:5174",
       "userPortalURL": "https://myaccount.asgardeo.io/t/YOUR_ORG",
       "scope": ["openid", "profile", "internal_login"],
       "identityVerificationProviderId": "YOUR_ONFIDO_IDVP_ID"
   }
   ```

3. **Environment Variables** (Optional):
   ```bash
   cp .env.example .env
   # Edit .env if you need custom port or base URL
   ```

4. **Run Development Server**:
   ```bash
   npm run dev
   ```
   
   Application opens at: http://localhost:5174 (or next available port)

## Application Structure

```
pizza-shack-riders/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── NavBar.tsx       # Modern navigation bar
│   │   ├── Plans.tsx        # Delivery plan selection
│   │   ├── AgeVerificationDrawer.tsx  # Verification prompt
│   │   └── Footer.tsx       # App footer
│   ├── pages/               # Route components
│   │   ├── LoginPage.tsx    # Landing/login page
│   │   ├── HomePage.tsx     # Main dashboard
│   │   ├── VerifyPage.tsx   # Onfido verification
│   │   └── SuccessPage.tsx  # Registration success
│   ├── api/                 # API client functions
│   ├── styles/              # Theme and styling
│   ├── utils/               # Helper functions
│   └── app.tsx              # Main app component
├── public/
│   ├── images/              # App assets
│   └── runtime-config.json  # Configuration file
└── package.json
```

## Delivery Plans

| Plan | Price/Month | Capacity | Distance | Duration |
|------|-------------|----------|----------|----------|
| **Bicycle Rider** | $200 | 1 location | 5 km | 30 mins |
| **Car Rider** | $250 | 4 locations | 15 km | 2 hours |
| **Delivery Van** | $300 | 8 locations | 30 km | 4 hours |

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production  
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Customization

**Branding**: Update design tokens in `src/index.css`
**Plans**: Modify plans data in `src/components/Plans.tsx`  
**Styling**: All styles use CSS custom properties for consistency

## Configuration Options

### Runtime Config (`public/runtime-config.json`)

| Property | Description | Example |
|----------|-------------|---------|
| `clientID` | Asgardeo application client ID | `abc123...` |
| `baseUrl` | Asgardeo organization base URL | `https://api.asgardeo.io/t/myorg` |
| `signInRedirectURL` | Post-login redirect | `http://localhost:5174` |
| `signOutRedirectURL` | Post-logout redirect | `http://localhost:5174` |
| `userPortalURL` | User account management | `https://myaccount.asgardeo.io/t/myorg` |
| `scope` | OAuth scopes | `["openid", "profile"]` |
| `identityVerificationProviderId` | Onfido provider ID | `onfido-idvp-123` |

## Troubleshooting

### Common Issues

**Authentication not working?**
- Verify `clientID` and `baseUrl` in runtime-config.json
- Check redirect URLs match in Asgardeo console
- Ensure CORS origins are configured

**Age verification failing?**
- Confirm Onfido connector is properly configured
- Check attribute mappings in identity provider
- Verify user profile has required attributes

**App not loading?**
- Check browser console for errors
- Verify Node.js version (18+)
- Clear browser cache and restart dev server
- If you see "process is not defined" error, ensure you're using the latest code with Vite environment variables

### Getting Help

- [WSO2 Identity Server Documentation](https://is.docs.wso2.com/)
- [Asgardeo Documentation](https://wso2.com/asgardeo/docs/)
- [Onfido Developer Documentation](https://documentation.onfido.com/)

## Security Considerations

- All authentication flows use industry-standard OAuth 2.0/OIDC
- Identity verification performed via secure Onfido integration
- No sensitive data stored in local storage
- HTTPS required for production deployment

## License

Copyright (c) 2025, WSO2 LLC. Licensed under the Apache License, Version 2.0.

---

**Pizza Shack Riders** - Delivering delicious food with verified, trusted partners! 🍕🚗