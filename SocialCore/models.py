from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle user creation.

    This manager provides methods to create regular users and superusers,
    utilizing the email field as the unique identifier.

    Methods:
        create_user(email, password=None, **extra_fields):
            Creates and returns a regular user with the given email and password.
        
        create_superuser(email, password=None, **extra_fields):
            Creates and returns a superuser with the given email, password, 
            and admin privileges.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.

        This method normalizes the email address and creates a user instance 
        with the provided credentials. The user's password is automatically 
        hashed before saving.

        Args:
            email (str): The user's email address.
            password (str, optional): The user's password. Defaults to None.
            **extra_fields: Additional fields to be set on the user.

        Returns:
            CustomUser: A new user instance.

        Raises:
            ValueError: If the email is not provided.
        """
        if not email:
            raise ValueError("The Email field must be set")
        # Normalize the email (convert to lowercase)
        email = self.normalize_email(email)
        # Create user object
        user = self.model(email=email, **extra_fields)
        # Set the user's password (hashed automatically)
        user.set_password(password)
        # Save the user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.

        This method ensures that the superuser has the necessary admin privileges 
        by setting 'is_staff' and 'is_superuser' to True.

        Args:
            email (str): The superuser's email address.
            password (str, optional): The superuser's password. Defaults to None.
            **extra_fields: Additional fields to be set on the superuser.

        Returns:
            CustomUser: A new superuser instance.
        """
        # Ensure the user has admin privileges
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Call create_user to handle the creation
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model to use email as the unique identifier.

    This model extends Django's AbstractBaseUser and PermissionsMixin to 
    provide a custom user model that uses email instead of a username 
    for authentication.

    Attributes:
        email (EmailField): The user's email address, used as the unique identifier.
        first_name (CharField): Optional field for the user's first name.
        last_name (CharField): Optional field for the user's last name.
        is_active (BooleanField): Indicates whether the user is active.
        is_staff (BooleanField): Indicates whether the user has staff privileges.
        objects (CustomUserManager): The custom user manager for handling user creation.

    Methods:
        __str__():
            Returns a string representation of the user, which is their email.
    """

    email = models.EmailField(unique=True, db_index=True)  # Email field, indexed and unique
    first_name = models.CharField(max_length=30, blank=True)  # Optional first name
    last_name = models.CharField(max_length=30, blank=True)   # Optional last name
    is_active = models.BooleanField(default=True)  # Active status
    is_staff = models.BooleanField(default=False)  # Staff status (for admin panel access)

    # Use CustomUserManager to handle object creation
    objects = CustomUserManager()

    # Specify email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No other required fields

    def __str__(self):
        """
        Return a string representation of the user.

        Returns:
            str: The user's email address.
        """
        return self.email

# for friend requests
    
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class FriendRequest(models.Model):
    """
    Model to represent a friend request between two users.
    
    Attributes:
        from_user (ForeignKey): The user who sent the friend request.
        to_user (ForeignKey): The user who received the friend request.
        created_at (DateTimeField): The date and time when the request was created.
        status (CharField): The status of the request, either 'pending', 'accepted', or 'rejected'.
    """
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"Friend request from {self.from_user.email} to {self.to_user.email}"

    @classmethod
    def can_send_request(cls, from_user):
        """
        Checks if a user can send more friend requests.
        
        Args:
            from_user (User): The user trying to send a friend request.
        
        Returns:
            bool: True if the user can send more requests, False otherwise.
        """
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        sent_requests_count = cls.objects.filter(from_user=from_user, created_at__gte=one_minute_ago).count()
        return sent_requests_count < 3
