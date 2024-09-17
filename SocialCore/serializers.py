from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

# Get the custom user model
User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user signup.

    This serializer validates the input data for creating a new user and 
    creates a user instance in the database using the custom user model.

    Attributes:
        model (User): The custom user model used for authentication.
        fields (list): Fields required for user signup, i.e., 'email' and 'password'.
        extra_kwargs (dict): Additional settings for the password field to make it write-only.

    Methods:
        create(validated_data):
            Creates and returns a new user instance using the provided validated data.

    """

    class Meta:
        model = User
        # fields = ['email', 'password']
        fields = ['id','email', 'password', 'first_name', 'last_name']  # Include first_name and last_name

        extra_kwargs = {'password': {'write_only': True}}  # won't return the password in responses

    def create(self, validated_data):
        """
        Creates a new user instance with the provided validated data.

        Args:
            validated_data (dict): Validated data containing 'email' and 'password'.

        Returns:
            User: A new user instance created with the given email and password.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),  # Optional: Provides the default empty string
            last_name=validated_data.get('last_name', '')  # Optional: Provides the default empty string
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for handling user login.

    This serializer validates the user's credentials and authenticates the user 
    based on the provided email and password.

    Attributes:
        email (EmailField): Email field for user login.
        password (CharField): Password field for user login, set as write-only.

    Methods:
        validate(data):
            Validates the input data, checks for the existence of a user and
            verifies the password.

    """

    email = serializers.EmailField()  # Email field for login
    password = serializers.CharField(write_only=True)  # Password field, write-only

    def validate(self, data):
        """
        Validates the provided login credentials.

        Args:
            data (dict): Contains the 'email' and 'password' provided by the user.

        Returns:
            User: The authenticated user object if credentials are valid.

        Raises:
            serializers.ValidationError: If the email or password is invalid.
        """
        # Look for user by email (case insensitive)
        user = User.objects.filter(email__iexact=data['email']).first()
        # Check if the password is correct
        if user and user.check_password(data['password']):
            return user
        raise serializers.ValidationError("Invalid email or password")


# for Friend requests

from .models import FriendRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        
class FriendRequestListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing friend requests.
    """
    from_user = UserSerializer()
    to_user = UserSerializer()
    
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']


class FriendRequestSerializer(serializers.ModelSerializer):
    
    """
    Serializer for handling friend request operations.

    Attributes:
        model (FriendRequest): The FriendRequest model.
        fields (list): Fields required for friend request operations.
    """

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
        read_only_fields = ['from_user', 'status', 'created_at']

    def validate(self, data):
        """
        Validates friend request data.

        Ensures the request is not being sent to self and does not exist already.

        Args:
            data (dict): Data to be validated.

        Returns:
            dict: Validated data.
        """
        if data['to_user'] == self.context['request'].user:
            raise serializers.ValidationError("Cannot send a friend request to yourself.")
        if FriendRequest.objects.filter(from_user=self.context['request'].user, to_user=data['to_user'], status='pending').exists():
            raise serializers.ValidationError("Friend request already sent to this user.")
        return data


class FriendRequestActionSerializer(serializers.ModelSerializer):
    """
    Serializer for accepting or rejecting friend requests.
    """
    status = serializers.ChoiceField(choices=['accepted', 'rejected'])

    class Meta:
        model = FriendRequest
        fields = ['status']
