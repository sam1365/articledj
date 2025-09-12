import uuid

from django.conf import settings
from django.db import IntegrityError

from rest_framework import status
from rest_framework.exceptions import APIException
import requests

from accounts.models import (User,
                             )


class GitHubOAuthError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'GitHub OAuth Authentication Failed.'


class GitHubOAuthService:
    """
    GitHub OAuth Service

    Methods:
        get_access_token(code): Get access token
            by using GitHub OAuth authorization code.
        get_user_information(access_token): Get user information.
        get_user_emails(access_token): Get user emails.
        _extract_name_parts(full_name): Extract first and names from full name.
        _get_primary_email(access_token): Get primary or verified email.
        get_or_create_user(github_user_data, access_token): Get or
            create user with GitHub user data.
        authenticate_user(code): Authenticate user with GitHub.
    """

    @staticmethod
    def get_access_token(code):
        """
        Get access token by using GitHub OAuth authorization code.

        Args:
            code: Authorization code from GitHub OAuth redirect
        Returns:
            GitHub access token
        """

        payload = {
            'client_id': settings.SOCIAL_AUTH_GITHUB_KEY,
            'client_secret': settings.SOCIAL_AUTH_GITHUB_SECRET,
            'code': code,
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(
                'https://github.com/login/oauth/access_token',
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if 'access_token' not in data:
                raise GitHubOAuthError('Failed to obtain access token from GitHub')

            return data['access_token']

        except requests.RequestException as e:
            raise GitHubOAuthError(f'GitHub API request failed: {str(e)}')

    @staticmethod
    def get_user_information(access_token):
        """
        Get user information from GitHub API using access token

        Args:
            access_token: GitHub access token
        Returns:
            Dictionary of GitHub user data
        """

        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json',
        }

        try:
            response = requests.get(
                'https://api.github.com/user',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise GitHubOAuthError(f'Failed to fetch user info from GitHub: {str(e)}')

    @staticmethod
    def get_user_emails(access_token):
        """
        Get user emails from GitHub API

        Args:
            access_token: GitHub access token
        Returns:
            List of email objects
        """

        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json',
        }

        try:
            response = requests.get(
                'https://api.github.com/user/emails',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            return []

    @staticmethod
    def _extract_name_parts(full_name):
        """
        Split full name into first and last name

        Args:
            full_name(str): Full name string
        Returns:
            Tuple of (first_name, last_name)
        """

        if not full_name:
            return '', ''

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        return first_name, last_name

    @staticmethod
    def _get_primary_email(emails_data):
        """
        Extract primary or verified email from emails data

        Args:
            emails_data(list): List of email objects from GitHub
        Returns:
            Primary email address or None
        """

        for email_data in emails_data:
            if email_data.get('primary') and email_data.get('verified'):
                return email_data['email']

        for email_data in emails_data:
            if email_data.get('verified'):
                return email_data['email']

        return None

    @staticmethod
    def get_or_create_user(github_user_data, access_token):
        """
        Get or create user based on GitHub user data

        Args:
            github_user_data: User data from GitHub API
            access_token: GitHub access token for email lookup
        Returns:
            Tuple of (user, created)
        """

        github_id = str(github_user_data['id'])
        email = github_user_data.get('email')

        if not email:
            emails_data = GitHubOAuthService.get_user_emails(access_token)
            email = GitHubOAuthService._get_primary_email(emails_data)

        if not email:
            email = f"{github_user_data.get('login', 'github')}-{github_id}@users.noreply.github.com"

        first_name, last_name = GitHubOAuthService._extract_name_parts(
            github_user_data.get('name')
        )

        user_data = {
            'github_id': github_id,
            'email': email,
            'github_username': github_user_data.get('login', ''),
            'first_name': first_name,
            'last_name': last_name,
            'github_profile_url': github_user_data.get('html_url', ''),
        }

        try:
            user, created = User.objects.update_or_create(
                github_id=github_id,
                defaults=user_data
            )

            return user, created

        except IntegrityError as e:
            # Handle unique constraint violations (e.g., duplicate email)
            if 'email' in str(e).lower():
                try:
                    user = User.objects.get(email=email)
                    user.github_id = github_id
                    user.github_username = user_data['github_username']
                    user.github_profile_url = user_data['github_profile_url']
                    user.save()
                    return user, False
                except User.DoesNotExist:
                    # Generate unique email if conflict exists
                    user_data['email'] = f"github-{github_id}@users.noreply.github.com"
                    user, created = User.objects.update_or_create(
                        github_id=github_id,
                        defaults=user_data
                    )
                    return user, created
            raise GitHubOAuthError(f'User creation failed: {str(e)}')

    @staticmethod
    def authenticate_user(code):
        """
        GitHub OAuth authentication
        """
        
        try:
            # Exchange code for access token
            access_token = GitHubOAuthService.get_access_token(code)

            # Get user info from GitHub
            github_user_data = GitHubOAuthService.get_user_information(access_token)

            # Get or create user in database
            user, created = GitHubOAuthService.get_or_create_user(
                github_user_data,
                access_token
            )

            return user, created, access_token

        except Exception as e:
            if isinstance(e, GitHubOAuthError):
                raise e
            raise GitHubOAuthError(f'Authentication failed: {str(e)}')
