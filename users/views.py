from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from .models import *
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets,status
from rest_framework.decorators import action
from .filters import *
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend

# API lấy token CSRF
class CSRFTokenView(APIView):
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrf_token': csrf_token})


# API đăng nhập
class ApiLoginView(APIView):
    # Không yêu cầu xác thực đối với API đăng nhập, vì api đăng nhập là điểm đầu tiên mà người dùng truy cập đến 
    # Người dùng chưa đăng nhập thì không có thông tin xác thực để gửi đến server
    permission_classes = [AllowAny] # xác định các lớp phân quyền , người dùng chưa đăng nhập nên loại bỏ phân quyền 
    @csrf_exempt
    def post(self, request):
        # Kiểm tra nếu người dùng đã đăng nhập
        if request.user.is_authenticated:
            return Response({"error": "Bạn đã đăng nhập"}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            role = user.role
            return Response({
                "message": "Đăng nhập thành công",
                "role": role,
                "access_token": access_token,  
                "refresh_token": refresh_token  
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Tên đăng nhập hoặc mật khẩu không chính xác"}, status=status.HTTP_401_UNAUTHORIZED)

# --------------------------------------------------------------------------------------------- 
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Không yêu cầu xác thực
    @csrf_exempt
    def post(self, request):
        # Validate AccountSerializer
        user_serializer = AccountSerializer(data=request.data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Lấy dữ liệu đã xác thực từ serializer
        user_data = user_serializer.validated_data
        role = user_data.get('role')
        VALID_ROLES = {'student', 'teacher', 'admin'}
        if role not in VALID_ROLES:
            return Response({"error": "Invalid role provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra sự tồn tại của user_id, email, phone_number
        existing_fields = {}
        if Account.objects.filter(user_id=user_data['user_id']).exists():
            existing_fields["already_exists_user_id"] = [user_data['user_id']]
        if user_data.get('usrename') and Account.objects.filter(username=user_data['username']).exists():
            existing_fields["already_exists_username"] = [user_data['username']]
        
        
        if existing_fields:
            return Response(existing_fields, status=status.HTTP_400_BAD_REQUEST)
        
        # Tạo Account
        user = Account.objects.create_user(
            user_id=user_data['user_id'],
            username=user_data['username'],
            role=role,
            password=user_data['user_id'], 
            is_active=True,
            is_staff=(False),
            is_superuser=(False),
            date_joined=timezone.now()
        )
        
        # Chọn serializer phù hợp theo role
        role_serializers = {
            'teacher': TeacherSerializer,
            'admin': AdminSerializer,
            'student': StudentSerializer
        }
        extra_fields = {key: request.data.get(key) for key in request.data if key not in ['user_id', 'role', 'email']}
        extra_fields['account'] = user.user_id  

        related_serializer = role_serializers[role](data=extra_fields)
        if related_serializer.is_valid():
            related_serializer.save()
        else:
            user.delete()  # Xóa user nếu role object tạo thất bại
            return Response(related_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": f"{role.capitalize()} registered successfully!",
                "user_id": user.user_id,
                "role": role,
            },
            status=status.HTTP_201_CREATED,
        )


class ChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # Kiểm tra dữ liệu đầu vào
        if not old_password or not new_password or not confirm_password:
            return Response({"error": "Vui lòng nhập đầy đủ thông tin."}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra mật khẩu cũ
        if not user.check_password(old_password):
            return Response({"error": "Mật khẩu cũ không chính xác."}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra mật khẩu mới và xác nhận mật khẩu phải giống nhau
        if new_password != confirm_password:
            return Response({"error": "Mật khẩu mới và xác nhận mật khẩu không khớp."}, status=status.HTTP_400_BAD_REQUEST)

        # Cập nhật mật khẩu mới
        user.password = make_password(new_password)
        user.save()

        return Response({"message": "Mật khẩu đã được cập nhật thành công."}, status=status.HTTP_200_OK)


class ResetPasswordByAdminView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.user.role != "admin":
            return Response({"error": "Bạn không có quyền thực hiện hành động này."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "Vui lòng cung cấp user_id."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(Account, user_id=user_id)

        # Reset password về mặc định là chính `user_id`
        default_password = user_id
        user.password = make_password(default_password)
        user.save()

        return Response({"message": f"Mật khẩu của {user_id} đã được đặt lại về mặc định."}, status=status.HTTP_200_OK)
    

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('account').all()
    serializer_class = TeacherSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    search_fields = ['full_name', 'account__user_id', 'phone_number', 'email']
    ordering_fields = '__all__'
    filter_backends = [DjangoFilterBackend]

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.select_related('account').all()
    serializer_class = AdminSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    search_fields = ['full_name', 'account__user_id', 'phone_number', 'email']
    ordering_fields = '__all__'
    filter_backends = [DjangoFilterBackend]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('account', 'room').all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    search_fields = ['full_name', 'account__user_id', 'room__id', 'phone_number', 'email']
    ordering_fields = '__all__'
    filter_backends = [DjangoFilterBackend]

# ordering_fields Cho phép người dùng sắp xếp dữ liệu theo bất kỳ trường nào trong model mà không cần khai báo từng trường.
# ✅ Linh hoạt hơn so với việc chỉ định một số trường cụ thể như ordering_fields = ['full_name', 'day_of_birth'].
# ✅ Giúp API dễ sử dụng hơn vì client có thể chọn trường để sắp xếp tùy ý.