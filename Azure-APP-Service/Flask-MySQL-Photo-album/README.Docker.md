# Use this locally
1. Must have MySQL up and running.
2. Create a .env file and enter these details:
```env
EMAIL_ID=
EMAIL_PASS=
MYSQL_HOST=host.docker.internal # Or as required
MYSQL_USER=
MYSQL_ROOT_PASSWORD=
PHOTO_ALBUM_DB=
USER_INFO_TABLE=
PHOTO_INFO_TABLE 
```
3. Pass on any names you like, and in `EMAIL_ID` and `EMAIL_PASS`, add those credentials which can send password reset emails (Need to have SMTP protocol)
4. Run this on terminal: `docker run -p 80:80 --env-file .env aanshojha/photo-album`
   
   
### Building and running your application

When you're ready, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:80.

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References
* [Docker's Python guide](https://docs.docker.com/language/python/)