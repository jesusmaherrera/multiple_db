echo off
color 30
echo 			==================================
echo 			=                                =
echo 			=     ACTUALIZANDO APLICACION    =
echo 			=                                =
echo 			=   [ POR FAVOR NO CERRAR!!!! ]  =
echo 			=                                =
echo 			==================================
echo.
echo.


cd C:\multiple_db
git clean -df & git checkout -- multipledb\Apps\
git checkout -- multipledb\static\
git checkout -- multipledb\Templates\
git checkout -- requirements\
git checkout -- multipledb\Actualizar.lnk
git checkout -- multipledb\Iniciar.lnk
git pull origin master
git gc
python manage.py syncdb 
yes
