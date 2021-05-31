import factory

class UserFactory(factory.django.DjangoModelFactory):

    username = "adedayo123"
    first_name = "Adedayo"
    last_name = "Ayeni"
    email = "ade.dayo@yeni.com"

    class Meta:
        model = "userapp.User"
        django_get_or_create = ('username',)
    


class UserProfileFactory(factory.django.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)
    timezone = 'Africa/Lagos'

    class Meta:
        model = "userapp.UserProfile"