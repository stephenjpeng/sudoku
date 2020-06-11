#!/usr/bin/python3 
import tkinter as tk
import copy
import src.constants as constants
import src.utils as utils
import src.puzzledetector as pdetector
import src.sudokusolver as solver
import functools
from datetime import datetime, timedelta
from time import sleep
import numpy as np
import pickle
# 

def createSudokuButton(parent, **kwargs):
    buttonArgs = {
        'relief': tk.SOLID,
        'background': constants.BUTTON_COLOR,
        'activebackground': constants.ACTIVE_BUTTON_COLOR,
        'fg': constants.BUTTON_TEXT_COLOR,
        'activeforeground': constants.BUTTON_TEXT_COLOR,
        'bd': 0,
    }
    buttonArgs.update(kwargs)

    return tk.Button(
        parent,
        **buttonArgs,
    )

class App(tk.Tk):
    def __init__(self, *args, **kwargs): 
        tk.Tk.__init__(self, *args, **kwargs)
        self.rows = 9
        self.columns = 9
        self.cellwidth = constants.CELL_WIDTH
        self.cellheight = constants.CELL_WIDTH
        self.fontsizes = {
            'answer': constants.ANSWER_SIZE,
            'corner': constants.CORNER_SIZE,
            'center': constants.CENTER_SIZE,
        }
        self.canvas = tk.Canvas(
            self,
            width=self.columns * self.cellwidth,
            height=self.rows * self.cellheight,
            borderwidth=0,
            highlightthickness=0
        )
        self.canvas.pack(side="top", fill="both", expand="true")
        self.update()
        self.popup = None
        self.popup_dims = { 'width': 500, 'height': 200 }

        self.hud = tk.Frame(
            self,
            bd=self.winfo_height()//30,
        )
        self.hud.pack()

        self.guis = [
            tk.Frame(
                self,
                # bd=self.winfo_height()//30 if i == 0 else 0,
                bd=0
            ) for i in range(3)
        ]
        for gui in self.guis:
            gui.pack(anchor='center')

        self.clock_running = False
        self.time = timedelta(seconds=0)
        self.clock = tk.Label(
            self.hud,
            text="00:00:00",
            font=constants.ANSWER_FONT,
            fg=constants.TEXT_COLOR,
        )
        self.clock.pack(side=tk.LEFT)

        self.pause = createSudokuButton(
            self.guis[0],
            text="Start/Pause",
            command=self._toggle_clock,
        )
        self.pause.pack(side=tk.LEFT, padx=self.winfo_height()//30)

        lock = createSudokuButton(self.guis[0], text="Set Problem", command=self._set_problem)
        lock.pack(side=tk.LEFT, padx=self.winfo_height()//30)
 
        check = createSudokuButton(self.guis[1], text="Check Answer", command=self._check_solution)
        check.pack(side=tk.LEFT, padx=self.winfo_height()//30)

        capture = createSudokuButton(self.guis[1], text="Capture Problem", command=self._capture_problem)
        capture.pack(side=tk.LEFT, padx=self.winfo_height()//30)

        capture = createSudokuButton(self.guis[2], text="Validate Answers", command=self._validate_solution)
        capture.pack(side=tk.LEFT, padx=self.winfo_height()//30)

        capture = createSudokuButton(self.guis[2], text="Solve Problem", command=self._solve_problem)
        capture.pack(side=tk.LEFT, padx=self.winfo_height()//30)

        self.update()

        self.state = {
            'board': constants.INITIAL_BOARD,
            'answers': constants.USER_BOARD,
            'solver': copy.deepcopy(constants.USER_BOARD),
            'corners': constants.USER_CORNERS,
            'centers': constants.USER_CENTERS,
        }

        self.solver = solver.SudokuSolver(self.state['board'])

        self.active = (-1, -1)
        self.selected = []
        self.undo_stack = []
        self.redo_stack = []

        self.rect = {}
        self.corners = {}
        self.centers = {}
        self.answers = {}
        self.solvers = {}
        self.givens = {}
        self._refresh_all()

        self.canvas.focus_set()
        self.canvas.bind("<A>", lambda event : self._create_popup(text=""))
        self.canvas.bind("<Escape>", lambda event : self._kill_popup())
        self.canvas.bind("<Button-1>", self._lmb_callback)
        self.canvas.bind("<Control-Button-1>", self._clmb_callback)
        self.canvas.bind("<Command-Button-1>", self._clmb_callback)
        self.canvas.bind("<BackSpace>", self._backspace_callback) 
        self.canvas.bind("<Delete>", self._delete_callback) 
        self.canvas.bind("<Key>", functools.partial(self._key_callback, control=False))
        self.canvas.bind("<Control-Key>", functools.partial(self._key_callback, control=True))
        self.canvas.bind("<Command-Key>", functools.partial(self._key_callback, control=True))
        self.canvas.bind("<Control-c>", self._copy_callback) 
        self.canvas.bind("<Command-c>", self._copy_callback) 
        self.canvas.bind("<Control-x>", self._cut_callback) 
        self.canvas.bind("<Command-x>", self._cut_callback) 
        self.canvas.bind("<Control-v>", self._paste_callback) 
        self.canvas.bind("<Command-v>", self._paste_callback) 
        self.canvas.bind("<Control-z>", self._undo_callback) 
        self.canvas.bind("<Command-z>", self._undo_callback) 
        self.canvas.bind("<Control-y>", self._redo_callback) 
        self.canvas.bind("<Command-y>", self._redo_callback) 
        self.canvas.bind("<Left>", functools.partial(self._dir_callback, shift=False, direction=constants.LEFT))
        self.canvas.bind("<Right>", functools.partial(self._dir_callback, shift=False, direction=constants.RIGHT))
        self.canvas.bind("<Up>", functools.partial(self._dir_callback, shift=False, direction=constants.UP))
        self.canvas.bind("<Down>", functools.partial(self._dir_callback, shift=False, direction=constants.DOWN))
        self.canvas.bind("<Shift-Left>", functools.partial(self._dir_callback, shift=True, direction=constants.LEFT))
        self.canvas.bind("<Shift-Right>", functools.partial(self._dir_callback, shift=True, direction=constants.RIGHT))
        self.canvas.bind("<Shift-Up>", functools.partial(self._dir_callback, shift=True, direction=constants.UP))
        self.canvas.bind("<Shift-Down>", functools.partial(self._dir_callback, shift=True, direction=constants.DOWN))
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        for i, gui in enumerate(self.guis):
            gui.place(relx=0.5, y=0.5*self.winfo_height()+self.cellheight*self.rows/2+self.guis[0].winfo_height()*1.25*(i+1), anchor=tk.N)
        self.hud.place(relx=0.5, y=0.5*self.winfo_height()-self.cellheight*self.rows/2, anchor=tk.S)
        self._update_clock()
        self.mainloop()

    def _update_clock(self):
        if self.clock_running:
            self.time = self.time + timedelta(seconds=1)
            new_time = utils.strfdelta(self.time, "{hours}:{minutes}:{seconds}")
            self.clock.configure(text=new_time)
        self.after(1000, self._update_clock)

    def _toggle_clock(self):
        self.clock_running = not self.clock_running
        if self.clock_running:
            self.timer_start = datetime.now()

    def _validate_solution(self):
        solution = self.solver.solve(render=False)
        incorrect = 0
        for i in range(solution.shape[0]):
            for j in range(solution.shape[1]):
                if solution[i, j] != self.state['answers'][i][j] and self.state['answers'][i][j] > 0:
                    self._highlight_answer(i, j)
                    incorrect += 1
        if incorrect:
            self._create_popup(text="%d errors found 😞" % incorrect, **self.popup_dims)
        else:
            self._create_popup(text="Looks good to me! 😃", **self.popup_dims)

    def _highlight_answer(self, row, column):
        if self.state['answers'][row][column] < 0:
            return
        else:
            self.canvas.delete(self.answers[row, column])
            self.answers[row, column] = self.draw_large(row, column, self.state['answers'][row][column], constants.WRONG_ANSWER_COLOR, tag="answer")

    def _solve_problem(self):
        if np.sum(np.array(self.state['board']) > 0) < 8:
            self._create_popup(text="Please make sure at least 8 digits are specified!", **self.popup_dims)
        else:
            start = datetime.now()
            self.solver.solve(render=True)
            end = datetime.now()
            solve_time = utils.strfdelta(end - start, "{seconds} seconds")
            if solve_time[:2] == '00':
                self._create_popup(text="Solved!", **self.popup_dims)
            else:
                self._create_popup(text="Solved in %s!" % solve_time, **self.popup_dims)

    def _capture_problem(self):
        detect = pdetector.SudokuDetector(True)
        board = np.maximum(self.state['board'], self.state['answers'])
        if np.max(board) > 0:
            self._create_popup(text="You can only capture a problem on an empty board!", **self.popup_dims)
            return
        self._create_popup(text="Please select the Sudoku grid with your mouse.", **self.popup_dims)
        detect.grab_image()
        self._kill_popup()
        detection = detect.detect_grid()
        if not detection:
            self._create_popup(text="Sorry, we were unable to recognize a Sudoku grid.", **self.popup_dims)
            return
        lazy_ocr = detect.extract_numbers()
        self._create_popup(text="  Running Tesseract OCR...", y_offset=-10, **self.popup_dims)
        res = np.empty(self.rows * self.columns, dtype=np.int8)
        progress_dims = {
            'width': 15 + res.shape[0] * 3,
            'height': 20,
            'offset': 8,
            'y_offset': 25,
        }
        progress_outline = self.popup.create_rectangle(
            ( self.popup_dims['width'] - progress_dims['width'] ) / 2,
            ( self.popup_dims['height'] - progress_dims['height'] ) / 2 + progress_dims['y_offset'],
            ( self.popup_dims['width'] + progress_dims['width'] ) / 2,
            ( self.popup_dims['height'] + progress_dims['height'] ) / 2 + progress_dims['y_offset'],
            fill='',
            outline=constants.FILL_COLOR,
            width=3,
        )
        progress_fill = self.popup.create_rectangle(
            ( self.popup_dims['width'] - progress_dims['width'] + progress_dims['offset'] ) / 2,
            ( self.popup_dims['height'] - progress_dims['height'] + progress_dims['offset'] ) / 2 + progress_dims['y_offset'],
            ( self.popup_dims['width'] - progress_dims['width'] + 15 ) / 2,
            ( self.popup_dims['height'] + progress_dims['height'] - progress_dims['offset']) / 2 + progress_dims['y_offset'],
            fill=constants.PROGRESS_FILL_COLOR,
            outline=constants.PROGRESS_FILL_COLOR,
        )

        for i, val in enumerate(lazy_ocr):
            res[i] = val
            self.popup.coords(
                progress_fill,
                ( self.popup_dims['width'] - progress_dims['width'] + progress_dims['offset'] ) / 2,
                ( self.popup_dims['height'] - progress_dims['height'] + progress_dims['offset'] ) / 2 + progress_dims['y_offset'],
                ( self.popup_dims['width'] - progress_dims['width'] + 15 + (i+1)*6 ) / 2,
                ( self.popup_dims['height'] + progress_dims['height'] - progress_dims['offset']) / 2 + progress_dims['y_offset'],
            )
            self.popup.itemconfig(self.popup_text, text=(" " * ((i // 5) % 3))+"Running Tesseract OCR"+("." * ((i // 5) % 3 + 1)))
            self.update_idletasks()

        res = res.reshape((self.rows, self.columns)).transpose()
        self.state['answers'] = res
        self._refresh_all()
        self._create_popup(text="Please double check and make corrections.", **self.popup_dims)

    def _check_solution(self):
        self.clock_running = False
        to_check = [[0] * self.columns] * self.rows
        answer = np.maximum(np.maximum(self.state['board'], self.state['answers']), self.state['solver'])
        if np.min(answer) < 1:
            self._create_popup(text="Please fill in all the blank spaces first!", width=500, height=200)
            return
        errors = []
        for i in range(self.rows):
            if np.unique(answer[i, :]).shape[0] < self.columns:
                errors += ["Duplicate number in row %d." % (i+1)]
        for i in range(self.columns):
            if np.unique(answer[:, i]).shape[0] < self.rows:
                errors += ["Duplicate number in column %d." % (i+1)]
        for i in range(self.rows // 3):
            for j in range(self.columns // 3):
                block = answer[i*3:(i+1)*3,j*3:(j+1)*3].flatten()
                if np.unique(answer[:, i]).shape[0] < self.rows:
                    errors += ["Duplicate number in block (%d, %d)." % (i+1, j+1)]
        if len(errors):
            error_text = "There are some errors:\n" + '\n'.join(['  '+e for e in errors])
            self._create_popup(text=error_text, width=600, height=400)
        else:
            final_time = utils.strfdelta(self.time, "{hours} hours, {minutes} mins, and {seconds} secs.")
            self._create_popup(text="Congrats! You finished the puzzle in %s" % final_time, width=700, height=200)

    def _set_problem(self):
        self.time = timedelta(seconds=0)
        del self.solver
        self.clock_running = True
        for i in range(len(self.state['board'])):
            for j in range(len(self.state['board'][0])):
                self.state['board'][i][j] = self.state['answers'][i][j] if self.state['board'][i][j] < 0 else self.state['board'][i][j]
        self.solver = solver.SudokuSolver(self.state['board'], renderer=self.render_answer)
        self._refresh_all()

    def _save_problem(self):
        self._set_problem()
        self.time = timedelta(seconds=0)
        self.clock_running = True
        f = None
        if f is None:
            return
        pickle.dump(self.state, f)
        f.close()

    def _create_popup(self, text, width=None, height=None, font=None, x_offset=0, y_offset=0):
        self.clock_running = False
        width = width or self.winfo_width()//2
        height = height or self.winfo_height()//4
        if self.popup:
            self._kill_popup()
        self.popup = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=constants.ACTIVE_COLOR,
            borderwidth=0,
            highlightthickness=0
        )
        self.popup.pack(side="top", fill="both", expand="true")
        self.popup.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.popup_text = self.popup.create_text(
            width / 2 + x_offset,
            height*0.5 + y_offset,
            text=text,
            font=font or constants.POPUP_FONT,
            fill=constants.TEXT_COLOR,
        )
        self.popup.create_text(
            width / 2,
            height - max(height*0.05, 20),
            text="Press <Esc> to close this window",
            font=constants.INFO_FONT,
            fill=constants.TEXT_COLOR,
        )
        self.update_idletasks()

    def _kill_popup(self):
        if self.popup:
            self.popup.destroy() # FIXME
            self.popup = None
            self.update_idletasks()

    def _backspace_callback(self, event):
        self._add_to_undo()
        for k in self.selected:
            self.state['answers'][k[0]][k[1]] = -1
            self._refresh_all()

    def _delete_callback(self, event):
        self._add_to_undo()
        for k in self.selected:
            self.state['answers'][k[0]][k[1]] = -1
            self.state['centers'][k[0]][k[1]] = set()
            self.state['corners'][k[0]][k[1]] = set()
            self._refresh_all()

    def _refresh_all(self):
        self.canvas.delete("answer")
        self.canvas.delete("solver")
        self.canvas.delete("corner")
        self.canvas.delete("center")
        for column in range(self.columns):
            for row in range(self.rows):
                self.rect[row, column] = self.draw_square(row, column)
                self.corners[row, column] = self.draw_corner(row, column)
                self.centers[row, column] = self.draw_center(row, column)
                self.answers[row, column] = self.draw_large(row, column, self.state['answers'][row][column], constants.ANSWER_COLOR, tag="answer")
                self.solvers[row, column] = self.draw_large(row, column, self.state['solver'][row][column], constants.SOLVER_COLOR, tag="solver")
                self.givens[row, column] = self.draw_large(row, column, self.state['board'][row][column], constants.GIVEN_COLOR)
        for i in [0, 3, 6]:
            _ = self.canvas.create_line(i * self.cellwidth, 0, i * self.cellwidth, 9 * self.cellwidth, fill=constants.OUTLINE_COLOR, width=6)
            _ = self.canvas.create_line(0, i * self.cellwidth, 9 * self.cellwidth, i * self.cellwidth, fill=constants.OUTLINE_COLOR, width=6)
        self._highlight_selected()

    def _copy_callback(self, event):
        r, c = self.active
        self.clipboard = { k: copy.deepcopy(self.state[k][r][c]) for k in self.state.keys() if k not in ['board', 'solver'] }

    def _cut_callback(self, event):
        r, c = self.active
        self.clipboard = { k: copy.deepcopy(self.state[k][r][c]) for k in self.state.keys() if k not in ['board', 'solver'] }
        for k in self.state.keys():
            if k not in ['board', 'solver']:
                if k == 'answers':
                    self.state[k][r][c] = -1
                else:
                    self.state[k][r][c] = set()
        self._refresh_all()

    def _paste_callback(self, event):
        self._add_to_undo(reset_redo=True)
        r, c = self.active
        for k, v in self.clipboard.items():
            self.state[k][r][c] = copy.deepcopy(v)
        self._refresh_all()

    def _undo_callback(self, event):
        if len(self.undo_stack):
            self._add_to_redo()
            last_state = self.undo_stack.pop()
            self.state = last_state
            self._refresh_all()

    def _redo_callback(self, event):
        if len(self.redo_stack):
            self._add_to_undo(reset_redo=False)
            last_state = self.redo_stack.pop()
            self.state['corners'] = last_state['corners']
            self.state['centers'] = last_state['centers']
            self.state['answers'] = last_state['answers']
            self._refresh_all()

    def _add_to_undo(self, reset_redo=True):
        self.undo_stack += [copy.deepcopy(self.state)]
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)
        if reset_redo:
            self.redo_stack = []

    def _add_to_redo(self):
        self.redo_stack += [copy.deepcopy(self.state)]
        if len(self.redo_stack) > 100:
            self.redo_stack.pop(0)

    def _key_callback(self, event, control):
        shift = False
        if event.keysym not in constants.DIGITS + constants.SYMBOLS:
            return
        try:
            keysym = int(event.keysym)
        except ValueError:
            if event.keysym in constants.SYMBOLS:
                keysym = int(constants.SYMBOLS_TO_DIGITS[event.keysym])
                shift = True
        else:
            if not self.clock_running:
                self.clock_running = True
            self._add_to_undo()
        if control:
            for cell in self.selected:
                self.state['answers'][cell[0]][cell[1]] = -1
                self.canvas.delete(self.answers[cell])
                if keysym not in self.state['centers'][cell[0]][cell[1]]:
                    self.state['centers'][cell[0]][cell[1]].add(keysym)
                else:
                    self.state['centers'][cell[0]][cell[1]].remove(keysym)
                self.centers[cell] = self.draw_center(cell[0], cell[1])
                self.corners[cell] = self.draw_corner(cell[0], cell[1])
        if shift:
            for cell in self.selected:
                self.canvas.delete(self.answers[cell])
                self.state['answers'][cell[0]][cell[1]] = -1
                for k in self.corners[cell]:
                    self.canvas.delete(k)
                if int(keysym) not in self.state['corners'][cell[0]][cell[1]]:
                    self.state['corners'][cell[0]][cell[1]].add(keysym)
                else:
                    self.state['corners'][cell[0]][cell[1]].remove(keysym)
                self.corners[cell] = self.draw_corner(cell[0], cell[1])
                self.centers[cell] = self.draw_center(cell[0], cell[1])
        elif not (shift or control):
            for cell in self.selected:
                self.state['answers'][cell[0]][cell[1]] = keysym
                self.canvas.delete(self.answers[cell])
                self.answers[cell] = self.draw_large(cell[0], cell[1], keysym, color=constants.ANSWER_COLOR, tag="answer")
                self.corners[cell] = self.draw_corner(cell[0], cell[1])
                self.centers[cell] = self.draw_center(cell[0], cell[1])
            if np.min(
                np.maximum(self.state['board'], self.state['answers'])
            ) > 0:
                self._check_solution()

    def _dir_callback(self, event, shift, direction):
        if self.active[0] < 0 and self.active[1] < 0:
            return
        if not self.clock_running:
            self.clock_running = True
        new_rc = self._get_new_coords(direction, self.active)
        counter = 0
        while self.state['board'][new_rc[0]][new_rc[1]] > 0 and counter < 9:
            new_rc = self._get_new_coords(direction, new_rc)
            counter += 1
        if not shift:
            self._clear_actives()
        self._set_active(new_rc)
        self.selected = self.selected + [self.active] if shift else [self.active]
        self._highlight_selected()

    def _get_new_coords(self, direction, cell):
        active_row, active_col = cell
        if direction == constants.UP:
            new_rc = ((active_row - 1) % 9, active_col)
        elif direction == constants.DOWN:
            new_rc = ((active_row + 1) % 9, active_col)
        elif direction == constants.LEFT:
            new_rc = (active_row, (active_col - 1) % 9)
        elif direction == constants.RIGHT:
            new_rc = (active_row, (active_col + 1) % 9)
        return new_rc

    def _lmb_callback(self, event):
        row, col = self._coords_rc(event.x, event.y)
        if self.state['board'][row][col] != -1:
            return
        if not self.clock_running:
            self.clock_running = True
        self._clear_actives()
        if row>=0 and col>=0:
            self._set_active((row, col))
            self.selected = [self.active]
            self._highlight_selected()

    def _clmb_callback(self, event):
        row, col = self._coords_rc(event.x, event.y)
        if self.state['board'][row][col] != -1:
            return
        if not self.clock_running:
            self.clock_running = True
        row, col = self._coords_rc(event.x, event.y)
        if row >= 0 and col >= 0:
            self._set_active((row, col))
            self.selected += [(row, col)]
            item_id = self.rect[row, col]
            self.canvas.itemconfig(item_id, fill=constants.ACTIVE_COLOR)

    def _clear_actives(self):
        for (rowi, coli) in self.selected:
            self.canvas.itemconfig(
                self.rect[rowi, coli],
                fill=constants.FILL_COLOR,
                outline=constants.OUTLINE_COLOR,
            )

    def _highlight_selected(self):
        for (rowi, coli) in self.selected:
            self.canvas.itemconfig(
                self.rect[rowi, coli],
                fill=constants.ACTIVE_COLOR,
            )

    def _set_active(self, new_active):
        if self.active[0] >= 0 and self.active[1] >= 0:
            self.canvas.itemconfig(
                self.rect[self.active],
                outline=constants.OUTLINE_COLOR,
            )
        self.active = new_active
        self.canvas.itemconfig(
            self.rect[self.active],
            outline=constants.ACTIVE_OUTLINE_COLOR,
        )
    def _coords_rc(self, x, y):
        if (x // self.cellheight > 8) or (y // self.cellheight > 8):
            return False, False
        return ( y // self.cellheight, x // self.cellwidth )

    def _rc_coords(self, row, column, size=None):
        size = size or self.cellwidth
        x1 = column * size
        y1 = row * size
        x2 = x1 + size
        y2 = y1 + size
        return x1, y1, x2, y2

    def _idx_corner_offset(self, idx):
        idx = idx % 8
        if idx < 4:
            return (
                self.cellwidth*(0.2 + 0.6*(idx % 2)),
                self.cellwidth*(0.2 + 0.6*(idx // 2))
            )
        else:
            if idx == 4:
                x_offset = 0
                y_offset = -0.3
            if idx == 5:
                x_offset = -0.3
                y_offset = -0.0
            if idx == 6:
                x_offset = 0.3
                y_offset = -0.0
            if idx == 7:
                x_offset = 0
                y_offset = 0.3
            x_offset *= self.cellwidth
            y_offset *= self.cellheight
            return (
                self.cellwidth*0.5 + x_offset,
                self.cellwidth*0.5 + y_offset,
            )

    def _rc_filled(self, row, column):
        return (
            self.state['board'][row][column] > 0 or
            self.state['answers'][row][column] > 0 or
            self.state['solver'][row][column] > 0
        ) 

    def render_answer(self, row, column, value):
        self.state['solver'][row][column] = value
        self.canvas.delete(self.solvers[row, column])
        self.canvas.delete('answer')
        self.canvas.delete('corner')
        self.canvas.delete('center')
        self.solvers[row, column] = self.draw_large(row, column, self.state['solver'][row][column], constants.SOLVER_COLOR, tag="solver")
        self.canvas.update_idletasks()
        sleep(constants.SOLVER_SLEEP)

    def draw_square(self, row, column, size=None, width=1):
        size = size or self.cellwidth
        x1, y1, x2, y2 = self._rc_coords(row, column, size=size)
        return self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=constants.FILL_COLOR,
            outline=constants.OUTLINE_COLOR,
            width=width,
            tags="rect",
        )

    def draw_large(self, row, column, num, color, tag="board"):
        if num < 0:
            return 
        x1, y1, x2, y2 = self._rc_coords(row, column)
        text = str(num)
        return self.canvas.create_text(
            x1 + self.cellwidth * 0.5,
            y1 + self.cellheight * 0.5,
            text=text,
            font=constants.ANSWER_FONT,
            fill=color,
            tag=tag,
        )

    def draw_center(self, row, column):
        try:
            self.canvas.delete(self.centers[row, column])
        except KeyError:
            pass
        x1, y1, x2, y2 = self._rc_coords(row, column)
        nums = self.state['centers'][row][column]
        text = ''.join([str(n) for n in sorted(nums)]) if not self._rc_filled(row, column) else ''
        return self.canvas.create_text(
            x1 + self.cellwidth * 0.5,
            y1 + self.cellheight * 0.52,
            text=text,
            font=("texgyreheros", self.fontsizes['center']),
            fill="gray",
            tag="center",
        )

    def draw_corner(self, row, column):
        texts = []
        try:
            for k in self.corners[row, column]:
                self.canvas.delete(k)
        except KeyError:
            pass
        if self._rc_filled(row, column):
            return texts
        x1, y1, x2, y2 = self._rc_coords(row, column)
        nums = self.state['corners'][row][column]
        for i, n in enumerate(sorted(nums)):
            dx, dy = self._idx_corner_offset(i)
            texts += [self.canvas.create_text(
                x1 + dx,
                y1 + dy,
                text=str(n),
                font=("texgyreheros", self.fontsizes['corner']),
                fill="gray",
                tag="corner",
            )]
        return texts


if __name__ == "__main__":
    app = App()
