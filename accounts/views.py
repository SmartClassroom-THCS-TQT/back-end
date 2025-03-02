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

# API lấy token CSRF
class CSRFTokenView(APIView):
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrf_token': csrf_token})


# API đăng nhập
class ApiLoginView(APIView):
    # Không yêu cầu xác thực đối với API đăng nhập, vì api đăng nhập là điểm đầu tiên mà người dùng truy cập đến 
    # Người dùng chưa đăng nhập thì không có thông tin xác thực để gửi đến server
    authentication_classes = [] #quy định các lớp xác thực được sử dụng để xác thực người dùng
    permission_classes = [] # xác định các lớp phân quyền , người dùng chưa đăng nhập nên loại bỏ phân quyền 
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
            return Response({
                "message": "Đăng nhập thành công",
                "access_token": access_token,  
                "refresh_token": refresh_token  
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Tên đăng nhập hoặc mật khẩu không chính xác"}, status=status.HTTP_401_UNAUTHORIZED)

# --------------------------------------------------------------------------------------------- 
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request):
        # Validate CustomUserSerializer
        user_serializer = CustomUserSerializer(data=request.data)
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
        if CustomUser.objects.filter(user_id=user_data['user_id']).exists():
            existing_fields["already_exists_user_id"] = [user_data['user_id']]
        if user_data.get('email') and CustomUser.objects.filter(email=user_data['email']).exists():
            existing_fields["already_exists_email"] = [user_data['email']]
        if user_data.get('phone_number') and CustomUser.objects.filter(phone_number=user_data['phone_number']).exists():
            existing_fields["already_exists_phone_number"] = [user_data['phone_number']]
        
        if existing_fields:
            return Response(existing_fields, status=status.HTTP_400_BAD_REQUEST)
        
        # Tạo CustomUser
        user = CustomUser.objects.create_user(
            user_id=user_data['user_id'],
            role=role,
            password=user_data['user_id'], 
            email=user_data.get('email'),
            phone_number=user_data.get('phone_number'),
            sex=user_data.get('sex'),
            full_name=user_data.get('full_name'),
            day_of_birth=user_data.get('day_of_birth'),
            nation=user_data.get('nation'),
            active_status=user_data.get('active_status'),
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
        extra_fields = {key: request.data.get(key) for key in request.data if key not in ['user_id', 'role', 'email', 'phone_number']}
        extra_fields['user'] = user.user_id  # Truyền ID thay vì object

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



    @action(detail=False, methods=['get'], url_path='detail', permission_classes=[IsAuthenticated])
    def my_detail(self, request):
        """
        API: `/api/accounts/users/detail/`
        → Trả về thông tin của chính người dùng đang đăng nhập (bao gồm tất cả thông tin role).
        """
        user = request.user
        
        # Xử lý dựa trên role của user
        role = user.role
        if role == 'teacher':
            teacher = get_object_or_404(Teacher, user=user)
            teacher_data = TeacherSerializer(teacher).data
            return Response({
                **CustomUserSerializer(user).data,
                'teacher': teacher_data
            })

        elif role == 'admin':
            admin = get_object_or_404(Admin, user=user)
            admin_data = AdminSerializer(admin).data
            return Response({
                **CustomUserSerializer(user).data,
                'admin': admin_data
            })

        elif role == 'student':
            student = get_object_or_404(Student, user=user)
            student_data = StudentSerializer(student).data
            return Response({
                **CustomUserSerializer(user).data,
                'student': student_data
            })
        
        return Response({
            'error': 'Role không hợp lệ'
        }, status=400)

    @action(detail=False, methods=['get'], url_path='detail/(?P<user_id>[^/.]+)', permission_classes=[IsAuthenticated])
    def user_detail(self, request, user_id):
        """
        API: `/api/accounts/users/detail/<user_id>/`
        → Chỉ Admin mới có quyền xem thông tin của người khác (bao gồm thông tin chi tiết của role).
        """
        if request.user.role != 'admin':
            return Response({"error": "Bạn không có quyền xem thông tin này."}, status=403)

        user = get_object_or_404(CustomUser, user_id=user_id)

        # Lấy thông tin chi tiết từ bảng phù hợp dựa trên role
        role = user.role
        if role == 'teacher':
            teacher = get_object_or_404(Teacher, user=user)
            teacher_data = TeacherSerializer(teacher).data
            return Response({
                **CustomUserSerializer(user).data,
                'teacher': teacher_data
            })

        elif role == 'admin':
            admin = get_object_or_404(Admin, user=user)
            admin_data = AdminSerializer(admin).data
            return Response({
                **CustomUserSerializer(user).data,
                'admin': admin_data
            })

        elif role == 'student':
            student = get_object_or_404(Student, user=user)
            student_data = StudentSerializer(student).data
            return Response({
                **CustomUserSerializer(user).data,
                'student': student_data
            })
        
        return Response({
            'error': 'Role không hợp lệ'
        }, status=400)

    @action(detail=False, methods=['put'], url_path='update', permission_classes=[IsAuthenticated])
    def update_self(self, request):
        """
        API: `/api/accounts/users/update/` → Người dùng tự cập nhật thông tin của chính mình.
        """
        return self._update_user(request, request.user, is_admin=False)

    @action(detail=True, methods=['put'], url_path='update', permission_classes=[IsAuthenticated])
    def update_other(self, request, pk=None):
        """
        API: `/api/accounts/users/<user_id>/update/` → Admin cập nhật thông tin của user khác.
        """
        if request.user.role != "admin":
            return Response({"error": "Bạn không có quyền chỉnh sửa người khác."}, status=403)

        user = get_object_or_404(CustomUser, user_id=pk)
        return self._update_user(request, user, is_admin=True)

    def _update_user(self, request, user, is_admin):
        """
        Xử lý cập nhật thông tin user (dùng chung cho self-update và admin-update).
        """
        update_data = request.data.copy()

        # Cấm thay đổi user_id và role
        update_data.pop("user_id", None)
        update_data.pop("role", None)

        # Cập nhật CustomUser
        user_serializer = CustomUserSerializer(user, data=update_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

            # Cập nhật dữ liệu bổ sung của role (Student, Teacher, Admin)
            if hasattr(user, user.role):
                role_instance = getattr(user, user.role)
                role_serializer_class = {
                    'student': StudentSerializer,
                    'teacher': TeacherSerializer,
                    'admin': AdminSerializer
                }.get(user.role)

                # Cập nhật dữ liệu riêng của Student, Teacher, Admin
                role_fields = [f.name for f in role_instance._meta.fields]
                extra_data = {k: v for k, v in update_data.items() if k in role_fields}

                if extra_data:
                    role_serializer = role_serializer_class(role_instance, data=extra_data, partial=True)
                    if role_serializer.is_valid():
                        role_serializer.save()

            return Response({"message": "Cập nhật thành công", "user": user_serializer.data})

        return Response(user_serializer.errors, status=400)
    # def _get_user_detail(self, user):
    #     """
    #     Lấy thông tin đầy đủ của user, bao gồm cả bảng Student, Teacher hoặc Admin.
    #     """
    #     user_serializer = CustomUserSerializer(user)
    #     user_data = user_serializer.data

    #     # Lấy thông tin từ bảng Student, Teacher hoặc Admin
    #     if hasattr(user, user.role):
    #         role_instance = getattr(user, user.role)
    #         role_serializer_class = {
    #             'student': StudentSerializer,
    #             'teacher': TeacherSerializer,
    #             'admin': AdminSerializer
    #         }.get(user.role)

    #         role_serializer = role_serializer_class(role_instance)
    #         user_data.update(role_serializer.data)

    #     return Response(user_data)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "admin":
            return Response({"error": "Bạn không có quyền thực hiện hành động này."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "Vui lòng cung cấp user_id."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, user_id=user_id)

        # Reset password về mặc định là chính `user_id`
        default_password = user_id
        user.password = make_password(default_password)
        user.save()

        return Response({"message": f"Mật khẩu của {user_id} đã được đặt lại về mặc định."}, status=status.HTTP_200_OK)