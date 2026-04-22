from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, ChatSession, ChatMessage, EducationalResource
from .serializers import (
    RegisterSerializer, UserSerializer, UserProfileSerializer,
    ChatSessionSerializer, ChatMessageSerializer, EducationalResourceSerializer
)
from .ai_service import FinanceAdvisorAI

# ========== Authentication Views ==========

class RegisterView(generics.CreateAPIView):
    """User registration endpoint — returns JWT tokens on success"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the newly created user
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user details"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# ========== User Profile Views ==========

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== Chat Views ==========

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_sessions(request):
    """List all chat sessions or create a new one"""
    if request.method == 'GET':
        sessions = ChatSession.objects.filter(user=request.user)
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create new chat session
        title = request.data.get('title', 'New Conversation')
        session = ChatSession.objects.create(user=request.user, title=title)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def chat_session_detail(request, session_id):
    """Get or delete a specific chat session"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Chat session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, session_id):
    """Send a message and get AI response"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Chat session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user_message = request.data.get('message', '').strip()
    
    if not user_message:
        return Response(
            {'error': 'Message cannot be empty'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save user message
    user_msg = ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message
    )
    
    try:
        # Initialize AI service
        ai_service = FinanceAdvisorAI()
        
        # Get conversation history
        previous_messages = session.messages.all()[:10]  # Last 10 messages for context
        messages_for_ai = [
            {"role": msg.role, "content": msg.content}
            for msg in previous_messages
        ]
        
        # Get user profile for context
        try:
            user_profile = request.user.profile
        except:
            user_profile = None
        
        # Get AI response
        ai_response = ai_service.get_completion(messages_for_ai, user_profile)
        
        # Save AI response
        ai_msg = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response
        )
        
        # Update session title if this is the first message
        if session.messages.count() == 2:  # user + assistant
            try:
                title = ai_service.generate_conversation_title(user_message)
                session.title = title
                session.save()
            except:
                pass
        
        # Update session timestamp
        session.save()
        
        return Response({
            'user_message': ChatMessageSerializer(user_msg).data,
            'ai_message': ChatMessageSerializer(ai_msg).data,
            'session_title': session.title
        })
        
    except Exception as e:
        # If AI fails, still save user message but return error
        return Response(
            {'error': f'Failed to get AI response: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ========== Educational Resources Views ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def educational_resources(request):
    """Get all educational resources with optional filtering"""
    resources = EducationalResource.objects.all()
    
    # Filter by category if provided
    category = request.query_params.get('category')
    if category:
        resources = resources.filter(category=category)
    
    # Filter by difficulty level if provided
    level = request.query_params.get('level')
    if level:
        resources = resources.filter(difficulty_level=level)
    
    serializer = EducationalResourceSerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resource_detail(request, resource_id):
    """Get details of a specific educational resource"""
    try:
        resource = EducationalResource.objects.get(id=resource_id)
        serializer = EducationalResourceSerializer(resource)
        return Response(serializer.data)
    except EducationalResource.DoesNotExist:
        return Response(
            {'error': 'Resource not found'},
            status=status.HTTP_404_NOT_FOUND
        )

# ========== Dashboard/Stats Views ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get user dashboard statistics"""
    user = request.user
    
    stats = {
        'total_conversations': ChatSession.objects.filter(user=user).count(),
        'total_messages': ChatMessage.objects.filter(session__user=user).count(),
        'recent_sessions': ChatSessionSerializer(
            ChatSession.objects.filter(user=user)[:5],
            many=True
        ).data,
    }
    
    return Response(stats)
