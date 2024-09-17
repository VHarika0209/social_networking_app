from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from ..serializers import UserSignupSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class UserSearchPagination(PageNumberPagination):
    page_size = 10  # Set the number of records per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserSearchView(generics.ListAPIView):
    """
    Searches for users based on the provided search keyword.
    """
    serializer_class = UserSignupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserSearchPagination  # Use pagination here
    
    def get(self, request):
        keyword = request.query_params.get("keyword", '').strip()
        if keyword:
            queryset = User.objects.filter(
                Q(email__icontains=keyword) | 
                Q(first_name__icontains=keyword) | 
                Q(last_name__icontains=keyword)
            )  # Search by email, first name, or last name
        else:
            queryset = User.objects.none()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
