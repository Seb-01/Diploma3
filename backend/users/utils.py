from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model


def get_and_authenticate_user(email, password):
    """
    The flow for login endpoint would be to get an email and password, authenticate the user based on the given
     credentials and provide the appropriate response based on authentication.
    """
    # If the given credentials are valid, return a User object.
    user = authenticate(username=email, password=password)
    if user is None:
        raise serializers.ValidationError("Invalid username/password. Please try again!")
    return user

def create_user_account(email, password, first_name="",
                        last_name="", **extra_fields):
    """
    we’ll create the user account and return the response. For creating a user account,
     we can define a helper function.
    """
    user = get_user_model().objects.create_user(
        email=email, password=password, first_name=first_name,
        last_name=last_name, **extra_fields)
    return user