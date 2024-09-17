from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Q

from ..models import FriendRequest
from ..serializers import UserSerializer,FriendRequestSerializer, FriendRequestActionSerializer,FriendRequestListSerializer


class FriendRequestCreateView(generics.CreateAPIView):
    """
    View to create a new friend request.

    Allows authenticated users to send friend requests to other users.
    Enforces a limit of sending no more than 3 friend requests within a minute.
    """
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Handles the creation of a friend request.

        Checks if the user can send more requests and saves the request.

        Args:
            serializer (Serializer): Serializer instance with validated data.

        Raises:
            ValidationError: If user exceeds the limit of friend requests.
        """
        from_user = self.request.user
        if not FriendRequest.can_send_request(from_user):
            raise serializers.ValidationError("You can only send up to 3 friend requests per minute.")
        serializer.save(from_user=from_user)


class FriendRequestActionView(APIView):
    """
    View to accept or reject a friend request.

    Expects a PATCH request with a 'status' parameter (either 'accepted' or 'rejected')
    in the form-data.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestActionSerializer

    def patch(self, request, friend_request_id):
        """
        Handle friend request action (accept/reject) with PATCH request.

        Args:
            request (Request): The HTTP request object.
            friend_request_id (int): The ID of the friend request being updated.

        Returns:
            Response: A response indicating success or failure of the operation.
        """
        # Retrieve the friend request by ID
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id, status='pending')
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found or already acted upon.'}, status=status.HTTP_404_NOT_FOUND)

        # Check that the request user is the 'to_user'
        if friend_request.to_user != request.user:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        # Validate and get the status from the request body using the serializer
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action_status = serializer.validated_data['status']

        # Check if the friend request is already in the desired state
        if friend_request.status == action_status:
            return Response({'message': f'Friend request is already {action_status}.'}, status=status.HTTP_200_OK)

        # Update the friend request status
        friend_request.status = action_status
        friend_request.save()

        return Response({'message': f'Friend request {action_status} successfully.'}, status=status.HTTP_200_OK)


class FriendListView(generics.ListAPIView):
    """
    View to list all friends or pending friend requests of the authenticated user.

    Lists users who have accepted friend requests or pending requests based on the status query parameter.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Selects the appropriate serializer based on the status parameter.
        
        Returns:
            Serializer: `UserSerializer` for friends, `FriendRequestListSerializer` for pending requests.
        """
        status_param = self.request.query_params.get('status', 'accepted')
        if status_param == 'pending':
            return FriendRequestListSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Retrieves the queryset of friends or pending friend requests for the authenticated user.
        
        Returns:
            QuerySet: Filtered queryset based on the status query parameter.
        """
        user = self.request.user
        status_param = self.request.query_params.get('status', 'accepted')

        if status_param == 'accepted':
            accepted_requests = FriendRequest.objects.filter(
                Q(from_user=user, status='accepted') | Q(to_user=user, status='accepted')
            )
            friends = set()
            for request in accepted_requests:
                if request.from_user == user:
                    friends.add(request.to_user)
                else:
                    friends.add(request.from_user)
            return friends  # Used set here to avoid duplicates

        elif status_param == 'pending':
            pending_requests = FriendRequest.objects.filter(to_user=user, status='pending')
            return pending_requests
        
        else:
            return FriendRequest.objects.none()  # or raises an exception if status is invalid

    def list(self, request, *args, **kwargs):
        """
        Handles the GET request to list friends or pending friend requests.

        Returns:
            Response: Serialized data or custom message if no data is found.
        """
        queryset = self.get_queryset()
        if not queryset:
            status_param = self.request.query_params.get('status', 'accepted')
            if status_param == 'accepted':
                return Response({"message": "No friends found."}, status=status.HTTP_404_NOT_FOUND)
            elif status_param == 'pending':
                return Response({"message": "No pending requests found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "Invalid status parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
