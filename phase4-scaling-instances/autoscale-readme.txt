# New instances are created but we need to change Ip of frontend instance with the lastest backend instance

# Backend
-> ssh to new backend instance 
ssh -i "TMKeyPrinceBackend.pem" ubuntu@3.109.22.154
cd TravelMemory/backend
node index.js

--> testing:
http://3.109.22.154:3000/trip


# Frontend
cd /TravelMemory/frontend/src
sudo nano url.js
--------------------------------------------------------------------------------------------
export const baseUrl = process.env.REACT_APP_BACKEND_URL || "http://3.109.22.154:3000";
--------------------------------------------------------------------------------------------

cd ..
npm run build
sudo cp -r build/* /var/www/html/

npm start

--> testing:
