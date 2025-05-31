from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, TagViewSet, CommentViewSet, LikeViewSet
from rest_framework_nested import routers

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)

# Rota aninhada: /posts/<post_id>/comments/
post_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
post_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(post_router.urls)),
]