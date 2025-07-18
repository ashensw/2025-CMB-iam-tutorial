const path = require('path');
const withFonts = require('next-fonts');
const withLess = require('next-with-less');
const tsconfig = require('./tsconfig.base.json');

const alias = Object.entries(tsconfig.compilerOptions.paths).reduce((acc, [key, value]) => {
  const cleanedKey = key.replace(/\/*$/, '');
  const cleanedValue = value[0].replace(/\/*$/, '');
  acc[cleanedKey] = path.join(__dirname, cleanedValue);
  return acc;
}, {});

const nextConfig = {
  lessLoaderOptions: {
    lessOptions: {
      strictMath: true
    }
  },
  webpack(config) {
    config.resolve.alias = { ...config.resolve.alias, ...alias };
    return config;
  },
  publicRuntimeConfig: {
    adminRole: process.env.ADMIN_ROLE_NAME,
    baseOrgUrl: process.env.BASE_ORG_URL,
    baseUrl: process.env.BASE_URL,
    meetingServiceUrl: process.env.MEETING_SERVICE_URL,
    clientId: process.env.CLIENT_ID,
    hostedUrl: process.env.HOSTED_URL,
    personalizationServiceUrl: process.env.PERSONALIZATION_SERVICE_URL,
    petManagementServiceUrl: process.env.PET_MANAGEMENT_SERVICE_URL,
    sharedAppName: process.env.SHARED_APP_NAME
  }
};

module.exports = withFonts(withLess(nextConfig));
