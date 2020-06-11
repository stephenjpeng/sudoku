## Getting Started
To install requirements, use
```
pip install -r requirements.txt
```

To run the program, just run `sudoku.py`. 

Note: due to anti-aliasing issues on the Anaconda `tkinter` interface, it is highly recommended that Anaconda Python is not used. I was too lazy to figure out what was going on.

1. Click <kbd>Capture Problem</kbd> to use OCR to load a problem from a screen clipping. Try to clip as tightly around the border of the grid as possible, as OCR will only work if there are exactly 21 lines detected.
1. The program will extract the numbers it thinks are present and populate them as answers. Change these to the correct values, then click <kbd>Set Problem</kbd> to start the timer and begin solving.
1. <kbd>Validate Solution</kbd> will highlight incorrect answers made so far in red.
1. <kbd>Play/Pause</kbd> pauses/resumes the timer.

## Shortcuts
<kbd>🡐</kbd> <kbd>🡒</kbd> <kbd>🡑</kbd> <kbd>🡓</kbd> or <kbd>Click</kbd> to move around the grid.<br/>
<kbd>Shift</kbd> + [<kbd>🡐</kbd> <kbd>🡒</kbd> <kbd>🡑</kbd> <kbd>🡓</kbd>] or <kbd>Ctril</kbd> + <kbd>Click</kbd> to highlight multiple cells.<br/>
<kbd>Shift</kbd> + [<kbd>1</kbd> - <kbd>9</kbd>] pencils the given digit(s) in the corner.<br/>
<kbd>Ctrl</kbd> + [<kbd>1</kbd> - <kbd>9</kbd>] pencils the given digit(s) in the center.<br/>
<kbd>Bksp</kbd> deletes user-entered answers from the grid.<br/>
<kbd>Del</kbd> deletes user-entered answers and pencil marks from the grid.<br/>
<kbd>Ctrl</kbd> + <kbd>c</kbd>, <kbd>Ctrl</kbd> + <kbd>x</kbd>, and <kbd>Ctrl</kbd> + <kbd>v</kbd> work as expected (copy/cut/paste)-- only work for single cell operations.<br/>
