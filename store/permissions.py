from rest_framework.permissions import BasePermission, SAFE_METHODS, DjangoModelPermissions


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:                              #safe methods are constants that include 'get', 'head' and 'option'
            return True
        return bool(request.user and request.user.is_staff)   
    




class FullDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']





class ViewCustomerHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_histroy')    #view_histroy is a codename 
    
# 'has_perm' contains all the permissions given to a specific user