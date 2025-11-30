# Deploy to Production

Execute the production deployment process:

1. Confirm deployment type (full/backend/frontend)
2. Execute deployment script: `cd deploy/scripts && ./update-production.sh`
3. Monitor progress and show each step
4. Verify deployment success
5. Report results to user

**Production Info:**
- URL: https://qwquant.com
- Server: 82.157.28.35
- User: ubuntu

**Script Options:**
- `./update-production.sh` - Full update (frontend + backend)
- `./update-backend.sh` - Backend only
- `./update-frontend.sh` - Frontend only

Display progress and final verification including service status and HTTPS test.
