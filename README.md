# Face Recognition - E-Corridor - H2020
## [server.py](https://github.com/MorphSeur/faceRecognitionH2020_2/blob/master/server.py)
The version of the IAI-skeleton is 1.1.  
The face recognition library is integrated with the new trained models.  
[server.py](https://github.com/MorphSeur/faceRecognitionH2020_2/blob/master/server.py) performs real face recognition, saliency detection and face recognition.

To run an example:
- Start the analytic
    ```sh
    $ python server.py
    $ python python iai_test_client.py --target http://0.0.0.0:5000 start --datalake ./tmp/testiai Chandler.jpg
    ```
- Stop the analytic
    ```sh
    $ python python iai_test_client.py --target http://0.0.0.0:5000 stop
    ```

## Requirements
Please refer to [requirements.txt](https://github.com/MorphSeur/faceRecognitionH2020_2/blob/master/requirements.txt).

## Dockerfile
Dockerfile contains necessary libraries to face recognition analytics.
- To build the docker
    ```
    $ sudo docker build --tag face_recognition .
    ```
- To run the analytic
    ```
    $ sudo docker run --publish 5000:5000 --volume="/path/to/tmp/testiai/:/path/to/tmp/testiai/tmp/testiai/" -v $(pwd):/app face_recognition sh /app/docker-entrypoint.sh
    ```

## Missing
Program to extract ground truth from ID, e.g., passport, is needed.  
Program to create random number to track the passenger is needed.  
Missing the integration of the previous programs in the above face recognition program.