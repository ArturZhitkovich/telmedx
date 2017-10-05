Telmedx Frontend
================

Before attempting to build
--------------------------
This assumes `node` is already installed on your machine. If you need to 
install `node`, go to: https://nodejs.org/en/.

1.  Install dependencies in `package.json` by doing: 
    ```bash  
    $ npm install 
    # alternatively, you can use `yarn`
    $ yarn install
    ```
2. Install global dependencies used for `brunch`
   ```bash
   $ npm install -g brunch uglify-es
   ```
   
Building
--------
* To build the frontend in "watch" mode, which will compile the frontend
  on-the-fly as you edit, use `brunch w` or `brunch watch`
* To build the frontend as files only, use `brunch build`.
    * After building, you will then need to get Django to collect the files:
      ```bash
      # activate your virtualenv, then,
      <virtualenv active> /base_dir/ $ ./manage.py collectstatic
      ```
