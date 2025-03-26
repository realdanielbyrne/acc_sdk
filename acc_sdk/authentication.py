import base64
from flask import session
import requests
from urllib.parse import urlencode, quote
from datetime import datetime
from enum import Enum

class GrantType(Enum):
    ClientCreds = "client_credentials"
    AuthCode = "authorization_code"
    Refresh = "refresh_token"
    
class ResponseType(Enum):
    Code = "code"
    IdToken = "id_token"
    CodeIdToken = "code id_token"



class Authentication:

    def __init__(self, 
                 session, 
                 client_id:str, 
                 client_secret:str, 
                 admin_email:str="",
                 callback_url:str="",
                 logout_url:str=""
                 ):
        """Create a new instance of the Authentication client.

        ACCAPI Authentication Client using Oauth2.0 which retrieves,
        stores, and refreshes 2 legged client credential flow and 
        3 legged authorization code flow bearer tokens and maintains their
        state in a session or dictionary object, refreshing the tokens as
        necessary.
        
        Args:
            session (_type_): 
                Session objest where tokens are stored. Can be a Flask session
                or a Python dictionary or similar.
            client_id (str): 
                APS Client Id
            client_secret (str): 
                APS Client Secret            
            callback_url (str): 
                The URL to redirect the user to after 3 legged authorization
            logout_url (str): 
                The URL to redirect the user to after logging out.
            admin_email (str):
                The email of the admin user for 2-legged user impersonation.
          
        """

        # Session is something like a Flask session or dictionary
        self._session = session
        self.token_names = []
        # Check for valid tokens in session starting with 'accapi_' and remove if not authorized
        for key in list(self._session.keys()):
            if key.startswith("accapi_"):
                self.token_names.append(key)
                if not self.is_authorized(key):
                    del self._session[key]
                    self.token_names.remove(key)

        auth_base_url = "https://developer.api.autodesk.com/authentication/v2"
        self.oidc_spec_url = "https://developer.api.autodesk.com/.well-known/openid-configuration"
        oidc_spec = self.get_oidc_spec()        
        self.authorize_url      = oidc_spec.get("authorization_endpoint") if oidc_spec else "https://developer.api.autodesk.com/authentication/v2/authorize"
        self.jwks_url           = oidc_spec.get("jwks_uri") if oidc_spec else "https://developer.api.autodesk.com/authentication/v2/keys"        
        self.token_url          = oidc_spec.get("token_endpoint") if oidc_spec else "https://developer.api.autodesk.com/authentication/v2/token"
        self.introspect_url     = oidc_spec.get("introspect_endpoint") if oidc_spec else "https://developer.api.autodesk.com/authentication/v2/introspect"
        self.revoke_url         = oidc_spec.get("revoke_endpoint") if oidc_spec else "https://developer.api.autodesk.com/authentication/v2/revoke"
        self.user_profile_url   = oidc_spec.get("userinfo_endpoint") if oidc_spec else "https://api.userprofile.autodesk.com/userinfo"
        self.logout_url         = f"{auth_base_url}/logoutout"
        
        self.supported_scopes   = oidc_spec.get("scopes_supported") if oidc_spec else [
            "user-profile:read",
            "user:read",
            "user:write",
            "viewables:read",
            "data:read",
            "data:write",
            "data:create",
            "data:search",
            "bucket:create",
            "bucket:read",
            "bucket:update",
            "bucket:delete",
            "code:all",
            "account:read",
            "account:write",
            "openid"
            ]        

        # store initial configuration
        self.admin_email   = admin_email # optional, for 2-legged user impersonation        
        self.client_id     = client_id
        self.client_secret = client_secret        
        self.callback_url  = callback_url
        self.post_logout_url = logout_url


    ###########################################################################
    # Token Helpers
    ###########################################################################
    
    def is_authorized(self, token_name)->bool:
        """
        Check if we have a valid private (3-legged) token stored.
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"
            
        if token_name not in self.token_names:
            return False
                
        ret = not bool(self.is_expired(token_name))
        return ret
    
    def expires_in(self, token_name)->int:
        """
        Compute how many seconds remain until the stored token expires.
        Returns 0 if not set or already expired.
        """
            # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        if token_name not in self.token_names:
            return 0
        
        expires_at = self._session[token_name].get("expires_at")
        if not expires_at:
            return 0
        now = datetime.now().timestamp()
        
        diff =  int(round(expires_at - now))
        return diff

    def is_expired(self, token_name)->bool:
        """
        Return True if the currently stored token(s) are expired.
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        if token_name not in self.token_names:
            return True
                
        return self.expires_in(token_name) <= 0

    def get_user_info(self)->dict:
        """
        Retrieve the user profile of the 3-legged token holder.

        https://aps.autodesk.com/en/docs/profile/v1/reference/profile/oidcuserinfo/
        """
        access_token = self.get_3legged_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
            "Accept":        "application/json"
        }
        
        resp = requests.get(self.user_profile_url, headers=headers)
        if resp.status_code == 200:
            user_info = resp.json()
            user_info["autodeskId"] = user_info['uid'] = user_info['sub']
            return user_info
        else:
            resp.raise_for_status()

    def get_access_token(self, token_name)->dict:
        """
        Return the access_token from the stored token.
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        if token_name not in self.token_names:
            return None
        
        if self.is_expired(token_name):                            
            if self._session[token_name].get("refresh_token"):
                self.request_private_refresh_token(token_name)
            else:
                self.request_2legged_token(token_name)

        return self._session[token_name].get("access_token")

    def get_token_names(self)->list:
        """
        Return a list of all token names stored in the session.
        """
        return self.token_names

    def get_2legged_token(self)->str:
        """
        Search for the first 2 legged token in the session and return it.
        """
        # loop through auth_client._session dictionary 
        # and return the first 3legged token type found        
        for key in self.get_token_names():
            if self._session[key]["grant_type"] == GrantType.ClientCreds.value:
                return self.get_access_token(key)
            
        return None

    def get_3legged_token(self)->str:
        """
        Search for the first 3 legged token in the session and return it.
        """
        # loop through auth_client._session dictionary 
        # and return the first 3legged token type found
        for key in self.get_token_names():
            if self._session[key]["grant_type"] == GrantType.AuthCode.value:
                return self.get_access_token(key)
            
        return None
    

    ###########################################################################
    # 3 Legged, Authorization Code Token Flows
    ###########################################################################

    def get_authorization_url(self, scopes:list, **kwargs)->str:
        """
        Returns the 3-legged authorization URL for redirecting the user the the GET /authorize endpoint.

        Parameters:
            scopes(list):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.

        Notes:
            api_reference: https://aps.autodesk.com/en/docs/oauth/v2/reference/http/authorize-GET/   
            tutorial: https://aps.autodesk.com/en/docs/oauth/v2/tutorials/get-3-legged-token/

            The app_reference says that the URL should contain a parameter called "state" which is a random string
            generated by the client. This is used to prevent CSRF attacks. However, the tutorial does not mention this
            requirement and does not use it for basic(not PKCE) 3-legged auth.
          
        """        
        if not scopes:
            raise Exception("Private 3legged scope is required")

        # check scopes against self.supported_scopes
        for scope in scopes:
            if scope not in self.supported_scopes:
                # remove unsupported scopes
                scopes.remove(scope)

        if not scopes:
            raise Exception("A list of at least one allowed scope is required.")    
        
        # Build the authorize URL
        url = (
            f"{self.authorize_url}"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.callback_url}"
            f"&response_type={ResponseType.Code.value}"
            f"&scope={quote(" ".join(scopes))}"
        )

        # Append any extra query params in **kwargs (ex. if using PKCE state, nonce, etc.)       
        if kwargs:
            url += "&" + urlencode(kwargs)
        
        return url
                    
    def request_authcode_access_token(self, code:str, scopes:list, token_name="accapi_3legged")->dict:
        """
        Obtain a token using the Authorization Code Flow by exchanging an Authorization Code received
        from an Oauth callback for an access token. 
        

        Parameters:
            code(str):
                The authorization code from the redirect.  
            scopes(list):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.
            token_name:
                The name used to save and track this token in the session. 
                

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/                      
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        if not code:
            raise Exception("Authorization code is required")

        # check scopes against self.supported_scopes
        for scope in scopes:
            if scope not in self.supported_scopes:
                # remove unsupported scopes
                scopes.remove(scope)

        if not scopes:
            raise Exception("A list of at least one allowed scope is required.")       
                                    
        headers = {            
            "Content-Type":  "application/x-www-form-urlencoded",
            "User-Agent":    "Accapi/1.0"
        }
        
        data = {
            "grant_type":    GrantType.AuthCode.value,
            "code":          code,            
            "redirect_uri":  self.callback_url,
            "client_id":     self.client_id,
            "client_secret": self.client_secret            
        }                    

        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json()            
            now = datetime.now().timestamp()
            token["expires_at"] = now + token["expires_in"]
            token["grant_type"] = GrantType.AuthCode.value
            token["scopes"] = scopes
            self._session[token_name] = token

            # add token name to token_names list if not already added
            if token_name not in self.token_names:
                self.token_names.append(token_name)
        
            return token
        else:
            return Exception(f"Failed to get 3-legged token: {response.text}")

    def request_authcode_public_pkce_access_token(self, code, code_verifier, scopes:list, token_name="3legged_public_token")->dict:
        """
        Exchange an authorization code and a code_verifier for an access token wihtout sending the client_secret.
        
        Parameters:
            code(str):           
                The authorization code from the redirect.    
            code_verifier(str):  
                The code verifier used to generate the code challenge.
            scopes(list):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.
            token_name:
                The name used to save and track this token in the session.                 

        https://aps.autodesk.com/en/docs/oauth/v2/tutorials/get-3-legged-token-pkce/get-3-legged-token-pkce/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        if not code:
            raise Exception("Authorization code is required")

        # check scopes against self.supported_scopes
        for scope in scopes:
            if scope not in self.supported_scopes:
                # remove unsupported scopes
                scopes.remove(scope)

        if not scopes:
            raise Exception("A list of at least one allowed scope is required.")   
                                            
        headers = {            
            "Content-Type":  "application/x-www-form-urlencoded",
            "User-Agent":    "Accapi/1.0"
        }
        
        data = {
            "client_id":     self.client_id,
            "grant_type":    GrantType.AuthCode.value,
            "code":          code,            
            "redirect_uri":  self.callback_url,
            "code_verifier": code_verifier
        }                    

        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json()            
            now = datetime.now().timestamp()
            token["expires_at"] = now + token["expires_in"]
            token["grant_type"] = GrantType.AuthCode.value
            token["scopes"] = scopes
            self._session[token_name] = token

            # add token name to token_names list if not already added
            if token_name not in self.token_names:
                self.token_names.append(token_name)            
        else:
            raise Exception(f"Failed to get 3-legged token: {response.text}")

    def request_authcode_private_pkce_access_token(self, code, code_verifier, scopes:list, token_name="accapi_3legged")->dict:
        """
        Exchange an authorization code and a code_verifier for an access token.
        
        Parameters:
            code(required):           
                The authorization code from the redirect.    
            code_verifier(required):  
                The code verifier used to generate the code challenge.
            scopes(required):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.
            token_name:
                The name used to save and track this token in the session. 

        
        https://aps.autodesk.com/en/docs/oauth/v2/tutorials/get-3-legged-token-pkce/get-3-legged-token-pkce-private/          
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        if not code:
            raise Exception("Authorization code is required")

        # check scopes against self.supported_scopes
        for scope in scopes:
            if scope not in self.supported_scopes:
                # remove unsupported scopes
                scopes.remove(scope)

        if not scopes:
            raise Exception("No supported scopes found.")           
                                                                                
        headers = {            
            "Content-Type":  "application/x-www-form-urlencoded",
            "User-Agent":    "Accapi/1.0"
        }
        
        data = {
            "client_id":     self.client_id,
            "client_secret": self.client_secret,
            "grant_type":    GrantType.AuthCode.value,
            "code":          code,            
            "redirect_uri":  self.callback_url,
            "code_verifier": code_verifier
        }                    

        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json()            
            now = datetime.now().timestamp()
            token["expires_at"] = now + token["expires_in"]
            token["grant_type"] = GrantType.AuthCode.value
            token["scopes"] = scopes
            self._session[token_name] = token

            # add token name to token_names list if not already added
            if token_name not in self.token_names:
                self.token_names.append(token_name)            
        else:
            raise Exception(f"Failed to get 3-legged token: {response.text}")


    ###########################################################################
    # 3 Legged, Request Code Token Flows
    ###########################################################################          
        
    def request_private_refresh_token(self, scopes:list=[], token_name="accapi_3legged")->dict:
        """
        Refresh an access token with a refresh token. 
        Optionally pass in a subset of the refresh token's scopes.

        Parameters:
            scopes(list):
                A list of allowed scopes. Scopes should equivalent or a subset
                of the scopes used to request the access token.
            token_name (str): 
                The name used to save and track this token in the session.
                

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        # check scopes against self.supported_scopes        
        for scope in scopes:
            if scope not in self.supported_scopes:
                # remove unsupported scopes
                scopes.remove(scope)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent":   "Accapi/1.0"
        }
                
        data = {
            "grant_type": GrantType.Refresh.value,
            "refresh_token": self._session.get("token_name").refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,        
        }

        if scopes:
            data["scope"] = " ".join(scopes)
        
        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json()
            now = datetime.now().timestamp()
            token["expires_at"] = now + token["expires_in"]
            token["grant_type"] = GrantType.AuthCode.value
            token["scopes"] = scopes

            # Store tokens in the session
            self._session[token_name] = token            
            return token
        else:
            raise Exception(f"Failed to refresh 3-legged token: {response.text}")

    def request_public_refresh_token(self, scopes:list=[], token_name="3legged_public_token")->dict:
        """
        Refresh an access token with a refresh token. 
        Optionally pass in a subset the refresh token's scopes.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        # check scopes against self.supported_scopes
        for scope in scopes:
            if scope not in self.supported_scopes:
                # remove unsupported scopes
                scopes.remove(scope)
                        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent":   "Accapi/1.0"
        }
                
        data = {
            "grant_type":    GrantType.Refresh.value,
            "refresh_token": self._session.get("token_name").refresh_token,
            "client_id": self.client_id            
        }

        if scopes:
            data["scope"] = " ".join(scopes)

        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json()
            now = datetime.now().timestamp()
            token["expires_at"] = now + token["expires_in"]
            token["grant_type"] = GrantType.AuthCode.value
            token["scopes"] = scopes

            # Store tokens in the session
            self._session[token_name] = token            
            return token
        else:
            raise Exception(f"Failed to refresh 3-legged token: {response.text}")


    ###########################################################################
    # 2 Legged, Client Credentials Token Flow
    ###########################################################################
    
    def request_2legged_token(self, scopes:list, token_name="accapi_2legged")->dict:        
        """
        Obtain a 2 legged, Client Credentials Flow grant type, Bearer Access Token 
        using a client_id/client_secret pair.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        # check scopes against self.supported_scopes
        for scope in scopes:
            if scope not in self.supported_scopes:
                # remove unsupported scopes
                scopes.remove(scope)        
            
        if not scopes:
            raise Exception("A list of at least one scope is required.")

        scopes_str = " ".join(scopes)        
        response = requests.post(
            self.token_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Accapi/1.0"
            },
            data={
                "grant_type": GrantType.ClientCreds.value,
                "scope": scopes_str,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )

        if response.status_code == 200:
            token = response.json()
            now = datetime.now().timestamp()
            token["expires_at"] = now + int(token["expires_in"])
            token["scopes"] = scopes
            token["grant_type"] = GrantType.ClientCreds.value

            # Store tokens in the session
            self._session[token_name] = token            

            # add token name to token_names list if not already added
            if token_name not in self.token_names:
                self.token_names.append(token_name)
                            
            return token
        else:
            raise Exception(f"Failed to get 2-legged token: {response.text}")


    ###########################################################################
    # Authorization Helpers    
    ###########################################################################

    def get_logout_url(self, logout_url=None)->str:
        """
        Returns a URL GET endpoint which will clear their session and clear the tokens
        on the server.  

        Thje local session is not cleared in this method. The client should call 
        clear_token_session() after redirecting the user to this URL.
        

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/logout-GET/
        """        
        logout_url = self.logout_url
        if self.post_logout_url:
            logout_url += f"?post_logout_redirect_uri={self.logout_url}"
            
        return logout_url

    def clear_token_session(self, token_name):
        """
        Clears the session of a specific token.
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        if token_name in self._session:
            del self._session[token_name]
                    
        if token_name not in self.token_names:
            self.token_names.remove(token_name)

    def clear_all_tokens(self):
        """
        Clears all tokens from the session.
        """
        for token_name in self.token_names:
            self.clear_token_session(token_name)
        
    def revoke_public_token(self, token_name="accapi_3legged", token_type="access_token"):
        """
        Revoke a token using the POST revoke endpoint.
        
        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/revoke-POST/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Accapi/1.0"
        }
        
        data = {
            "token": self._session.get(token_name).get(token_type),
            "token_type_hint": token_type,
            "client_id": self.client_id,            
        }

        response = requests.post(self.revoke_url, headers=headers, data=data)
        if response.status_code == 200:
            if token_name in self._session:
                del self._session[token_name]
                        
            if token_name not in self.token_names:
                self.token_names.remove(token_name)            
            return response.json()
        else:
            raise Exception(f"Failed to revoke token: {response.text}")

    def revoke_private_token(self, token_name="accapi_3legged", token_type="access_token"):
        """
        Revoke a token using the POST revoke endpoint.

        Parameters:
            token(required): The token to revoke.
            token_type: The type of token to revoke (access_token | refresh_token).
        
        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/revoke-POST/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        auth = f"{self.client_id}:{self.client_secret}"
        auth = base64.b64encode(auth.encode()).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Accapi/1.0"
        }
        
        data = {
            "token": self._session.get(token_name).get(token_type),
            "token_type_hint": token_type,            
        }

        response = requests.post(self.revoke_url, headers=headers, data=data)
        if response.status_code == 200:
            if token_name in self._session:
                del self._session[token_name]
                        
            if token_name not in self.token_names:
                self.token_names.remove(token_name)            
            return response.json()
        else:
            raise Exception(f"Failed to revoke token: {response.text}")        

    def introspect_public_token(self, token_name="accapi_3legged"):
        """
        Introspect a token to determine its validity.
        
        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/introspect-POST/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Accapi/1.0"
        }
        
        data = {
            "token": self._session.get(token_name).get("access_token"),
            "client_secret": self.client_secret
        }

        response = requests.post(self.introspect_url, headers=headers, data=data)
        if response.status_code == 200:      
            return response.json()
        else:
            raise Exception(f"Failed to introspect token: {response.text}")

    def introspect_private_token(self, token_name="accapi_3legged"):
        """
        Introspect a token to determine its validity.
        
        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/introspect-POST/
        """
        # check to see token_name starts with accapi_
        if not token_name.startswith("accapi_"):
            token_name = f"accapi_{token_name}"

        auth = f"{self.client_id}:{self.client_secret}"
        auth = base64.b64encode(auth.encode()).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Accapi/1.0"
        }
        
        data = {
            "token": self._session.get(token_name).get("access_token"),
        }

        response = requests.post(self.introspect_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to introspect token: {response.text}")

    def get_oidc_spec(self)->dict:
        """
        Retrieve the OpenID Connect Discovery Document.
        
        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/.well-known/openid-configuration-GET/
        """
        response = requests.get(self.oidc_spec_url)
        if response.status_code == 200:
            return response.json()        
