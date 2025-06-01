from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Tag, Comment, Like, Favorite

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username já existe.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, source='tags'
    )
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author',
            'tags', 'tag_ids', 'created_at', 'updated_at',
            'comments', 'likes_count', 'favorites_count', 'image'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'comments', 'likes_count', 'favorites_count']

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_favorites_count(self, obj):
        return obj.favorited_by.count()
    
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Atualiza os outros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Atualiza a senha com hash
        if password:
            instance.set_password(password)

        instance.save()
        return instance