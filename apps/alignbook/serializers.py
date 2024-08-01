from rest_framework import serializers

class VoucherSerializer(serializers.Serializer):
    voucher_value = serializers.CharField(max_length=255)


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    flag = serializers.CharField(max_length=155)
