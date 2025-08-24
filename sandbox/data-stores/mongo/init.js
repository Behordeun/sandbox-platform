// Initialize MongoDB for sandbox
db = db.getSiblingDB('sandbox_db');
db.createUser({
  user: 'sandbox_user',
  pwd: 'sandbox_password',
  roles: [{ role: 'readWrite', db: 'sandbox_db' }]
});