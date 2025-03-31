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
    """
    This class provides methods to manage authentication with the Autodesk Construction Cloud API.
    It supports both 2-legged and 3-legged OAuth flows, token management, and various authentication-related operations.

    Example:
        ```python
        # Initialize authentication
        auth_client = Authentication(
            client_id="your_client_id",
            client_secret="your_client_secret",
            admin_email="admin@example.com",  # Optional, for 2-legged user impersonation
            session={},  # Flask session or dictionary to store tokens
            callback_url="http://your-app/callback",  # Required for 3-legged flow
            logout_url="http://your-app/logout"  # Optional, for logout redirect
        )

        # 2-legged authentication
        scopes = ["data:read", "data:write", "account:read", "account:write"]
        token = auth_client.request_2legged_token(scopes=scopes)

        # 3-legged authentication
        auth_url = auth_client.get_authorization_url(scopes=scopes)
        # Redirect user to auth_url, then handle callback:
        token_data = auth_client.request_authcode_access_token(
            code=request.args.get("code"),
            scopes=scopes
        )
        ```
    """

    def __init__(self, 
                 client_id:str, 
                 client_secret:str="", 
                 admin_email:str="",
                 session = {}, 
                 callback_url:str="",
                 logout_url:str=""
                 ):
        """
        Create a new instance of the Authentication client.

        The AccSdk Authentication module implements methods to use the the OAuth2 2-legged and 3-legged authentication processes, and it 
        manages the tokens and their liftimes. The Authentication module class provides the necessary methods to

        - Authenticate with the ACC API using 
            - 2 legged OAuth Client Credential flow 
            - 3 legged OAuth Authorization Code flow 
        - Maintain the validity of tokens, by refreshing them as they expire
        - Manage both 2-legged and 3-legged tokens concurrently to give you full access to the API services
        - Revoke tokens
        - Introspect tokens to check their validity
        - Logout of the 3-legged session
        - Get the user profile of the 3-legged token holder
        - Get the OpenID Connect Discovery Document
        - Get the APIs supported scopes

        Args:
            session (dict): 
                Session object where tokens are stored. Can be a Flask session
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

        Example:
            ```python
            # Basic initialization
            auth_client = Authentication(
                client_id="your_client_id",
                client_secret="your_client_secret"
            )

            # Full initialization with Flask session
            from flask import session
            auth_client = Authentication(
                client_id="your_client_id",
                client_secret="your_client_secret",
                admin_email="admin@example.com",
                session=session,
                callback_url="http://localhost:5000/callback",
                logout_url="http://localhost:5000/logout"
            )
            ```
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

        Args:
            token_name (str):
                The name of the token to check.

        Returns:
            bool: True if the token is valid, False otherwise.

        Example:
            ```python
            # Check if 3-legged token is valid
            is_valid = auth_client.is_authorized("accapi_3legged")
            if is_valid:
                print("Token is valid")
            else:
                print("Token is invalid or expired")
            ```
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

        Args:
            token_name (str):
                The name of the token to check.

        Returns:
            int: The number of seconds until the token expires.

        Example:
            ```python
            # Check token expiration
            seconds_remaining = auth_client.expires_in("accapi_3legged")
            if seconds_remaining > 0:
                print(f"Token expires in {seconds_remaining} seconds")
            else:
                print("Token is expired")
            ```
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

        Args:
            token_name (str):
                The name of the token to check.

        Returns:
            bool: True if the token is expired, False otherwise.

        Example:
            ```python
            # Check if token is expired
            if auth_client.is_expired("accapi_3legged"):
                print("Token is expired, refreshing...")
                auth_client.request_private_refresh_token()
            else:
                print("Token is still valid")
            ```
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

        Returns:
            dict: The user profile of the 3-legged token holder.

        Example:
            ```python
            # Get user profile information
            user_info = auth_client.get_user_info()
            print(f"User name: {user_info['name']}")
            print(f"User email: {user_info['email']}")
            print(f"User ID: {user_info['uid']}")
            ```
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

        Args:
            token_name (str):
                The name of the token to check.

        Returns:
            str: The access token.

        Example:
            ```python
            # Get access token
            access_token = auth_client.get_access_token("accapi_3legged")
            if access_token:
                print("Access token retrieved successfully")
            else:
                print("No valid access token found")
            ```
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

        Returns:
            list: A list of all token names stored in the session.

        Example:
            ```python
            # Get all token names
            token_names = auth_client.get_token_names()
            print("Available tokens:")
            for name in token_names:
                print(f"- {name}")
            ```
        """
        return self.token_names

    def get_2legged_token(self)->str:
        """
        Search for the first 2 legged token in the session and return it.

        Returns:
            str: The 2-legged token.

        Example:
            ```python
            # Get 2-legged token
            token = auth_client.get_2legged_token()
            if token:
                print("2-legged token retrieved successfully")
            else:
                print("No 2-legged token found")
            ```
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

        Returns:
            str: The 3-legged token.

        Example:
            ```python
            # Get 3-legged token
            token = auth_client.get_3legged_token()
            if token:
                print("3-legged token retrieved successfully")
            else:
                print("No 3-legged token found")
            ```
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
        Returns the 3-legged authorization URL for redirecting the user to the GET /authorize endpoint.

        Args:
            scopes(list):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.

        Returns:
            str: A 3-legged authorization URL crafted from the scopes requested.

        Notes:
            api_reference: https://aps.autodesk.com/en/docs/oauth/v2/reference/http/authorize-GET/   
            tutorial: https://aps.autodesk.com/en/docs/oauth/v2/tutorials/get-3-legged-token/

            The app_reference says that the URL should contain a parameter called "state" which is a random string
            generated by the client. This is used to prevent CSRF attacks. However, the tutorial does not mention this
            requirement and does not use it for basic(not PKCE) 3-legged auth.

        Example:
            ```python
            # Get authorization URL
            scopes = ["data:read", "data:write", "account:read"]
            auth_url = auth_client.get_authorization_url(scopes=scopes)
            print(f"Redirect user to: {auth_url}")
            
            # With PKCE
            auth_url = auth_client.get_authorization_url(
                scopes=scopes,
                code_challenge="your_code_challenge",
                code_challenge_method="S256"
            )
            ```
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
        
        Args:
            code(str):
                The authorization code from the redirect.  
            scopes(list):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.
            token_name:
                The name used to save and track this token in the session. 

        Returns:
            dict: The access token.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/

        Example:
            ```python
            # Exchange authorization code for token
            scopes = ["data:read", "data:write", "account:read"]
            token_data = auth_client.request_authcode_access_token(
                code=request.args.get("code"),
                scopes=scopes
            )
            print(f"Token expires in: {token_data['expires_in']} seconds")
            ```
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
        Exchange an authorization code and a code_verifier for an access token without sending the client_secret.
        
        Args:
            code(str):           
                The authorization code from the redirect.    
            code_verifier(str):  
                The code verifier used to generate the code challenge.
            scopes(list):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.
            token_name:
                The name used to save and track this token in the session.                 

        Returns:
            dict: The access token.

        https://aps.autodesk.com/en/docs/oauth/v2/tutorials/get-3-legged-token-pkce/get-3-legged-token-pkce/

        Example:
            ```python
            # Exchange code for token using PKCE
            scopes = ["data:read", "data:write"]
            token_data = auth_client.request_authcode_public_pkce_access_token(
                code=request.args.get("code"),
                code_verifier="your_code_verifier",
                scopes=scopes
            )
            print(f"Token expires in: {token_data['expires_in']} seconds")
            ```
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
        
        Args:
            code(required):           
                The authorization code from the redirect.    
            code_verifier(required):  
                The code verifier used to generate the code challenge.
            scopes(required):
                A list of allowed scopes. Scopes should match the
                scopes requested in the initial authorization request.
            token_name:
                The name used to save and track this token in the session. 

        Returns:
            dict: The access token.

        https://aps.autodesk.com/en/docs/oauth/v2/tutorials/get-3-legged-token-pkce/get-3-legged-token-pkce-private/

        Example:
            ```python
            # Exchange code for token using private PKCE
            scopes = ["data:read", "data:write"]
            token_data = auth_client.request_authcode_private_pkce_access_token(
                code=request.args.get("code"),
                code_verifier="your_code_verifier",
                scopes=scopes
            )
            print(f"Token expires in: {token_data['expires_in']} seconds")
            ```
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

        Args:
            scopes(list):
                A list of allowed scopes. Scopes should equivalent or a subset
                of the scopes used to request the access token.
            token_name (str): 
                The name used to save and track this token in the session.

        Returns:
            dict: The access token.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/

        Example:
            ```python
            # Refresh token with all original scopes
            token_data = auth_client.request_private_refresh_token()
            
            # Refresh token with subset of scopes
            scopes = ["data:read"]
            token_data = auth_client.request_private_refresh_token(scopes=scopes)
            print(f"Token refreshed, expires in: {token_data['expires_in']} seconds")
            ```
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
        Optionally pass in a subset of the refresh token's scopes.

        Args:
            scopes(list):
                A list of allowed scopes. Scopes should equivalent or a subset
                of the scopes used to request the access token.
            token_name (str): 
                The name used to save and track this token in the session.

        Returns:
            dict: The access token.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/

        Example:
            ```python
            # Refresh public token
            token_data = auth_client.request_public_refresh_token()
            
            # Refresh with subset of scopes
            scopes = ["data:read"]
            token_data = auth_client.request_public_refresh_token(scopes=scopes)
            print(f"Token refreshed, expires in: {token_data['expires_in']} seconds")
            ```
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

        Args:
            scopes(list):
                A list of allowed scopes. Scopes should equivalent or a subset
                of the scopes used to request the access token.
            token_name (str): 
                The name used to save and track this token in the session.

        Returns:
            dict: The access token.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST/

        Example:
            ```python
            # Get 2-legged token
            scopes = ["data:read", "data:write", "account:read"]
            token_data = auth_client.request_2legged_token(scopes=scopes)
            print(f"Token expires in: {token_data['expires_in']} seconds")
            
            # Get token with specific name
            token_data = auth_client.request_2legged_token(
                scopes=scopes,
                token_name="accapi_custom_token"
            )
            ```
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

        The local session is not cleared in this method. The client should call 
        clear_token_session() after redirecting the user to this URL.

        Returns:
            str: A URL GET endpoint which will clear their session and clear the tokens
            on the server.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/logout-GET/

        Example:
            ```python
            # Get logout URL
            logout_url = auth_client.get_logout_url()
            print(f"Redirect user to: {logout_url}")
            
            # After redirect, clear local session
            auth_client.clear_all_tokens()
            ```
        """        
        logout_url = self.logout_url
        if self.post_logout_url:
            logout_url += f"?post_logout_redirect_uri={self.logout_url}"
            
        return logout_url

    def clear_token_session(self, token_name):
        """
        Clears the session of a specific token.

        Args:
            token_name (str):
                The name of the token to clear.

        Example:
            ```python
            # Clear specific token
            auth_client.clear_token_session("accapi_3legged")
            print("Token cleared from session")
            ```
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

        Example:
            ```python
            # Clear all tokens
            auth_client.clear_all_tokens()
            print("All tokens cleared from session")
            ```
        """
        for token_name in self.token_names:
            self.clear_token_session(token_name)
        
    def revoke_public_token(self, token_name="accapi_3legged", token_type="access_token"):
        """
        Revoke a token using the POST revoke endpoint.
        
        Args:
            token_name (str):
                The name of the token to revoke.
            token_type (str):
                The type of token to revoke (access_token | refresh_token).

        Returns:
            dict: The response from the revoke endpoint.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/revoke-POST/

        Example:
            ```python
            # Revoke access token
            auth_client.revoke_public_token("accapi_3legged")
            
            # Revoke refresh token
            auth_client.revoke_public_token(
                token_name="accapi_3legged",
                token_type="refresh_token"
            )
            ```
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

        Args:
            token_name (str):
                The name of the token to revoke.
            token_type (str):
                The type of token to revoke (access_token | refresh_token).

        Returns:
            dict: The response from the revoke endpoint.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/revoke-POST/

        Example:
            ```python
            # Revoke access token
            auth_client.revoke_private_token("accapi_3legged")
            
            # Revoke refresh token
            auth_client.revoke_private_token(
                token_name="accapi_3legged",
                token_type="refresh_token"
            )
            ```
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
        
        Args:
            token_name (str):
                The name of the token to introspect.

        Returns:
            dict: The response from the introspect endpoint.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/introspect-POST/

        Example:
            ```python
            # Check token validity
            result = auth_client.introspect_public_token("accapi_3legged")
            if result.get("active"):
                print("Token is valid")
            else:
                print("Token is invalid")
            ```
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
        
        Args:
            token_name (str):
                The name of the token to introspect.

        Returns:
            dict: The response from the introspect endpoint.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/introspect-POST/

        Example:
            ```python
            # Check token validity
            result = auth_client.introspect_private_token("accapi_3legged")
            if result.get("active"):
                print("Token is valid")
            else:
                print("Token is invalid")
            ```
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
        
        Returns:
            dict: The OpenID Connect Discovery Document.

        https://aps.autodesk.com/en/docs/oauth/v2/reference/http/.well-known/openid-configuration-GET/

        Example:
            ```python
            # Get OpenID Connect specification
            spec = auth_client.get_oidc_spec()
            print(f"Supported scopes: {spec.get('scopes_supported')}")
            print(f"Token endpoint: {spec.get('token_endpoint')}")
            ```
        """
        response = requests.get(self.oidc_spec_url)
        if response.status_code == 200:
            return response.json()        
