from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.oauth_client import OAuthClient
from app.schemas.oauth import OAuthClientCreate, OAuthClientResponse
from app.core.security import generate_client_id, generate_client_secret


class CRUDOAuthClient(CRUDBase[OAuthClient, OAuthClientCreate, OAuthClientResponse]):
    def get_by_client_id(self, db: Session, *, client_id: str) -> Optional[OAuthClient]:
        return db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    
    def create(self, db: Session, *, obj_in: OAuthClientCreate) -> OAuthClient:
        # Generate client credentials
        client_id = generate_client_id()
        client_secret = generate_client_secret()
        
        db_obj = OAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            client_name=obj_in.client_name,
            client_description=obj_in.client_description,
            client_uri=obj_in.client_uri,
            grant_types=obj_in.grant_types,
            response_types=obj_in.response_types,
            redirect_uris=obj_in.redirect_uris,
            scope=obj_in.scope,
            is_confidential=obj_in.is_confidential,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate_client(
        self, 
        db: Session, 
        *, 
        client_id: str, 
        client_secret: str
    ) -> Optional[OAuthClient]:
        """Authenticate OAuth client."""
        client = self.get_by_client_id(db, client_id=client_id)
        if not client:
            return None
        if not client.is_active:
            return None
        if client.is_confidential and client.client_secret != client_secret:
            return None
        return client
    
    def is_redirect_uri_valid(
        self, 
        db: Session, 
        *, 
        client_id: str, 
        redirect_uri: str
    ) -> bool:
        """Check if redirect URI is valid for the client."""
        client = self.get_by_client_id(db, client_id=client_id)
        if not client:
            return False
        return redirect_uri in client.redirect_uris
    
    def supports_grant_type(
        self, 
        db: Session, 
        *, 
        client_id: str, 
        grant_type: str
    ) -> bool:
        """Check if client supports the grant type."""
        client = self.get_by_client_id(db, client_id=client_id)
        if not client:
            return False
        return grant_type in client.grant_types
    
    def supports_response_type(
        self, 
        db: Session, 
        *, 
        client_id: str, 
        response_type: str
    ) -> bool:
        """Check if client supports the response type."""
        client = self.get_by_client_id(db, client_id=client_id)
        if not client:
            return False
        return response_type in client.response_types


oauth_client_crud = CRUDOAuthClient(OAuthClient)

