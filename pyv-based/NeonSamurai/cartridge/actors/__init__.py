"""
important remark to use sprite sheets!

 to load spritesheets you will need not only the .PNG but also a .JSON !
 this JSON file describes
 - how images are packed in your spritesheet
 - what name identifies every single image of your spritesheet

 To build a usable Spritesheet from a set of individual images, you can use this tool:
 https://www.codeandweb.com/tp-online then download both the .PNG and the .JSON
you will need to list the JSON in your list of assets (that is declared in metadat.json)
then, the data will be available from: pyv.vars.spritesheets[key] where key is the name given to your spritesheet

if you need an animation, you may use
pyv.gfx.AnimatedSprite()
"""
