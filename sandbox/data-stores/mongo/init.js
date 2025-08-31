// Initialize MongoDB for sandbox (example only; do not commit real creds)
db = db.getSiblingDB('sandbox_db');
db.createUser({
  user: 'CHANGE_ME_USER',
  pwd: 'CHANGE_ME_PASSWORD',
  roles: [{ role: 'readWrite', db: 'sandbox_db' }]
});
