# Fluffy - AI powered photo describer
Automated image description based on Tensorflow

## How it works
Fluffy is a website that enables blind people to surf the web with the power of AI. Users can submit a photo to the website and it will use Google's Tensorflow API to guess what the image is representing.

## How to make it run
On your server install Python 3.6, [Tensorflow](https://www.tensorflow.org/install/pip), MySQL Server and these PIP packages:
* mysql-connector-python
* flask
* flask-cors

Get a client id from [Imgur website](https://apidocs.imgur.com/) and place it in the "main.js" file approximately at line 58.
Once you've done that, you can place the website on your favourite webserver and let it run!

## Screenshots
![Fluffy's main view](https://i.imgur.com/G5fBHBP.png "Main view")
![Fluffy's success view](https://i.imgur.com/xgFe1jD.png "Success screen, fluffy dsplay results")
![Fluffy's error view](https://i.imgur.com/c35hdsa.png "Error screen")

## License
All the code is licensed under the GNU General Public License v3.0, unless specified by the original creator of non-original pieces of the project.

## Credits
This work was made by Riccardo Carissimi. Some scripts are based on https://tensorflow.org/tutorials/image_recognition/.
