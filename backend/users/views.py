from django.shortcuts import get_object_or_404
from djoser.views import TokenCreateView, UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.paginators import Pagination
from .models import User
from .serializers.extended import ExtendedUserSerializer


class GetTokenView(TokenCreateView):
    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED

        return response


class UserViewSet(DjoserUserViewSet):

    def get_queryset(self):
        if hasattr(self, 'do_get_subscriptions'):
            return self.request.user.subscribed_to.all()
        
        return super().get_queryset()

    @action(['get'], detail=False, serializer_class=ExtendedUserSerializer,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        self.do_get_subscriptions = True
        return self.list(request)

    @action(['post'], detail=True, serializer_class=ExtendedUserSerializer,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if request.user == author:
            return Response(
                dict(errors='Нельзя подписаться на самого себя.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.is_subscribed_to(author):
            return Response(
                dict(errors='Вы уже подписаны на этого автора.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.subscribe_to(author)
        serializer = self.get_serializer(author)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if not request.user.is_subscribed_to(author):
            return Response(
                dict(errors='Вы не подписаны на этого автора.'),
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.unsubscribe_from(author)
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

