from django.urls import path
from .views.authentication_views import UserSignupView, UserLoginView  
from .views.user_search_views import UserSearchView
from .views.friend_requests_views import FriendRequestCreateView, FriendRequestActionView,FriendListView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/send/', FriendRequestCreateView.as_view(), name='friend-request-send'),
    path('friend-request/action/<int:friend_request_id>/', FriendRequestActionView.as_view(), name='friend-request-action'),
    path('friend-request/list/', FriendListView.as_view(), name='friend-request-list'),

]
