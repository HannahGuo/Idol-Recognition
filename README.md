All the images used for training. 

Since the images aren't needed once they have been converted to numpy arrays, I decided to put these on a separate branch.

The structures is (pretty self-explanatory):
`training_faces -> <group> -> <members>`

Inside each member is both the numpy folder and the images.

A note on training data: Each image must include one clear shot of the idol's face. An error will be printed if this condition isn't met.