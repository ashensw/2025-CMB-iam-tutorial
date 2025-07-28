# Pizza Shack Riders - User Setup Guide

## Age Verification Requirements

The Pizza Shack Riders app requires age verification through Onfido. Before you can complete the verification process, your Asgardeo user profile must contain specific required attributes.

### Required Profile Attributes

For age verification to work, you must have these attributes set in your Asgardeo profile:

- ✅ **First Name** (`givenname`)
- ✅ **Last Name** (`lastname`) 
- ✅ **Date of Birth** (`dob`)

### How to Update Your Profile

1. **Access MyAccount Portal**
   - Go to: https://myaccount.asgardeo.io/t/wso2conasia
   - Sign in with your Asgardeo credentials

2. **Navigate to Profile Section**
   - Click on "Profile" in the left sidebar
   - You'll see your user profile information

3. **Fill Required Fields**
   - **First Name**: Enter your legal first name
   - **Last Name**: Enter your legal last name
   - **Date of Birth**: Enter your date of birth (format: YYYY-MM-DD)

4. **Save Changes**
   - Click "Update Profile" or "Save" button
   - Wait for confirmation that your profile was updated

5. **Return to App**
   - Go back to the Pizza Shack Riders app
   - Try the age verification process again

### Common Issues and Solutions

#### ❌ Error: "OIDV-10002"
This error occurs when required profile attributes are missing.

**Solution**: Complete all required profile fields as described above.

#### ❌ Age Verification Fails
If age verification still fails after updating your profile:

1. **Check attribute mapping**: Ensure your Asgardeo org has proper attribute mappings
2. **Wait for sync**: Sometimes it takes a few minutes for profile changes to sync
3. **Clear browser cache**: Clear your browser cache and try again
4. **Contact support**: If issues persist, contact your administrator

### Development Debug Info

If you're running the app in development mode, you'll see a debug panel in the bottom-right corner showing:
- Authentication status
- Username
- Available user claims
- Configuration details

This can help troubleshoot profile attribute issues.

### Testing the Flow

1. **Login**: Sign in with your Asgardeo account
2. **Profile Check**: App will automatically check if your profile is complete
3. **Age Verification**: If profile is complete, you can proceed with Onfido verification
4. **Plan Selection**: After successful verification, you can select a rider plan

### Support

If you continue experiencing issues:
- Check the browser console for detailed error messages
- Verify your Asgardeo profile contains all required attributes
- Contact your system administrator for configuration assistance