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
from django.db import connection
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


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
    parser_classes = [MultiPartParser, FormParser,JSONParser]
    # @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
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
        extra_fields['user'] = user.user_id  

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
        user_data = self.get_user_data(user.user_id)
        
        if not user_data:
            return Response({'error': 'User not found'}, status=404)

        role_data = self.get_role_data(user.user_id)
        if role_data:
            user_data.update(role_data)
        
        return Response(user_data)

    def get_user_data(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, email, phone_number, role, image, full_name, sex, day_of_birth, nation,
                       active_status, is_active, is_staff, is_superuser, date_joined, last_login
                FROM custom_user
                WHERE user_id = %s
            """, [user_id])
            row = cursor.fetchone()
        
        if row:
            image_url = f"{settings.MEDIA_URL}{row[4]}" if row[4] else None
            return {
                'user_id': row[0], 'email': row[1], 'phone_number': row[2], 'role': row[3],
                'image': image_url if row[4] else None, 'full_name': row[5], 'sex': row[6],
                'day_of_birth': row[7], 'nation': row[8], 'active_status': row[9],
                'is_active': row[10], 'is_staff': row[11], 'is_superuser': row[12],
                'date_joined': row[13], 'last_login': row[14]
            }
        return None

    def get_role_data(self, user_id, role):
        role_query = {
            'teacher': "SELECT contract_types, expertise_levels, subjects FROM teacher WHERE user_id = %s",
            'admin': "SELECT contract_types, expertise_levels, description FROM admin WHERE user_id = %s",
            'student': "SELECT classroom_id FROM student WHERE user_id = %s",
        }
        
        if role in role_query:
            with connection.cursor() as cursor:
                cursor.execute(role_query[role], [user_id])
                row = cursor.fetchone()
            
            if row:
                if role == 'teacher':
                    return {'teacher': {'contract_types': row[0], 'expertise_levels': row[1], 'subjects': row[2]}}
                elif role == 'admin':
                    return {'admin': {'contract_types': row[0], 'expertise_levels': row[1], 'description': row[2]}}
                elif role == 'student':
                    return {'student': {'classroom_id': row[0]}}
        return None


    @action(detail=False, methods=['get'], url_path='detail/(?P<user_id>[^/.]+)', permission_classes=[IsAuthenticated])
    def user_detail(self, request, user_id):
        """
        API: `/api/accounts/users/detail/<user_id>/`
        → Chỉ Admin mới có quyền xem thông tin của người khác (bao gồm thông tin chi tiết của role).
        """
        if request.user.role != 'admin':
            return Response({"error": "Bạn không có quyền xem thông tin này."}, status=403)

        user_data = self.get_user_data(user_id)
        if not user_data:
            return Response({'error': 'User not found'}, status=404)

        role_data = self.get_role_data(user_id, user_data['role'])
        if role_data:
            user_data.update(role_data)
        
        return Response(user_data)


    @action(detail=False, methods=['put'], url_path='update', permission_classes=[IsAuthenticated], parser_classes=[JSONParser, MultiPartParser, FormParser])
    def update_self(self, request):
        return self._update_user(request, request.user.user_id, is_admin=False)

    @action(detail=True, methods=['put'], url_path='update', permission_classes=[IsAuthenticated], parser_classes=[JSONParser, MultiPartParser, FormParser])
    def update_other(self, request, pk=None):
        if request.user.role != "admin":
            return Response({"error": "Bạn không có quyền chỉnh sửa người khác."}, status=403)

        user = get_object_or_404(CustomUser, user_id=pk)
        return self._update_user(request, user.user_id, is_admin=True)

    def _update_user(self, request, user_id, is_admin):
        """
        Xử lý cập nhật thông tin user (dùng chung cho self-update và admin-update).
        """
        update_data = request.data.copy()

        # Cấm thay đổi user_id và role
        update_data.pop("user_id", None)
        update_data.pop("role", None)

        # Lấy thông tin user
        user = get_object_or_404(CustomUser, user_id=user_id)

        # Xử lý ảnh đại diện nếu có
        image = request.FILES.get('image')
        if image:
            user.image = image  # Lưu ảnh trực tiếp qua model

        # Cập nhật các trường còn lại
        for key, value in update_data.items():
            setattr(user, key, value)

        user.save()

        # Lấy thông tin user sau cập nhật
        user_data = self.get_user_data(user_id)
        if not user_data:
            return Response({'error': 'User not found'}, status=404)

        # Cập nhật thông tin role nếu có
        role_data = self.get_role_data(user_id, user_data['role'])
        if role_data:
            user_data.update(role_data)

        return Response({"message": "Cập nhật thành công", "user": user_data})

    

    @action(detail=True, methods=['delete'], url_path='delete', permission_classes=[IsAuthenticated])
    def delete_user(self, request, pk=None):
        """
        API: `/api/accounts/users/<user_id>/delete/`
        → Chỉ Admin mới có thể xóa user.
        """
        if request.user.role != "admin":
            return Response({"error": "Bạn không có quyền xóa user."}, status=403)

        user = get_object_or_404(CustomUser, user_id=pk)
        
        # Xóa dữ liệu liên quan từ bảng con
        role = user.role
        if role == "student":
            Student.objects.filter(user=user).delete()
        elif role == "teacher":
            Teacher.objects.filter(user=user).delete()
        elif role == "admin":
            Admin.objects.filter(user=user).delete()

        # Xóa user chính
        user.delete()

        return Response({"message": f"User {pk} đã được xóa thành công."}, status=200)
    




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
    

class UserDetailView(APIView):
    """ API lấy thông tin chi tiết của người dùng theo role """
    
    permission_classes = [AllowAny]  # Nếu cần xác thực thì dùng IsAuthenticated
    
    # def post(self, request):
    #     role = request.data.get("role")
    #     requested_fields = request.data.get("fields", [])
        
    #     # Danh sách role hợp lệ và bảng tương ứng
    #     valid_roles = {"teacher": "teacher", "admin": "admin", "student": "student"}
    #     if role not in valid_roles:
    #         return Response({"error": "Invalid role"}, status=400)

    #     table_name = valid_roles[role]

    #     # Mapping các trường hợp lệ giữa custom_user và bảng con (teacher/admin/student)
    #     valid_fields = {
    #         "user_id": "custom_user.user_id",
    #         "full_name": "custom_user.full_name",
    #         "phone_number": "custom_user.phone_number",
    #         "image": "custom_user.image",
    #         "email": "custom_user.email",
    #         "sex": "custom_user.sex",
    #         "day_of_birth": "custom_user.day_of_birth",
    #         "nation": "custom_user.nation",
    #         "active_status": "custom_user.active_status",
    #         "contract_types": f"{table_name}.contract_types" if role in ["teacher", "admin"] else None,
    #         "expertise_levels": f"{table_name}.expertise_levels" if role in ["teacher", "admin"] else None,
    #         "description": f"{table_name}.description" if role == "admin" else None,
    #         "classroom": "student.classroom_id" if role == "student" else None,
    #         "subjects": "teacher.subjects" if role == "teacher" else None 
    #     }

    #     # Kiểm tra các fields hợp lệ
    #     selected_fields = []
    #     for field in requested_fields:
    #         if valid_fields.get(field) is not None:
    #             selected_fields.append(valid_fields[field])
    #         else:
    #             return Response({"error": f"'{field}' not found in {role}"}, status=400)

    #     if not selected_fields:
    #         return Response({"error": "No valid fields requested"}, status=400)

    #     fields_str = ", ".join(selected_fields)
        
    #     # Truy vấn dữ liệu từ PostgreSQL
    #     query = f"""
    #         SELECT {fields_str} FROM custom_user
    #         LEFT JOIN {table_name} ON custom_user.user_id = {table_name}.user_id
    #         WHERE custom_user.role = %s
    #     """

    #     with connection.cursor() as cursor:
    #         cursor.execute(query, [role])
    #         columns = [col[0] for col in cursor.description]
    #         results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    #     if not results:
    #         return Response({"error": f"No {role} found"}, status=404)

    #     return Response({"data": results})
    def post(self, request):
        role = request.data.get("role")
        requested_fields = request.data.get("fields", [])
        
        # Danh sách role hợp lệ và bảng tương ứng
        valid_roles = {"teacher": "teacher", "admin": "admin", "student": "student"}
        if role not in valid_roles:
            return Response({"error": "Invalid role"}, status=400)

        table_name = valid_roles[role]

        # Mapping các trường hợp lệ giữa custom_user và bảng con (teacher/admin/student)
        valid_fields = {
            "user_id": "custom_user.user_id",
            "full_name": "custom_user.full_name",
            "phone_number": "custom_user.phone_number",
            "image": "custom_user.image",
            "email": "custom_user.email",
            "sex": "custom_user.sex",
            "day_of_birth": "custom_user.day_of_birth",
            "nation": "custom_user.nation",
            "active_status": "custom_user.active_status",
            "contract_types": f"{table_name}.contract_types" if role in ["teacher", "admin"] else None,
            "expertise_levels": f"{table_name}.expertise_levels" if role in ["teacher", "admin"] else None,
            "description": f"{table_name}.description" if role == "admin" else None,
            "classroom": "student.classroom_id" if role == "student" else None,
            "subjects": "teacher.subjects" if role == "teacher" else None 
        }

        # Kiểm tra các fields hợp lệ
        selected_fields = []
        for field in requested_fields:
            if valid_fields.get(field) is not None:
                selected_fields.append(valid_fields[field])
            else:
                return Response({"error": f"'{field}' not found in {role}"}, status=400)

        if not selected_fields:
            return Response({"error": "No valid fields requested"}, status=400)

        fields_str = ", ".join(selected_fields)
        
        # Truy vấn dữ liệu từ PostgreSQL
        query = f"""
            SELECT {fields_str} FROM custom_user
            LEFT JOIN {table_name} ON custom_user.user_id = {table_name}.user_id
            WHERE custom_user.role = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [role])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        if not results:
            return Response({"error": f"No {role} found"}, status=404)

        # Cập nhật đường dẫn hình ảnh
        for result in results:
            if "image" in result and result["image"]:
                result["image"] = settings.MEDIA_URL + result["image"]

        return Response({"data": results})