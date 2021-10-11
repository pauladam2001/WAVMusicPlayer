from tkinter import *
from tkinter import filedialog
import pygame
import time
from mutagen.wave import WAVE
import tkinter.ttk as ttk
from tkinter import messagebox
import sqlite3


class GUI:
    def __init__(self, controller, repository):
        self._controller = controller
        self._repository = repository

        self.root = Tk()
        self.root.title("WAV Player")
        self.root.iconbitmap("../MusicPlayer/images/music_player.ico")
        self.root.geometry("550x375")
        # self.root.configure(bg="powder blue")

        self.master_frame = Frame(self.root)
        self.master_frame.pack(pady=20, expand=True)    # for moving with the window

        self.song_box = Listbox(self.master_frame, bg="white", fg="black", width=75, selectbackground="blue",
                                selectforeground="white")
        self.song_box.grid(row=0, column=0, sticky="nsew")   # sticky north south east west for moving with the window
        # self.song_box.pack()

        # initializing
        self.paused = False
        self.stopped = False
        self.index = 0
        self.song_length = -1
        self.muted = False

        # for time
        self.status_bar = Label(self.root, text='', bd=3, relief=RAISED, anchor=CENTER)
        self.status_bar.pack(fill=X, side=BOTTOM, ipady=2)

        # song slider
        self.slider = ttk.Scale(self.master_frame, from_=0, to=100, orient=HORIZONTAL, value=0, length=360,
                                command=self.slide)
        self.slider.grid(row=1, column=0, pady=10)
        # self.slider.pack()

        # volume slider frame
        volume_frame = LabelFrame(self.master_frame, text="Volume")
        volume_frame.grid(row=0, column=1, padx=20)
        # volume_frame.pack()

        # volume slider
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=VERTICAL, value=1, length=125,
                                       command=self.volume)
        self.volume_slider.grid(row=0, column=0)
        # self.volume_slider.pack(pady=10)

        # mute/unmute button
        self.mute_img = PhotoImage(file='../MusicPlayer/images/speaker_mute.png')
        self.sound_img = PhotoImage(file='../MusicPlayer/images/sound.png')
        self.mute_unmute_button = Button(volume_frame, image=self.sound_img, borderwidth=0, command=self.mute_unmute)
        self.mute_unmute_button.grid(row=1, column=0)

        pygame.mixer.init()

        self.init_listbox()

    def init_listbox(self):
        songs = self._controller.get_songs()
        for song in songs:
            self.song_box.insert(END, song[0])

    def add_song(self):
        song = filedialog.askopenfilename(initialdir='songs/', title="Choose a song",
                                          filetypes=(("wav files", "*.wav"),))
        replacement_song = song
        abs_path = replacement_song[:replacement_song.rfind("songs/")]   # finding the absolute path
        abs_path += 'songs/'
        # delete directory info from the song name
        # song = song.replace("C:/Users/paula/PycharmProjects/Music Player/songs/", "")   # absolute path
        song = song.replace(abs_path, "")

        try:
            self._controller.add_one_song(song)
            self.song_box.insert(END, song)  # always add the song at the final
        except sqlite3.IntegrityError:
            messagebox.showinfo("Error", "Song '" + song + "' already in playlist!")

    def add_many_songs(self):
        songs = filedialog.askopenfilenames(initialdir='songs/', title="Choose a song",
                                            filetypes=(("wav files", "*.wav"),))
        for song in songs:
            replacement_song = song
            abs_path = replacement_song[:replacement_song.rfind("songs/")]  # finding the absolute path
            abs_path += 'songs/'
            # song = song.replace("C:/Users/paula/PycharmProjects/Music Player/songs/", "")  # absolute path
            song = song.replace(abs_path, "")

            try:
                self._controller.add_one_song(song)
                self.song_box.insert(END, song)  # always add the song at the final
            except sqlite3.IntegrityError:
                messagebox.showinfo("Error", "Song '" + song + "' already in playlist!")
                continue

    def play(self):
        try:
            self.index = self.song_box.curselection()[0]    # get the current index
        except IndexError:
            messagebox.showinfo("Error", "Select a song first!")

        self.stopped = False
        self.slider.config(value=0)

        song = self.song_box.get(ACTIVE)
        song = f'..\\MusicPlayer\\songs\\{song}'    # reconstruct song name

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(song)
        try:
            pygame.mixer.music.play()
        except pygame.error:
            messagebox.showinfo("Error", "In order to play the song it needs to be in  the/songs folder!")

        self.song_time()    # for elapsed time and total time in status bar

    def stop(self):
        self.slider.config(value=0)  # reset the slider

        pygame.mixer.music.stop()
        self.song_box.select_clear(ACTIVE)  # ACTIVE = the song that is clicked
        self.song_box.selection_clear(self.index)

        self.status_bar.config(text='')  # clear the status bar

        self.stopped = True

    def pause(self):
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def back(self):
        self.slider.config(value=0)

        self.index = self.song_box.curselection()[0]  # .curselection() returns a tuple and we need the first element

        self.song_box.select_clear(self.index)
        if self.index == 0:
            self.index = self.song_box.size() - 1
        else:
            self.index -= 1
        song = self.song_box.get(self.song_box.index(self.index))
        song = f'..\\MusicPlayer\\songs\\{song}'
        self.song_box.select_set(self.song_box.index(self.index))   # select the previous song in the listbox
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()

    def forward(self):
        self.slider.config(value=0)

        self.index = self.song_box.curselection()[0]    # tuple

        self.song_box.select_clear(self.index)      # OR self.song_box.selection_clear(0, END)
        if self.index == self.song_box.size() - 1:
            self.index = 0
        else:
            self.index += 1
        song = self.song_box.get(self.song_box.index(self.index))
        song = f'..\\MusicPlayer\\songs\\{song}'
        self.song_box.select_set(self.song_box.index(self.index))

        pygame.mixer.music.load(song)
        pygame.mixer.music.play()

    def repeat(self):
        self.back()
        self.forward()

    def delete_song(self):
        song = self.song_box.get(ACTIVE)
        self._controller.delete_song(song)

        self.song_box.delete(ANCHOR)  # the song that is highlighted

        self.stop()

    def delete_all_songs(self):
        for song in enumerate(self.song_box.get(0, END)):
            self._controller.delete_song(song[1])    # a tuple formed by rowid and song_name

        self.song_box.delete(0, END)
        self.stop()

    def song_time(self):
        """
        With this function we find the total time of the song, the elapsed time and we adjust the slider and the status bar
        """
        if self.stopped:   # there is no song playing
            return

        # grab current song time
        current_time = pygame.mixer.music.get_pos() / 1000  # for seconds, not milliseconds
        # converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))  # convert to a nicer format

        # get currently playing song
        song = self.song_box.get(self.song_box.index(self.index))  # SAU ACTIVE
        song = f'..\\MusicPlayer\\songs\\{song}'

        # get current song length with mutagen
        song_wav = WAVE(song)
        self.song_length = int(song_wav.info.length)

        converted_song_length = time.strftime('%M:%S', time.gmtime(self.song_length))    # convert to time format

        current_time += 1  # increase current time in order to sync the slider

        if int(self.slider.get()) == int(self.song_length):  # if the song has finished
            self.status_bar.config(text=f'Time elapsed: {converted_song_length} of {converted_song_length}   ')
            self.forward()

        elif self.paused:  # make the slider stop when the song is paused
            pass

        elif int(self.slider.get()) == int(current_time):
            # slider hasn't been moved
            # update slider to position
            slider_position = self.song_length  # make the slider and the current time be equal
            self.slider.config(to=slider_position, value=int(current_time))

        else:
            # slider has been moved
            # update slider to position
            slider_position = self.song_length
            self.slider.config(to=slider_position, value=self.slider.get())

            converted_current_time = time.strftime('%M:%S', time.gmtime(int(self.slider.get())))

            # update status bar
            self.status_bar.config(text=f'Time elapsed: {converted_current_time} of {converted_song_length}   ')

            # move this along by one second
            next_time = int(self.slider.get()) + 1
            self.slider.config(value=next_time)

        # update time
        self.status_bar.after(1000, self.song_time)   # every second this function calls itself

    def slide(self, arg):
        """
        Play the song from the second given by the slider when we drag it
        """
        song = self.song_box.get(ACTIVE)
        song = f'..\\MusicPlayer\\songs\\{song}'

        pygame.mixer.music.load(song)
        # pygame.mixer.music.play(start=self.slider.get())
        try:
            pygame.mixer.music.play(start=1.00)
        except pygame.error:
            messagebox.showinfo("Error", "Can't drag the slider on wav files!")
            self.play()

    def volume(self, arg):  # when we move the slider it puts its position in an argument, we're not using it
        pygame.mixer.music.set_volume(self.volume_slider.get())

    def mute_unmute(self):
        if not self.muted:
            self.muted = True
            # self.volume_slider.set(0)
            pygame.mixer.music.set_volume(0)
            self.mute_unmute_button.config(image=self.mute_img)
        else:
            self.muted = False
            # self.volume_slider.set()
            pygame.mixer.music.set_volume(self.volume_slider.get())
            self.mute_unmute_button.config(image=self.sound_img)

    def start(self):
        # images for buttons
        back_button_img = PhotoImage(file='../MusicPlayer/images/button_grey_rew.png')
        forward_button_img = PhotoImage(file='../MusicPlayer/images/button_grey_ffw.png')
        play_button_img = PhotoImage(file='../MusicPlayer/images/button_grey_play.png')
        pause_button_img = PhotoImage(file='../MusicPlayer/images/button_grey_pause.png')
        stop_button_img = PhotoImage(file='../MusicPlayer/images/button_grey_stop.png')
        repeat_button_img = PhotoImage(file='../MusicPlayer/images/button_grey_repeat.png')

        # buttons frame
        controls_frame = Frame(self.master_frame)
        controls_frame.grid(row=2, column=0)
        # controls_frame.pack()

        # create buttons
        back_button = Button(controls_frame, image=back_button_img, borderwidth=0, command=self.back)
        forward_button = Button(controls_frame, image=forward_button_img, borderwidth=0, command=self.forward)
        play_button = Button(controls_frame, image=play_button_img, borderwidth=0, command=self.play)
        pause_button = Button(controls_frame, image=pause_button_img, borderwidth=0, command=self.pause)
        stop_button = Button(controls_frame, image=stop_button_img, borderwidth=0, command=self.stop)
        repeat_button = Button(controls_frame, image=repeat_button_img, borderwidth=0, command=self.repeat)

        # Grid.rowconfigure(controls_frame, index=0, weight=1)
        # Grid.columnconfigure(controls_frame, index=0, weight=1)
        # Grid.columnconfigure(controls_frame, index=1, weight=1)       # for dynamically resizing
        # Grid.columnconfigure(controls_frame, index=2, weight=1)
        # Grid.columnconfigure(controls_frame, index=3, weight=1)
        # Grid.columnconfigure(controls_frame, index=4, weight=1)

        back_button.grid(row=0, column=2, sticky="nsew")
        forward_button.grid(row=0, column=4, sticky="nsew")
        play_button.grid(row=0, column=3, sticky="nsew")
        pause_button.grid(row=0, column=1, sticky="nsew")
        stop_button.grid(row=0, column=0, sticky="nsew")
        repeat_button.grid(row=0, column=5, sticky="nsew")

        my_menu = Menu(self.root)
        self.root.config(menu=my_menu)

        # add song menu
        add_song_menu = Menu(my_menu)
        my_menu.add_cascade(label="Add songs",
                            menu=add_song_menu)  # Creates a new hierarchical menu by associating a given menu to a parent menu
        add_song_menu.add_command(label="Add one song to playlist", command=self.add_song)
        add_song_menu.add_command(label="Add many songs to playlist", command=self.add_many_songs)

        # delete song menu
        delete_song_menu = Menu(my_menu)
        my_menu.add_cascade(label="Delete songs", menu=delete_song_menu)
        delete_song_menu.add_command(label="Delete highlighted song from playlist", command=self.delete_song)
        delete_song_menu.add_command(label="Delete all songs from playlist", command=self.delete_all_songs)

        # self.song_box.bind('<<ListboxSelect>>', self.play)  # if we want to associate mouse click with playing a song

        self.root.mainloop()

    def close_connection(self):
        self._controller.close_connection()
