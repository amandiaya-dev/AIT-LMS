import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

def setup():
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_user(
            username='admin',
            password='AIT@2026'
        )
        admin.is_staff = True
        admin.is_superuser = True
        
        # Automatically sets the role if your model has a custom role field
        if hasattr(admin, 'role'):
            admin.role = 'ADMIN' 
            
        admin.save()
        print(" Admin user created successfully! Username: admin | Password: AIT@2026")
    else:
        print(" Admin user already exists.")

if __name__ == '__main__':
    setup()