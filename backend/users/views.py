from djoser.views import TokenCreateView
from rest_framework import status


class GetTokenView(TokenCreateView):
    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED

        return response
