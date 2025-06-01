from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, TagViewSet, CommentViewSet, LikeViewSet, RegisterView, FavoriteViewSet, AuthorPostsView, ProfileUpdateView
from rest_framework_nested import routers

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorite')


# Rota aninhada: /posts/<post_id>/comments/
post_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
post_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(post_router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('users/<int:user_id>/posts/', AuthorPostsView.as_view(), name='author-posts'),
    path('profile/', ProfileUpdateView.as_view(), name='profile-update'),
]