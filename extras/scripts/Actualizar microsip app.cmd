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
git checkout -- multiple_db\static\
git checkout -- multiple_db\Templates\
git checkout -- requirements\
git checkout -- multiple_db\Actualizar.lnk
git checkout -- multiple_db\Iniciar.lnk
git pull origin master
git gc
python manage.py syncdb 
yes
EXPLORER.EXE http://127.0.0.1:8000/inicializar_tablas
python manage.py runserver 127.0.0.1:8000
EXPLORER.EXE http://127.0.0.1:8000/inicializar_tablas
