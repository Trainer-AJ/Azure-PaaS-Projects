# PhotoVault: Smart personal photo album

## Features

### User Registration:
* Register with a unique username and email.
* Passwords are stored as hashes.
* If the username or email is already registered, a warning prompts the user to choose a different one.

### User Login:
* Log in using either username or email and password.

### Forgot Password:
* Users can reset their password via a link sent to their registered email, containing a unique token valid for 10 minutes, or by entering an OTP.

### Photo Upload:
* After logging in, users can upload photos with a title, description, location, and tags.
* Each photo is only visible to the user who uploaded it.

### Profile Updation & Management:
* Users can update their profile information (name, username, email, and profile picture) in real time.
* Users can also permanently delete their accounts.

## Use this locally on Docker
1. Must have MySQL up and running.
2. Create a .env file and enter these details:
```env
EMAIL_ID=
EMAIL_PASS=
MYSQL_HOST=host.docker.internal     # Or as required
MYSQL_USER=     # your MySQL user
MYSQL_ROOT_PASSWORD=    # your MySQL password
PHOTO_ALBUM_DB=photo_album
USER_INFO_TABLE=user_info
PHOTO_INFO_TABLE = photo_info
```
3. Pass on any names you like.
4. Run this on terminal: `docker run -p 80:80 --env-file .env --name photo-album aanshojha/photo-album`
5. To stop, `docker stop photo-album`
> * `EMAIL_ID` and `EMAIL_PASS`, are not necessary to run the application. For sending reset password emails, add those credentials (Need to have SMTP protocol)

> * `MYSQL_HOST` value
> 1. For local development: `localhost`
> 2. For docker container to host: `host.docker.internal`

## Demo
* [Screenshots](https://drive.google.com/drive/folders/1xg2_eAXhRO3Mm3c6d4-09u8ZaiAOuRxZ?usp=sharing)