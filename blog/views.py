from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Tag, Comment, Like, Favorite
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission
from .serializers import (
    PostSerializer, TagSerializer, CommentSerializer, LikeSerializer, RegisterSerializer, FavoriteSerializer, UserSerializer, UserUpdateSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related('author').prefetch_related('tags', 'comments', 'likes')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'tags']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Leitura para todos, edição só para o autor
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('author', 'post') 
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        queryset = Comment.objects.select_related('author', 'post')
        post_id = self.kwargs.get('post_pk')  # ← do roteador nested
        if post_id:
            queryset = queryset.filter(post__id=post_id)
        return queryset

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        if post_id:
            serializer.save(author=self.request.user, post_id=post_id)
        else:
            serializer.save(author=self.request.user)

class IsLikeOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permite leitura (GET, HEAD, OPTIONS) para qualquer um
        if request.method in SAFE_METHODS:
            return True
        # Permite deletar somente se o like for do usuário
        return obj.user == request.user

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().select_related('user', 'post')
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, IsLikeOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Mostra apenas os favoritos do usuário logado
        return Favorite.objects.filter(user=self.request.user).select_related('post')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AuthorPostsView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        author_id = self.kwargs['user_id']
        try:
            author = User.objects.get(pk=author_id)
        except User.DoesNotExist:
            raise NotFound("Usuário não encontrado.")
        return Post.objects.filter(author=author).select_related('author').prefetch_related('tags', 'comments', 'likes')

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Perfil atualizado com sucesso.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Perfil atualizado com sucesso.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)