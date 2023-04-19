# Fluffy - Docker
This is the dockerized version of the APIs only.
Fluffy is an automated image description based on Tensorflow, powered by AI.

## How to make it run
### 1. Install docker
Follow the [guide for your OS](https://lmgtfy.app/?q=docker+install). Don't bother me.

### 2. Clone the repository
With HTTP or SSH clone.
```
git clone -b dockerized-api https://github.com/r-carissimi/Fluffy.git
```

### 3. Build the image
```
cd Fluffy/
docker build -t fluffy-api .
```

### 4. Run the image
Remember to expose the `5000` port.
```
docker run -p 8069:5000 fluffy-api
```

### 5. Try it
Find an image on Imgur, [like this](https://i.imgur.com/0366DUS.jpeg). Then provide only the name in the url.

`http://192.168.1.98:8069/api/0366DUS.jpeg`
