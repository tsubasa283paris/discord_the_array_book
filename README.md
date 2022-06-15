# the array book

`python run.py`

## installation

1. Setup pipenv

2. Clone into this repository and get inside of it  
   ```bash
   git clone git@github.com:tsubasa283paris/discord_the_array_book.git
   cd discord_the_array_book
   ```

3. Install all dependencies  
   ```bash
   pipenv install
   ```

4. Create a file `.env`  
   1. Create with blank
      ```bash
      echo -e 'DISCO_TOKEN=\nDISCO_CHID=' > .env
      ```

   2. Open it and set each value  
      ```
      DISCO_TOKEN=***
      DISCO_CHID=***
      ```

      - `DISCO_TOKEN`: The bot token you can retrieve from your Application > Bot > Build-A-Bot
      - `DISCO_CHID`: The text channel ID (numeric) where you want this app to post global messages

5. (optional) In case you want to enable the feature to automatically save md files into your Google Drive, follow the official document:  
   <https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred>  
   And then copy `client_secret.json` into the root directory of this repository.  
   The JSON file must be formed like:  
   ```json
   {
      "web": {
         "client_id": "xxx.com",
         "project_id": "foobar",
         "auth_uri": "someurl",
         "token_uri": "someurl",
         "auth_provider_x509_cert_url": "someurl",
         "client_secret": "v3RySeCRet-STR1ng"
      }
   }
   ```
