# Navigating IAM in the Modern Enterprise

## Overview

Managing identity and access is a critical cornerstone for enterprise security, agility and user experience today. It is critically important for  all users that include employees of an enterprise (B2E), consumers (B2C), as well as business customers, partners, or franchises (B2B).

The technical deep dive of this tutorial mainly focuses on managing secure and frictionless access for consumer facing applications (web and mobile), and B2B customer facing SaaS applications.

**CIAM for consumer facing applications**
1. Integrating a SPA with Asgardeo and managing access for that application.
 - Self registration
 - Account linking
 - Self service account management
 - Single Logout (SLO)
 - Multi-Factor Authentication (MFA)
 - Passwordless Authentication
 - Access a high assurance API
 - Integrate with Salesforce

2. Providing a native access experience for a mobile application still adhering to best security practices using the In-App Authentication API
   
   <img width="800" alt="Screenshot 2024-05-03 at 3 59 01 PM" src="https://github.com/wso2con2024/iam-tutorial/assets/4951983/f65cab54-f319-4356-a66f-2d21ab0ae08d">

Check the instruction in the [guide](/b2c/README.md) to try out the B2C lab session.

## Quick Start - Pizza Shack Application

To start all Pizza Shack services (frontend, API, agent, and riders app):

```bash
cd b2c
./start_pizza_shack.sh
```

**📋 Technical Architecture**: For detailed technical documentation of the Pizza Shack application architecture, including CrewAI integration, WebSocket implementation, and data flow patterns, see the [Architecture Guide](/b2c/PIZZA_SHACK_ARCHITECTURE_GUIDE.md).

### Application Components

1. **Pizza Shack Frontend** - React application (http://localhost:5173/)
2. **Pizza API** - FastAPI backend for orders and menu (http://localhost:8000/)
3. **Pizza Agent** - AI-powered chatbot service (http://localhost:8001/)
4. **Pizza Shack Riders** - React rider management app (http://localhost:5174/)

**CIAM for B2B Customer facing applications**

Integrating a B2B Saas app with WSO2 Identity Server and serving self serviced access management and administration for B2B customers.
- Authorizing APIs
- Managing organizations
- Delegating administrative access for customer organization admins
- Configuring login and access policies per customer organization
- Support for customers’ branding
- Let customers to selectively subscribe to apps
- Modelling reseller/partner usecases with organization hierarchies

Check the instruction in the [guide](/b2b/README.md) to try out the B2B lab session.