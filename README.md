
The current set of scripts aims at easing the testing of parts of the `katagames_sdk`.

## Content

Resources for testing need to be as various as possible. More specifically scripts need to verify the compliance of the pygame emulator with what you'd get by running your script from within the Python Interpreter (expected behaviors).


## How to design new scripts?

Providing many use-cases is key. All together, scripts ensure that most of pygame functions and features are available in the browser.

## Format/rules

Each test has to consist in one `.py` file, and one file only!
Do not import libraries except from the python std lib, and the `katagames_sdk` of course.
