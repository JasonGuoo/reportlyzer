# Dev Notes

## Front end
### Bootstrap
- Use bootstrap5 as front-end
- Use https://startbootstrap.com/template/sb-admin sb-admin bootstrap as HTML template
- Use Morph theme https://bootswatch.com/morph/

## Backend

## database

## design

## Issues
#### Mac上不能安装psycopg2

First thing first, you need to verify that openssl is installed and correctly linked:
~~~
brew install openssl
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
~~~
Now, if using python 3.8 means python executable is bound to python 3.8, you may want to try the following workarounds:

Workaround #1: Install specifying the interpreter
~~~
python -m pip --no-cache install psycopg2
~~~