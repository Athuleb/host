from rest_framework import serializers
from .models import UserModel

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    user_type = serializers.ChoiceField(choices=[('personal', 'Personal'), ('business', 'Business')], required=True)
    company = serializers.CharField(required=False, allow_blank=True)  
    
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'password', 'user_type', 'company', 'dob', 'gender', 'mobile', 'state', 'district', 'pincode']

    def create(self, validated_data):
        user_type = validated_data.get('user_type')

        
        if user_type == 'business' and not validated_data.get('company'):
            print('user_type>>>',user_type)
            raise serializers.ValidationError({"company": "Company name is required for business users."})
        
        # Create user based on user type
        user = UserModel.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            user_type=user_type,  # Set user type
            company=validated_data.get('company') if user_type == 'business' else None,  # Set company name if business user
            dob=validated_data.get('dob'),
            gender=validated_data.get('gender'),
            mobile=validated_data.get('mobile'),
            state=validated_data.get('state'),
            district=validated_data.get('district'),
            pincode=validated_data.get('pincode'),
        )
        
        return user
