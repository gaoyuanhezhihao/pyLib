# Play Images 


```bash
python3 images_player.py /path/to/image-directory/
```
Images inside the directory should be named xxx.yy, xxx is number, yy is extension of image, such as 124.jpg

After the player is started, it will show the images one by one at default speed 10Hz. You can use following keys to control it.

| Key   | Command                |
| ----- | ---------------------- |
| .     | speed up               |
| ,     | slow down              |
| space | toggle pause/continue  |
| q     | quit                   |
| d     | step to next frame     |
| a     | step to previous frame |



# Show IOU 

```bash
python3 ./IoU_player.py  /path/to/validation/images/directory  /path/to/validation/result/directory/ /path/to/annotations.xml
```

Commands are same as the ones above


# Calculate precision and recall

```bash
python3 /path/to/validation/result/directory/ /path/to/annotations.xml 
```

