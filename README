# Running the Counting Program

## Requirements

The program requires python version 3 and pytorch version 1.7 or higher.
A graphics card is not necessary, and it has not been tested using one.

### Code

I recommend using a [virtual environment](https://docs.python.org/3/library/venv.html) to manage the dependencies of this project.
To create a python virtual environment for the project run
```
python -m venv
```

Then activate the virtual environment.
```
source venv/bin/activate
```

Then install the requirements
```
pip install -r requirements.txt
```


### Camera

You will also need a camera.

#### Windows

Make sure the camera is on.
Plug the camera into the computer. 
If using the Canon camera, run the Canon EOS software.
Open up the camera app in windows, and verify that the camera is available.

#### Linux

Make sure the camera is on.
Plug the camera into the computer. 
On my machine I had to run the following commands to make the camera available:

```
sudo modprobe v4l2loopback exclusive_caps=1 card_label="GPhoto2 Webcam"
gphoto2 --stdout --capture-movie  \
| ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video2
```

## Running the program

Navigate to the root directory of the project.
Make sure the virtual environment is active

```
source venv/bin/activate
```

To run the program run the following command

```
python app.py --camera CAMERA --weights WEIGHTS
```

On linux `CAMERA` will be the path to the camera device, 
so in the previous example that would be `/dev/video2`.
On windows it is the index of the camera.
If the computer has a webcam, that is likely index 0, so the new camera is probably index 1.
In general just try different values until it works.

`WEIGHTS` will be the path to the weights for the model.

## Controls

The program starts in real time mode. It will show the live feed from the camera and the parts it detects.
Each of the dots shown is a predicted part.
Press `q` to quit the program.
Press `enter` to go to capture mode.

In capture mode you can count the parts.
Press `+` and `-` to increase and decrease the threshold.
The threshold is a value between 0 and 1, than determines what parts are shown.
For every prediction from the model, there is a confidence value.
If the confidence value is higher than the threshold the prediction is shown.

Press `tab` to toggle between seeing points and rectangles.

When you move the mouse around you will see a blue rectangle underneath where your mouse is.
This blue rectangle is the model's prediction at that location.
It will show **all** predictions, not just those that are above the confidence threshold.
This is useful for correcting the model's mistakes.
Usually, a part will be found by the model, the confidence just might be low.
Move the mouse over a undetected part and see if a blue rectangle appears.
If it does double click it to select it, and then double click it once more to set its confidence to 1.

The model can also make mistakes.
In these cases you will want to remove the bad predictions.
To do this you can double click the bad prediction twice to set its confidence to 0.

Press `p` to toggle between `selection mode` and `placement mode`
In placement mode you can double click to start a new bounding box.
Once you place the first point, you will see a preview of the rectangle you are creating.
Double click again to finish placing it.

Press `m` to toggle between masking the parts.
When the mask is active, the predicted regions will be shaded to match the background.
This makes it easier to see what parts haven't been found.

When you finish counting you can press `q` to leave capture mode and go back to real time mode.

# Training the model

Training the model is straightforward.
Follow the documentation [here](https://docs.ultralytics.com/yolov5/tutorials/train_custom_data/) to train the model.
The paths in the `.yaml` file can either be relative or absolute.
You do not have to use a training test split, you can simply set the training and test paths to be the same value.
