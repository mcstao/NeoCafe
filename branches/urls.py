from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, BranchMenuView, BranchMenuByCategoryView

router = DefaultRouter()
router.register(r'', BranchViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('branches/menu/', BranchMenuView.as_view(), name='branch-menu'),
    path('branches/menu/category/<int:category_id>/',
         BranchMenuByCategoryView.as_view(), name='branch-menu-by-category'),
]
