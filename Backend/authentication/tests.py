from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, ChatSession, ChatMessage, EducationalResource
from .serializers import RegisterSerializer, UserSerializer, ChatSessionSerializer


# ========== Model Tests ==========

class UserProfileModelTest(TestCase):
    """Tests for the UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )

    def test_profile_created_with_user(self):
        """Profile should NOT auto-create (only created in serializer/view)"""
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())

    def test_create_profile_manually(self):
        """Manually creating a profile should work"""
        profile = UserProfile.objects.create(
            user=self.user,
            finance_goal='Save for retirement',
            risk_tolerance='moderate'
        )
        self.assertEqual(str(profile), "testuser's Profile")
        self.assertEqual(profile.risk_tolerance, 'moderate')
        self.assertEqual(profile.finance_goal, 'Save for retirement')

    def test_profile_default_risk_tolerance(self):
        """Risk tolerance should default to moderate"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.risk_tolerance, 'moderate')

    def test_profile_risk_tolerance_choices(self):
        """All valid risk tolerance values should be accepted"""
        for choice in ['conservative', 'moderate', 'aggressive']:
            profile, _ = UserProfile.objects.update_or_create(
                user=self.user,
                defaults={'risk_tolerance': choice}
            )
            self.assertEqual(profile.risk_tolerance, choice)


class ChatSessionModelTest(TestCase):
    """Tests for the ChatSession model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='chatuser',
            email='chat@example.com',
            password='TestPass123!'
        )

    def test_create_session_default_title(self):
        """Session should have 'New Conversation' as default title"""
        session = ChatSession.objects.create(user=self.user)
        self.assertEqual(session.title, 'New Conversation')

    def test_create_session_custom_title(self):
        """Session should accept a custom title"""
        session = ChatSession.objects.create(user=self.user, title='My Financial Plan')
        self.assertEqual(session.title, 'My Financial Plan')

    def test_session_str_representation(self):
        """String representation should include username and title"""
        session = ChatSession.objects.create(user=self.user, title='Tax Questions')
        self.assertEqual(str(session), 'chatuser - Tax Questions')

    def test_sessions_ordered_by_updated_at(self):
        """Sessions should be ordered by most recently updated first"""
        session1 = ChatSession.objects.create(user=self.user, title='First')
        session2 = ChatSession.objects.create(user=self.user, title='Second')
        sessions = list(ChatSession.objects.filter(user=self.user))
        self.assertEqual(sessions[0].title, 'Second')

    def test_cascade_delete_with_user(self):
        """Deleting user should cascade delete sessions"""
        ChatSession.objects.create(user=self.user, title='Session 1')
        self.user.delete()
        self.assertEqual(ChatSession.objects.count(), 0)


class ChatMessageModelTest(TestCase):
    """Tests for the ChatMessage model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='msguser',
            password='TestPass123!'
        )
        self.session = ChatSession.objects.create(user=self.user)

    def test_create_user_message(self):
        msg = ChatMessage.objects.create(
            session=self.session, role='user', content='Hello'
        )
        self.assertEqual(msg.role, 'user')
        self.assertEqual(msg.content, 'Hello')

    def test_create_assistant_message(self):
        msg = ChatMessage.objects.create(
            session=self.session, role='assistant', content='Hi there!'
        )
        self.assertEqual(msg.role, 'assistant')

    def test_message_str_truncates(self):
        """String representation should truncate content to 50 chars"""
        long_content = 'A' * 100
        msg = ChatMessage.objects.create(
            session=self.session, role='user', content=long_content
        )
        self.assertEqual(str(msg), f"user: {'A' * 50}")

    def test_messages_ordered_by_timestamp(self):
        """Messages should be ordered by timestamp ascending"""
        msg1 = ChatMessage.objects.create(
            session=self.session, role='user', content='First'
        )
        msg2 = ChatMessage.objects.create(
            session=self.session, role='assistant', content='Second'
        )
        messages = list(self.session.messages.all())
        self.assertEqual(messages[0].content, 'First')
        self.assertEqual(messages[1].content, 'Second')

    def test_cascade_delete_with_session(self):
        """Deleting session should cascade delete messages"""
        ChatMessage.objects.create(
            session=self.session, role='user', content='test'
        )
        self.session.delete()
        self.assertEqual(ChatMessage.objects.count(), 0)


class EducationalResourceModelTest(TestCase):
    """Tests for the EducationalResource model"""

    def test_create_resource(self):
        resource = EducationalResource.objects.create(
            title='Intro to Investing',
            category='investing',
            content='Learn the basics of investing...',
            difficulty_level='beginner'
        )
        self.assertEqual(str(resource), 'Intro to Investing')
        self.assertEqual(resource.category, 'investing')
        self.assertEqual(resource.difficulty_level, 'beginner')

    def test_resources_ordered_by_created_at_desc(self):
        """Resources should be ordered newest first"""
        r1 = EducationalResource.objects.create(
            title='First', category='budgeting',
            content='Content 1', difficulty_level='beginner'
        )
        r2 = EducationalResource.objects.create(
            title='Second', category='savings',
            content='Content 2', difficulty_level='intermediate'
        )
        resources = list(EducationalResource.objects.all())
        self.assertEqual(resources[0].title, 'Second')


# ========== Serializer Tests ==========

