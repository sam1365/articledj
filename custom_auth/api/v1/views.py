from rest_framework import status
from rest_framework.permissions import (AllowAny,
                                        )
from rest_framework.decorators import (api_view,
                                       permission_classes,
                                       )
from rest_framework.response import (Response,
                                     )
from rest_framework_simplejwt.tokens import (RefreshToken,
                                             )

from custom_auth.services.github_service.github_oauth import (GitHubOAuthService,
                                                              )


@api_view(['POST'])
@permission_classes([AllowAny])
def github_oauth_callback(request):
    """
    Handle GitHub callback and get JWT tokens
    """

    code = request.data['code']
    if not code:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'error': 'Authorization code is required'})

    try:
        access_token = GitHubOAuthService.get_access_token(code)
        github_user_data = GitHubOAuthService.get_user_information(access_token)
        user, created = GitHubOAuthService.get_or_create_user(github_user_data, access_token)
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data=data)

    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        )


@api_view(['POST'])
def logout(request):
    """
    Handle logout user and blacklisting refresh token
    """

    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'error': 'Invalid token'},
                        )
