from rest_framework import serializers


class InitializeSerializer(serializers.Serializer):
    api_key = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    firstName = serializers.CharField(required=False)
    lastName = serializers.CharField(required=False)
    phoneNumber = serializers.CharField(required=False)

    # def validate_api_key(self, value):
    #     pass
    #
    # def validate(self, attrs):
    #     print("Validate:", attrs)
    #     pass

    def to_internal_value(self, data):
        """
        Deserialization customization, for write operations.
        :param data:
        :return:
        """
        print("to internal:", data)
        # "api_key" field has a dash in JSON. Manually set it here.
        data['api_key'] = data.get('api-key')
        return super(InitializeSerializer, self).to_internal_value(data)