class RegisterSerializerTest(TestCase):
    """Tests for the RegisterSerializer"""

    def test_valid_registration_data(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_password_mismatch(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass456!',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_missing_required_fields(self):
        data = {'username': 'newuser', 'password': 'StrongPass123!', 'password2': 'StrongPass123!'}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)
        self.assertIn('last_name', serializer.errors)
        self.assertIn('email', serializer.errors)

    def test_weak_password_rejected(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123',
            'password2': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_user_and_profile(self):
        """Saving serializer should create both User and UserProfile"""
        data = {
            'username': 'created_user',
            'email': 'created@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Created',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, 'created_user')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_duplicate_username_rejected(self):
        User.objects.create_user(username='taken', password='TestPass123!')
        data = {
            'username': 'taken',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())


# ========== API Endpoint Tests ==========

class RegisterAPITest(TestCase):
    """Tests for the registration API endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'

    def test_register_success(self):
        data = {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'API',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'apiuser')

    def test_register_missing_fields(self):
        data = {'username': 'incomplete'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        data = {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'StrongPass123!',
            'password2': 'WrongPass456!',
            'first_name': 'API',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(TestCase):
    """Tests for the login API endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.user = User.objects.create_user(
            username='loginuser',
            password='TestPass123!',
            email='login@example.com'
        )

    def test_login_success(self):
        data = {'username': 'loginuser', 'password': 'TestPass123!'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        data = {'username': 'loginuser', 'password': 'WrongPassword!'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_missing_fields(self):
        data = {'username': 'loginuser'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_request(self):
        response = self.client.post(self.login_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        data = {'username': 'ghost', 'password': 'TestPass123!'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CurrentUserAPITest(TestCase):
    """Tests for the get_current_user endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/me/'
        self.user = User.objects.create_user(
            username='meuser', password='TestPass123!',
            email='me@example.com', first_name='Me', last_name='User'
        )

    def test_get_current_user_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'meuser')
        self.assertEqual(response.data['email'], 'me@example.com')

    def test_get_current_user_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAPITest(TestCase):
    """Tests for the user profile endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/profile/'
        self.user = User.objects.create_user(
            username='profileuser', password='TestPass123!',
            email='profile@example.com', first_name='Profile', last_name='User'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile_auto_creates(self):
        """GET profile should auto-create one if it doesn't exist"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['risk_tolerance'], 'moderate')
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_update_profile(self):
        """PUT should update profile fields"""
        UserProfile.objects.create(user=self.user)
        data = {'finance_goal': 'Buy a house', 'risk_tolerance': 'aggressive'}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['finance_goal'], 'Buy a house')
        self.assertEqual(response.data['risk_tolerance'], 'aggressive')

    def test_profile_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChatSessionAPITest(TestCase):
    """Tests for chat session endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.sessions_url = '/api/chat/sessions/'
        self.user = User.objects.create_user(
            username='chatapi', password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_sessions_empty(self):
        response = self.client.get(self.sessions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_session_default_title(self):
        response = self.client.post(self.sessions_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Conversation')

    def test_create_session_custom_title(self):
        response = self.client.post(
            self.sessions_url, {'title': 'Investment Help'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Investment Help')

    def test_list_sessions_returns_own_only(self):
        """User should only see their own sessions"""
        ChatSession.objects.create(user=self.user, title='My Session')
        other_user = User.objects.create_user(username='other', password='TestPass123!')
        ChatSession.objects.create(user=other_user, title='Other Session')

        response = self.client.get(self.sessions_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My Session')

    def test_get_session_detail(self):
        session = ChatSession.objects.create(user=self.user, title='Detail Test')
        url = f'/api/chat/sessions/{session.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Detail Test')

    def test_get_other_users_session_returns_404(self):
        other_user = User.objects.create_user(username='other2', password='TestPass123!')
        session = ChatSession.objects.create(user=other_user, title='Secret')
        url = f'/api/chat/sessions/{session.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_session(self):
        session = ChatSession.objects.create(user=self.user, title='Delete Me')
        url = f'/api/chat/sessions/{session.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChatSession.objects.filter(id=session.id).exists())

    def test_sessions_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.sessions_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EducationalResourceAPITest(TestCase):
    """Tests for educational resource endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/education/resources/'
        self.user = User.objects.create_user(
            username='eduuser', password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

        self.resource1 = EducationalResource.objects.create(
            title='Budgeting 101', category='budgeting',
            content='Learn budgeting basics', difficulty_level='beginner'
        )
        self.resource2 = EducationalResource.objects.create(
            title='Advanced Investing', category='investing',
            content='Learn advanced strategies', difficulty_level='advanced'
        )

    def test_list_all_resources(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_category(self):
        response = self.client.get(self.url, {'category': 'investing'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Advanced Investing')

    def test_filter_by_level(self):
        response = self.client.get(self.url, {'level': 'beginner'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Budgeting 101')

    def test_resource_detail(self):
        url = f'/api/education/resources/{self.resource1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Budgeting 101')

    def test_resource_detail_not_found(self):
        response = self.client.get('/api/education/resources/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_resources_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardStatsAPITest(TestCase):
    """Tests for the dashboard stats endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/dashboard/stats/'
        self.user = User.objects.create_user(
            username='dashuser', password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_empty_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_conversations'], 0)
        self.assertEqual(response.data['total_messages'], 0)
        self.assertEqual(len(response.data['recent_sessions']), 0)

    def test_dashboard_with_data(self):
        session = ChatSession.objects.create(user=self.user, title='Test Chat')
        ChatMessage.objects.create(session=session, role='user', content='Hello')
        ChatMessage.objects.create(session=session, role='assistant', content='Hi')

        response = self.client.get(self.url)
        self.assertEqual(response.data['total_conversations'], 1)
        self.assertEqual(response.data['total_messages'], 2)
        self.assertEqual(len(response.data['recent_sessions']), 1)

    def test_dashboard_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
