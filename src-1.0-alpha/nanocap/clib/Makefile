SHELL = /bin/sh
PYTHON_INCLUDES = $(shell python-config --includes)
PYTHON_SITE_PACKAGES = -I$(shell python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
INCLUDES = ${PYTHON_INCLUDES} ${PYTHON_SITE_PACKAGES}/numpy/core/include/

apt-get:
	cc -c -O3 -fPIC clib.c
	cc -shared -flat_namespace   -o clib.so clib.o


win:
	gcc -c -O3 -fPIC clib.c
	gcc -shared -flat_namespace -o clib.so clib.o

osx:
	cc -c -O3 -fPIC clib.c
	cc -mmacosx-version-min=10.4 -shared -flat_namespace -undefined suppress  -o clib.so clib.o

clean:
	rm  -f *.o *.so
	

